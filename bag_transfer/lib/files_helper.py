import os
import pwd
import tarfile
import zipfile
from uuid import uuid4

import boto3
import psutil
from asterism.file_helpers import is_dir_or_file
from django.conf import settings

from ..models import Transfer


def open_files_list():
    """Return a list of files open on the linux system"""
    path_list = []

    for proc in psutil.process_iter():
        open_files = proc.open_files()
        if open_files:
            for fileObj in open_files:
                path_list.append(fileObj.path)
    return path_list


def files_in_unserialized(dirpath):
    """Returns a list of files in infinitely recursing subdirectories."""
    files = []
    dirpaths = []
    to_check = [dirpath]
    checked_dirs = []

    while True:
        if not to_check:
            break
        live_dir = to_check[0]

        for path in os.listdir(live_dir):
            fullpath = "{}/{}".format(live_dir, path)
            if os.path.isdir(fullpath):
                dirpaths.append(fullpath)

                if fullpath not in checked_dirs:
                    to_check.append(fullpath)

        checked_dirs.append(live_dir)
        if live_dir in to_check:
            to_check = [x for x in to_check if x != live_dir]

    # check all dirs -- can narrow to /data since payload requirement or not
    if dirpaths:
        for dire in dirpaths:
            d = os.listdir(dire)
            if d:
                for contents in d:
                    fullpath = "{}/{}".format(dire, contents)
                    if os.path.isfile(fullpath):
                        files.append(fullpath)
    return files


def zip_has_top_level_only(file_path):
    """Checks to see whether a ZIP file has a single top-level directory."""
    items = []
    with zipfile.ZipFile(file_path, "r") as zfile:
        items = zfile.namelist()
    top_dir = items[0].split("/")[0]
    for item in items[1:]:
        if item.split("/")[0] != top_dir:
            return False
    return top_dir


def tar_has_top_level_only(file_path):
    """Checks to see whether a TAR file has a single top-level directory."""
    items = []
    with tarfile.open(file_path, "r:*") as tfile:
        items = tfile.getnames()
        if not tfile.getmembers()[0].isdir():
            return False
    if not items:
        return False
    # items 0 should be the first of every split
    top_dir = items[0]
    for item in items:
        if item.split("/")[0] != top_dir:
            return False
    return top_dir


def all_paths_exist(list_of_paths):
    """Checks whether or not all paths in a list exist."""
    return all([is_dir_or_file(p) for p in list_of_paths])


def get_file_contents(filepath):
    """Returns the contents of a file as a string."""
    data = ""
    try:
        with open(filepath, "r") as open_file:
            data = open_file.read()
    except Exception as e:
        print(e)
    finally:
        return data


def chown_path_to_root(file_path):
    if is_dir_or_file(file_path):
        root_uid = pwd.getpwnam("root").pw_uid
        os.chown(file_path, root_uid, root_uid)


def s3_bucket_exists(bucket_name, client=None):
    """Checks to see if an S3 bucket exists."""
    s3_client = client or boto3.client(
        's3',
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION)
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except s3_client.exceptions.NoSuchBucket:
        return False


def generate_identifier():
    """returns a unique identifier"""
    iden = str(uuid4())
    if Transfer.objects.filter(machine_file_identifier=iden).exists():
        generate_identifier()
    return iden
