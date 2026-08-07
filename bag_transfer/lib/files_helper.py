import os
import pwd
import tarfile
import zipfile
from os import makedirs, pardir, remove, walk
from os.path import abspath, basename, getsize, isdir, isfile, join
from shutil import copy, copytree, move, rmtree
from uuid import uuid4

import boto3
from django.conf import settings

from ..models import Transfer


def copy_file_or_dir(src, dest):
    copied = False
    if isdir(src):
        copytree(src, dest)
        copied = True
    elif isfile(src):
        if not isdir(abspath(join(dest, pardir))):
            makedirs(abspath(join(dest, pardir)))
        copy(src, dest)
        copied = True
    return copied


def get_dir_size(start_path):
    """Returns the total size of a directory.

    See https://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
    """
    total_size = 0
    for dirpath, dirnames, filenames in walk(start_path):
        for f in filenames:
            fp = join(dirpath, f)
            total_size += getsize(fp)
        for d in dirnames:
            dp = join(dirpath, d)
            total_size += getsize(dp)
    return total_size if total_size else False


def is_dir_or_file(file_path):
    result = False
    if isdir(file_path):
        result = True
    if isfile(file_path):
        result = True
    return result


def tar_extract_all(file_path, tmp_dir):
    """Extracts the contents of a TAR file."""
    extracted = False
    try:
        tf = tarfile.open(file_path, "r:*")
        tf.extractall(tmp_dir)
        tf.close()
        extracted = tmp_dir
    except Exception as e:
        print("Error extracting TAR file: {}".format(e))
    return extracted


def make_tarfile(src, dest, compressed=True, compresslevel=1, remove_src=False):
    """Creates a TAR file.

    Args:
        src (str): directory to serialize.
        dest(str): file path for TAR file to be created.
        compressed (bool): whether the TAR file should be compressed.
        compresslevel (int): from 0 to 9 controlling the level of compression
        remove_src (bool): whether the src should be deleted after serialization.
    """
    if not isdir(abspath(join(dest, pardir))):
        makedirs(abspath(join(dest, pardir)))
    if compressed:
        with tarfile.open(dest, "w:gz", compresslevel=compresslevel) as tar:
            tar.add(src, arcname=basename(src))
    else:
        with tarfile.open(dest, "w") as tar:
            tar.add(src, arcname=basename(src))
    if remove_src:
        rmtree(src)
    return dest


def move_file_or_dir(src, dest):
    try:
        if not isdir(abspath(join(dest, pardir))):
            makedirs(abspath(join(dest, pardir)))
        move(src, dest)
        return True
    except Exception as e:
        print(e)
        return False


def remove_file_or_dir(file_path):
    removed = False
    if isfile(file_path):
        try:
            remove(file_path)
            removed = True
        except Exception as e:
            print(e)
    elif isdir(file_path):
        try:
            rmtree(file_path)
            removed = True
        except Exception as e:
            print(e)
    return removed


def zip_extract_all(file_path, tmp_dir):
    """Extracts the contents of a ZIP file."""
    extracted = False
    try:
        zf = zipfile.ZipFile(file_path, "r")
        zf.extractall(tmp_dir)
        zf.close()
        extracted = tmp_dir
    except Exception as e:
        print("Error extracting ZIP file: {}".format(e))
    return extracted


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
