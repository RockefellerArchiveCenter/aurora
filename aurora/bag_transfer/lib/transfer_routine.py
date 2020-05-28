import datetime
import os
import re
import shutil
import tarfile
import zipfile
from pwd import getpwuid

import bag_transfer.lib.log_print as Pter
from asterism.file_helpers import remove_file_or_dir, get_dir_size, zip_extract_all, tar_extract_all
from bag_transfer.lib.files_helper import (all_paths_exist,
                                           files_in_unserialized, 
                                           is_dir_or_file, open_files_list,
                                           tar_has_top_level_only,
                                           zip_has_top_level_only)
from bag_transfer.lib.virus_scanner import VirusScan
from bag_transfer.models import BAGLog, Organization
from django.conf import settings
from django.utils.timezone import make_aware


class TransferRoutine(object):
    def __init__(self, RUN=False):
        self.transfers = []
        self.active_organizations = []
        self.routine_contents_dictionary = {}
        self.organizations_processing_paths = []
        self.has_setup_err = False

        if RUN:
            self.run_routine()

    def setup_routine(self):
        self.has_setup_err = False

        # pull active organizations
        if not self.has_active_organizations():
            self.has_setup_err = True
            Pter.plines(["No active organizations in database"])
            return False

        # do active orgs dirs exist (processing / upload)
        self.verify_organizations_paths()

        # are there active orgs left?
        if not self.active_organizations:
            self.has_setup_err = True
            Pter.plines(["No active organizations that are set up correctly"])
            return False

        # build contents dictionary of all files / dirs in active org uploads
        self.build_contents_dictionary()
        if not self.routine_contents_dictionary:
            Pter.plines(["No files discovered in uploads directory"])
            return False

        return True

    def run_routine(self):
        # discovery phase: searches active orgs dirs for files/dir in uploads
        if not self.setup_routine():
            Pter.plines(
                [
                    "Transfer Routine Setup didn't yield results so the routine will stop here"
                ]
            )
        else:
            # Move Files to Processing
            self._move_transfers_to_processing_dir()

        # STEP 1: get list of uploads to process by checking orgs processing dir
        self._discover_paths_in_processing_dir()
        if not self.organizations_processing_paths:
            Pter.plines(["didnt find anything in processing so ending routine"])
            return False

        # STEP 2: VALIDATION ROUTINES
        for file_path in self.organizations_processing_paths:
            transObj = TransferFileObject(file_path)

            if not transObj.is_processible():
                BAGLog.log_it("DEXT")
                continue

            if not transObj.passes_filename():
                pass
            else:
                if not transObj.passes_virus_scan():
                    pass
                else:
                    if not transObj.resolve_file_type():
                        pass
                    else:
                        if not transObj.resolve_file_size():
                            pass
                        else:
                            if not transObj.passes_filesize_max():
                                pass

            self.transfers.append(transObj.render_transfer_record())

        return self.transfers if self.transfers else False

    #####################
    # START SETUP METHODS
    #####################
    def has_active_organizations(self):
        self._setup_active_organizations()
        return True if self.active_organizations else False

    def _setup_active_organizations(self):
        self.active_organizations = Organization.objects.filter(is_active=True)

    def verify_organizations_paths(self):
        ck = 0
        orgs_to_remove = []
        for org in self.active_organizations:
            if not all_paths_exist(org.org_machine_upload_paths()):
                ck += 1
                orgs_to_remove.append(org)
            # TODO: PLACE ERR
        # remove org from Routine and log
        if ck > 0:
            self.active_organizations = [
                org for org in self.active_organizations if org not in orgs_to_remove
            ]
            Pter.plines(
                ["{} orgs were removed from routine".format(len(orgs_to_remove))]
            )

    def build_contents_dictionary(self):
        org_dir_contents = {}
        for org in self.active_organizations:
            upload_dir = org.org_machine_upload_paths()[0]
            dir_content = os.listdir(upload_dir)
            if dir_content:
                for item in dir_content:
                    item_path = "{}{}".format(upload_dir, item)
                    if org.machine_name not in org_dir_contents:
                        org_dir_contents[org.machine_name] = {
                            "files": [],
                            "dirs": [],
                            "count": 0,
                        }
                    if os.path.isfile(item_path):
                        org_dir_contents[org.machine_name]["files"].append(item_path)
                        org_dir_contents[org.machine_name]["count"] += 1
                    elif os.path.isdir(item_path):
                        org_dir_contents[org.machine_name]["dirs"].append(item_path)
                        org_dir_contents[org.machine_name]["count"] += 1

        if org_dir_contents:
            self.routine_contents_dictionary = org_dir_contents
            self._purge_routine_contents_dictionary()

    def _purge_routine_contents_dictionary(self):
        """get list of files to remove, when compared to contents dict"""
        paths_to_remove_from_active_routine = self._org_contents_in_lsof()
        if paths_to_remove_from_active_routine:
            self._dump_from_routine_contents(paths_to_remove_from_active_routine)

    def _org_contents_in_lsof(self):
        """Returns list of files to remove from current processing, based on lsof log (open files)"""
        rm_list = []
        for org, obj in self.routine_contents_dictionary.items():
            # Get open files
            open_files = open_files_list()
            if obj["count"] < 1:
                continue
            # Get files
            for f in obj["files"]:
                if f in open_files:
                    rm_list.append((org, 0, f))
            # get directory
            for d in obj["dirs"]:
                # check files in directory are on list
                for fls in files_in_unserialized(d, True):
                    if fls in open_files:
                        rm_list.append((org, 1, d))
            return rm_list

    def _dump_from_routine_contents(self, cObj):
        """Removes items from processing list"""
        for obj in cObj:
            if obj[1] == 0 and os.path.isfile(obj[2]):
                self.routine_contents_dictionary[obj[0]]["files"] = [
                    x
                    for x in self.routine_contents_dictionary[obj[0]]["files"]
                    if x != obj[2]
                ]
            elif obj[1] == 1 and os.path.isdir(obj[2]):
                self.routine_contents_dictionary[obj[0]]["dirs"] = [
                    x
                    for x in self.routine_contents_dictionary[obj[0]]["dirs"]
                    if x != obj[2]
                ]

    #####################
    # END SETUP METHODS
    #####################

    def _move_transfers_to_processing_dir(self):
        """Moves transfers prebuilt in setup to processiong dir"""
        print("Moving transfers to processing directory")
        for org, obj in self.routine_contents_dictionary.items():
            mergedlist = obj["files"] + obj["dirs"]
            for f in mergedlist:
                processing_path = f.replace("upload", "processing")
                # todo: would prefer a try/except cause these are system resource dependent
                # ck for processing file existence so we can cleanly rm then mv instead of mv to overwrite (notice colisions on dirs that already existed)
                if is_dir_or_file(processing_path):
                    remove_file_or_dir(processing_path)
                shutil.move(f, processing_path)

    def _discover_paths_in_processing_dir(self):
        for org in self.active_organizations:
            org_processing_path = org.org_machine_upload_paths()[1]
            org_paths = [
                "{}{}".format(org_processing_path, x)
                for x in os.listdir(org_processing_path)
            ]
            self.organizations_processing_paths = (
                self.organizations_processing_paths + org_paths
            )

    ####################
    # START VALIDATION METHODS
    ####################


class TransferFileObject(object):
    FILE_TYPE_OTHER = "OTHER"
    FILE_TYPE_ZIP = "ZIP"
    FILE_TYPE_TAR = "TAR"
    AUTO_FAIL_DEXT = "DEXT"
    AUTO_FAIL_BFNM = "BFNM"
    AUTO_FAIL_VIRUS = "VIRUS"
    AUTO_FAIL_BDIR = "BDIR"
    AUTO_FAIL_BTAR = "BTAR"
    AUTO_FAIL_BTAR2 = "BTAR2"
    AUTO_FAIL_ZIP = "BZIP"
    AUTO_FAIL_ZIP2 = "BZIP2"
    AUTO_FAIL_FSERR = "FSERR"
    ACCEPTABLE_FILE_EXT = {FILE_TYPE_TAR: [".gz", ".tar"], FILE_TYPE_ZIP: [".zip"]}
    PATH_TYPE_DIR = "isdir"
    PATH_TYPE_FILE = "isfile"

    def __init__(self, file_path):
        self._is_processible = False
        self.extract_dir = settings.TRANSFER_EXTRACT_TMP
        self.transfer_filesize_max = settings.TRANSFER_FILESIZE_MAX * 1000
        self.file_path = file_path
        self.auto_fail = False
        self.auto_fail_code = ""
        self.bag_it_name = ""
        self.file_type = self.FILE_TYPE_OTHER
        self.file_size = 0
        self.file_path_ext = ""
        self.path_type = self.PATH_TYPE_FILE
        self.org_machine_name = ""
        self.virus_scanner = {}

        if (
            self.path_still_exist() and self._resolve_org_machine_name() and self._resolve_virus_scan_connection()
        ):
            self._generate_file_info()
            self._is_processible = True

    def is_processible(self):
        """True when class init has passed all"""
        return self._is_processible

    def path_still_exist(self):
        """Secondary check in routine that path still exist"""
        if not is_dir_or_file(self.file_path):
            return self.set_auto_fail_with_code(self.AUTO_FAIL_DEXT)
        return True

    def _resolve_org_machine_name(self):
        org_in_path = self.file_path.split(os.sep)[-3]
        if not org_in_path:
            return False
        self.org_machine_name = org_in_path
        return True

    def _resolve_virus_scan_connection(self):
        self.virus_scanner = VirusScan()
        if not self.virus_scanner.is_ready():
            BAGLog.log_it("VCONN")
            return False
        return True

    def resolve_file_type(self):
        """sets file_type based on ext and then file_type validation"""

        # if dir then we are all set here
        if os.path.isdir(self.file_path):
            self.file_type = self.FILE_TYPE_OTHER
            self.path_type = self.PATH_TYPE_DIR
            self.bag_it_name = self.file_path.split("/")[-1]
        else:
            # get extension
            self.file_path_ext = os.path.splitext(self.file_path)[-1]
            # check extension vs Acceptable list
            if not any(
                self.file_path_ext in sl
                for sl in list(self.ACCEPTABLE_FILE_EXT.values())
            ):
                self.set_auto_fail_with_code(
                    self.AUTO_FAIL_BDIR
                )  # ACTUALLY NOT Acurate
            else:
                passed = False
                if self.file_path_ext in self.ACCEPTABLE_FILE_EXT[self.FILE_TYPE_TAR]:
                    self.file_type = self.FILE_TYPE_TAR
                    try:
                        if tarfile.is_tarfile(self.file_path):
                            passed = True
                    except Exception as e:
                        print("Error validating tar file: {}".format(e))
                    if not passed:
                        self.set_auto_fail_with_code(self.AUTO_FAIL_BTAR)
                    else:
                        # check for top level dir
                        self.bag_it_name = tar_has_top_level_only(self.file_path)
                        if not self.bag_it_name:
                            self.set_auto_fail_with_code(self.AUTO_FAIL_BTAR2)

                elif self.file_path_ext in self.ACCEPTABLE_FILE_EXT[self.FILE_TYPE_ZIP]:
                    self.file_type = self.FILE_TYPE_ZIP

                    if not zipfile.is_zipfile(self.file_path):
                        self.set_auto_fail_with_code(self.AUTO_FAIL_ZIP)
                    else:
                        self.bag_it_name = zip_has_top_level_only(self.file_path)
                        if not self.bag_it_name:
                            self.set_auto_fail_with_code(self.AUTO_FAIL_ZIP2)

        return False if self.auto_fail else True

    def resolve_file_size(self):

        # todo: figure out how to return this function false, file size errs
        file_size = 0

        if self.path_type == self.PATH_TYPE_DIR:
            file_size = get_dir_size(self.file_path)
        elif self.path_type == self.PATH_TYPE_FILE:

            # path that will exist once it's created in tmp
            tmp_dir_path = "{}{}".format(self.extract_dir, self.bag_it_name)

            # extract tar to tmp
            if self.file_type == self.FILE_TYPE_TAR:
                if tar_extract_all(self.file_path, self.extract_dir):
                    file_size = get_dir_size(tmp_dir_path)
                    remove_file_or_dir(tmp_dir_path)
            elif self.file_type == self.FILE_TYPE_ZIP:
                if zip_extract_all(self.file_path, self.extract_dir):
                    file_size = get_dir_size(tmp_dir_path)
                    remove_file_or_dir(tmp_dir_path)

        if not file_size or (isinstance(file_size, tuple) and not file_size[0]):
            self.file_size = 0
            return self.set_auto_fail_with_code(self.AUTO_FAIL_FSERR)

        self.file_size = file_size  # can it be tuple though?
        return True

    def _generate_file_info(self):
        self.file_owner = self._get_file_owner()
        self.file_modtime = self._get_file_modified_time()
        self.file_date = self.file_modtime.date()
        self.file_time = self.file_modtime.time()

    def _get_file_owner(self):
        return getpwuid(os.stat(self.file_path).st_uid).pw_name

    def _get_file_modified_time(self):
        return make_aware(
            datetime.datetime.fromtimestamp(os.path.getmtime(self.file_path))
        )

    def passes_filename(self):
        is_valid = re.match(
            r"^[a-zA-Z0-9\-\_\/\.\s]+$", self.file_path.split("/")[-1]
        )
        if not is_valid:
            return self.set_auto_fail_with_code(self.AUTO_FAIL_BFNM)
        return True

    def passes_virus_scan(self):

        # secondary ping, but right before scan
        if not self.virus_scanner.is_ready():
            # need actionable to drop from active processing
            return False
        try:
            self.virus_scanner.scan(self.file_path)
        except Exception as e:
            print("Error scanning for viruses".format(e))
            # again need actionable to reloop
            return False
        if not self.virus_scanner.scan_result:
            return True
        # quarantine or move
        remove_file_or_dir(self.file_path)

        return self.set_auto_fail_with_code(self.AUTO_FAIL_VIRUS)

    def passes_filesize_max(self):
        if self.file_size > self.transfer_filesize_max:
            return self.set_auto_fail_with_code(self.AUTO_FAIL_FSERR)
        return True

    def set_auto_fail_with_code(self, code):
        self.auto_fail = True
        self.auto_fail_code = code
        return False

    def render_transfer_record(self):
        """Called after processing fails validation or succeeds, generates dictionary for next step"""
        return {
            "date": self.file_date,
            "time": self.file_time,
            "file_path": self.file_path,
            "file_name": self.file_path.split("/")[-1],
            "file_type": self.file_type,
            "org": self.org_machine_name,
            "file_modtime": self.file_modtime,
            "file_size": self.file_size,
            "upload_user": self.file_owner,
            "auto_fail": self.auto_fail,
            "auto_fail_code": self.auto_fail_code,
            "bag_it_name": self.bag_it_name,
            "virus_scanresult": self.virus_scanner.scan_result,
        }
