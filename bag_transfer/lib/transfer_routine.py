import datetime
import os
import re
import shutil
import tarfile
import zipfile

import boto3
from asterism.file_helpers import (get_dir_size, is_dir_or_file,
                                   move_file_or_dir, remove_file_or_dir,
                                   tar_extract_all, zip_extract_all)
from django.conf import settings
from django.utils.timezone import make_aware

import bag_transfer.lib.log_print as Pter
from bag_transfer.lib.files_helper import (all_paths_exist,
                                           files_in_unserialized,
                                           generate_identifier,
                                           open_files_list, s3_bucket_exists,
                                           tar_has_top_level_only,
                                           zip_has_top_level_only)
from bag_transfer.lib.virus_scanner import VirusScan
from bag_transfer.models import Organization


class TransferRoutineException(Exception):
    def __init__(self, code):
        self.code = code


class TransferRoutine(object):
    def __init__(self):
        self.tmp_dir = settings.TRANSFER_EXTRACT_TMP
        self.active_organizations = None
        self.routine_contents_dictionary = None
        self.has_setup_err = False

    def setup_routine(self):
        """Sets up the transfer routine.

        Ensures there is at least one active organization with the expected
        directories, and builds a dictionary of transfers to process.
        """
        active_organizations = Organization.objects.filter(is_active=True)
        if not len(active_organizations):
            self.has_setup_err = True
            Pter.plines(["No active organizations in database"])
            return False

        self.active_organizations = self.verify_organizations_paths(active_organizations)
        if not self.active_organizations:
            self.has_setup_err = True
            Pter.plines(["No active organizations that are set up correctly"])
            return False

        self.routine_contents_dictionary = self.build_contents_dictionary()
        if not self.has_processible_files():
            self.has_setup_err = False
            Pter.plines(["No files discovered in uploads directory"])
            return False

        return True

    def run_routine(self):
        """Runs the transfer routine."""
        transfers = []

        self.setup_routine()
        for org, org_transfers in self.routine_contents_dictionary.items():
            to_process = org_transfers["files"] + org_transfers["dirs"]
            for transfer_path in to_process:
                processing_path = self.move_transfer_to_tmp_dir(transfer_path, org)
                transfer = TransferFileObject(processing_path, org)
                identifier = generate_identifier()
                try:
                    transfer.is_processible()
                    transfer.passes_filename()
                    transfer.passes_virus_scan()
                    transfer.file_modtime = transfer.get_file_modified_time()
                    transfer.file_type, transfer.bag_it_name = transfer.resolve_file_type()
                    transfer.file_size, expanded_path = transfer.resolve_file_size()
                    transfer.passes_filesize_max()
                    move_file_or_dir(expanded_path, os.path.join(self.tmp_dir, identifier))
                    transfer.file_path = os.path.join(self.tmp_dir, identifier)
                    transfer.machine_file_identifier = identifier
                except TransferRoutineException as err:
                    transfer.auto_fail = True
                    transfer.auto_fail_code = err.code
                remove_file_or_dir(processing_path)
                transfers.append(transfer.render_transfer_record())
        return transfers

    def verify_organizations_paths(self, active_orgs):
        """Makes sure organizations have upload and processing paths."""
        for org in active_orgs:
            if settings.S3_USE:
                if not s3_bucket_exists(org.upload_target):
                    active_orgs = active_orgs.exclude(name=org.name)
            else:
                if not all_paths_exist([org.upload_target]):
                    active_orgs = active_orgs.exclude(name=org.name)
        return active_orgs

    def build_contents_dictionary(self):
        """Creates a dictionary of transfers to process."""
        org_dir_contents = {}
        for org in self.active_organizations:
            if org.machine_name not in org_dir_contents:
                org_dir_contents[org.machine_name] = {
                    "files": [],
                    "dirs": [],
                    "count": 0}
            upload_path = org.upload_target
            if settings.S3_USE:
                # TODO: will need futzing for dirs
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION)
                paginator = s3_client.get_paginator('list_objects_v2')
                results = paginator.paginate(Bucket=upload_path)
                for page in results:
                    org_dir_contents[org.machine_name]["files"] += [item["Key"] for item in page.get("Contents", [])]
                    org_dir_contents[org.machine_name]["count"] += page["KeyCount"]
            else:
                dir_contents = os.listdir(upload_path)
                org_dir_contents[org.machine_name]["count"] = len(dir_contents)
                for item in dir_contents:
                    item_path = os.path.join(upload_path, item)
                    if os.path.isfile(item_path):
                        org_dir_contents[org.machine_name]["files"].append(item_path)
                    elif os.path.isdir(item_path):
                        org_dir_contents[org.machine_name]["dirs"].append(item_path)
                if org_dir_contents:
                    org_dir_contents = self._purge_routine_contents_dictionary(org_dir_contents)
        return org_dir_contents

    def has_processible_files(self):
        """Returns a boolean indicating if any files are waiting for processing."""
        return bool(sum([self.routine_contents_dictionary[org]["count"] for org in self.routine_contents_dictionary]))

    def _purge_routine_contents_dictionary(self, org_dir_contents):
        """Removes transfers from the routine if they are still in the process of being transferred."""
        paths_to_remove_from_active_routine = self._org_contents_in_lsof(org_dir_contents)
        if paths_to_remove_from_active_routine:
            return self._dump_from_routine_contents(paths_to_remove_from_active_routine)
        return org_dir_contents

    def _org_contents_in_lsof(self, org_dir_contents):
        """Returns list of files to remove from current processing, based on lsof log (open files)"""
        rm_list = []
        for org, obj in org_dir_contents.items():
            open_files = open_files_list()
            if obj["count"] < 1:
                continue
            for f in obj["files"]:
                if f in open_files:
                    rm_list.append((org, 0, f))
            for d in obj["dirs"]:
                for fls in files_in_unserialized(d):
                    if fls in open_files:
                        rm_list.append((org, 1, d))
        return rm_list

    def _dump_from_routine_contents(self, active_paths, org_dir_contents):
        """Removes items from processing list"""
        for org, isdir, fpath in active_paths:
            if isdir == 0 and os.path.isfile(fpath):
                org_dir_contents[org]["files"] = [
                    x
                    for x in org_dir_contents[org]["files"]
                    if x != fpath]
            elif isdir == 1 and os.path.isdir(fpath):
                org_dir_contents[org]["dirs"] = [
                    x
                    for x in org_dir_contents[org]["dirs"]
                    if x != fpath]
        return org_dir_contents

    def move_transfer_to_tmp_dir(self, file_path, org):
        """Moves transfer from upload target to processing directory."""
        upload_path = Organization.objects.get(machine_name=org).upload_target
        if settings.S3_USE:
            # TODO: this is going to need some futzing for dirs
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION)
            if os.path.dirname(file_path):
                target_dir = os.path.join(self.tmp_dir, os.path.dirname(file_path))
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
            s3_client.download_file(
                upload_path,
                file_path,
                os.path.join(self.tmp_dir, file_path))
            s3_client.delete_object(
                Bucket=upload_path,
                Key=file_path)
        else:
            shutil.move(file_path, self.tmp_dir)
        return os.path.join(self.tmp_dir, os.path.basename(file_path))


class TransferFileObject(object):
    FILE_TYPE_OTHER = "OTHER"
    FILE_TYPE_ZIP = "ZIP"
    FILE_TYPE_TAR = "TAR"
    AUTO_FAIL_DEXT = "DEXT"
    AUTO_FAIL_BFNM = "BFNM"
    AUTO_FAIL_VIRUS = "VIRUS"
    AUTO_FAIL_VCONN = "VCONN"
    AUTO_FAIL_BDIR = "BDIR"
    AUTO_FAIL_BTAR = "BTAR"
    AUTO_FAIL_BTAR2 = "BTAR2"
    AUTO_FAIL_ZIP = "BZIP"
    AUTO_FAIL_ZIP2 = "BZIP2"
    AUTO_FAIL_FSERR = "FSERR"
    ACCEPTABLE_FILE_EXT = {FILE_TYPE_TAR: [".gz", ".tar"], FILE_TYPE_ZIP: [".zip"]}
    PATH_TYPE_DIR = "isdir"
    PATH_TYPE_FILE = "isfile"

    def __init__(self, file_path, org):
        self.extract_dir = settings.TRANSFER_EXTRACT_TMP
        self.transfer_filesize_max = settings.TRANSFER_FILESIZE_MAX * 1000
        self.file_path = file_path
        self.auto_fail = False
        self.auto_fail_code = ""
        self.bag_it_name = ""
        self.file_type = self.FILE_TYPE_OTHER
        self.file_size = 0
        self.file_modtime = None
        self.file_path_ext = ""
        self.machine_file_identifier = ""
        self.path_type = self.PATH_TYPE_FILE if os.path.isfile(file_path) else self.PATH_TYPE_DIR
        self.org_machine_name = org
        self.virus_scanner = {"scan_result": None}

    def is_processible(self):
        """Transfer is available to be processed."""
        return (self.path_still_exists() and self._resolve_virus_scan_connection())

    def path_still_exists(self):
        """Secondary check in routine that path still exist"""
        if not is_dir_or_file(self.file_path):
            raise TransferRoutineException(self.AUTO_FAIL_DEXT)
        return True

    def _resolve_virus_scan_connection(self):
        self.virus_scanner = VirusScan()
        if not self.virus_scanner.is_ready():
            raise TransferRoutineException(self.AUTO_FAIL_VCONN)
        return True

    def resolve_file_type(self):
        """Sets file_type based on extension and then file type validation"""

        if os.path.isdir(self.file_path):
            file_type = self.FILE_TYPE_OTHER
            bag_it_name = self.file_path.split("/")[-1]
        else:
            file_path_ext = os.path.splitext(self.file_path)[-1]
            if not any(file_path_ext in sl for sl in list(self.ACCEPTABLE_FILE_EXT.values())):
                raise TransferRoutineException(self.AUTO_FAIL_BDIR)
            else:
                passed = False
                if file_path_ext in self.ACCEPTABLE_FILE_EXT[self.FILE_TYPE_TAR]:
                    file_type = self.FILE_TYPE_TAR
                    try:
                        if tarfile.is_tarfile(self.file_path):
                            passed = True
                    except Exception as e:
                        raise Exception(f"Error validating tar file: {e}")
                    if not passed:
                        raise TransferRoutineException(self.AUTO_FAIL_BTAR)
                    else:
                        bag_it_name = tar_has_top_level_only(self.file_path)
                        if not bag_it_name:
                            raise TransferRoutineException(self.AUTO_FAIL_BTAR2)

                elif file_path_ext in self.ACCEPTABLE_FILE_EXT[self.FILE_TYPE_ZIP]:
                    file_type = self.FILE_TYPE_ZIP

                    if not zipfile.is_zipfile(self.file_path):
                        raise TransferRoutineException(self.AUTO_FAIL_ZIP)
                    else:
                        bag_it_name = zip_has_top_level_only(self.file_path)
                        if not bag_it_name:
                            raise TransferRoutineException(self.AUTO_FAIL_ZIP2)
        return file_type, bag_it_name

    def resolve_file_size(self):
        """Sets file size for a transfer."""
        file_size = 0
        if self.path_type == self.PATH_TYPE_DIR:
            file_size = get_dir_size(self.file_path)
        elif self.path_type == self.PATH_TYPE_FILE:
            tmp_dir_path = os.path.join(self.extract_dir, self.bag_it_name)
            if self.file_type == self.FILE_TYPE_TAR:
                if tar_extract_all(self.file_path, self.extract_dir):
                    file_size = get_dir_size(tmp_dir_path)
            elif self.file_type == self.FILE_TYPE_ZIP:
                if zip_extract_all(self.file_path, self.extract_dir):
                    file_size = get_dir_size(tmp_dir_path)
        if not file_size or (isinstance(file_size, tuple) and not file_size[0]):
            file_size = 0
            raise TransferRoutineException(self.AUTO_FAIL_FSERR)
        return file_size, os.path.join(self.extract_dir, self.bag_it_name)

    def get_file_modified_time(self):
        return make_aware(
            datetime.datetime.fromtimestamp(os.path.getmtime(self.file_path)))

    def passes_filename(self):
        is_invalid = re.search(
            r"[<>\:\"\!\|\?\*]", self.file_path.split("/")[-1])
        if is_invalid:
            raise TransferRoutineException(self.AUTO_FAIL_BFNM)
        return True

    def passes_virus_scan(self):
        """Checks transfer for viruses."""
        try:
            self.virus_scanner.scan(self.file_path)
        except Exception as e:
            raise Exception(f"Error scanning for viruses: {e}")
        if self.virus_scanner.scan_result:
            remove_file_or_dir(self.file_path)
            raise TransferRoutineException(self.AUTO_FAIL_VIRUS)

    def passes_filesize_max(self):
        """Checks transfer to see if it's larger than the allowed maximum."""
        if self.file_size > self.transfer_filesize_max:
            raise TransferRoutineException(self.AUTO_FAIL_FSERR)

    def render_transfer_record(self):
        """Called after processing fails validation or succeeds, generates dictionary for next step"""
        return {
            "bag_it_name": self.bag_it_name,
            "machine_file_path": self.file_path,
            "machine_file_size": self.file_size,
            "machine_file_type": self.file_type,
            "machine_file_upload_time": self.file_modtime,
            "machine_file_identifier": self.machine_file_identifier,
            "org": self.org_machine_name,
            "auto_fail": self.auto_fail,
            "auto_fail_code": self.auto_fail_code,
            "virus_scanresult": self.virus_scanner.scan_result,
        }
