import datetime
import os
import pwd
import re
import tarfile
import zipfile
from shutil import copytree, move, rmtree

import bagit
import psutil


def open_files_list():
    """Return a list of files open on the linux system"""
    path_list = []

    for proc in psutil.process_iter():
        open_files = proc.open_files()
        if open_files:
            for fileObj in open_files:
                path_list.append(fileObj.path)
    return path_list


def files_in_unserialized(dirpath, CK_SUBDIRS=False):
    files = []

    if CK_SUBDIRS:
        dirpaths = []
        to_check = [dirpath]
        checked_dirs = []

        # build list from all files in Infinite sub dirs
        while True:

            # resolve new dir to check
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

    else:
        for f1 in os.listdir(dirpath):
            if os.path.isfile(f1):
                files.append(f1)

    return files


def get_dir_size(start_path):
    """returns size of contents of dir https://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
        for d in dirnames:
            dp = os.path.join(dirpath, d)
            total_size += os.path.getsize(dp)
    return total_size if total_size else False


def zip_has_top_level_only(file_path):
    items = []
    with zipfile.ZipFile(file_path, "r") as zfile:

        items = zfile.namelist()

    top_dir = items[0].split("/")[0]

    for item in items[1:]:
        if item.split("/")[0] != top_dir:
            return False

    return top_dir


def tar_has_top_level_only(file_path):
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


def anon_extract_all(file_path, tmp_dir):
    """determine which path type, return extraction results"""
    # is it a dir
    if os.path.isdir(file_path):
        return dir_extract_all(file_path, tmp_dir)
    else:
        # is it a tar
        if file_path.endswith("tar.gz") or file_path.endswith(".tar"):
            return tar_extract_all(file_path, tmp_dir)

        # is it a zip
        if file_path.endswith(".zip"):
            return zip_extract_all(file_path, tmp_dir)

    return False


def zip_extract_all(file_path, tmp_dir):
    extracted = False
    try:
        zf = zipfile.ZipFile(file_path, "r")
        zf.extractall(tmp_dir)
        zf.close()
        extracted = True
    except Exception as e:
        print(e)
    return extracted


def tar_extract_all(file_path, tmp_dir):
    extracted = False
    try:
        tf = tarfile.open(file_path, "r:*")
        tf.extractall(tmp_dir)
        tf.close()
        extracted = True
    except Exception as e:
        print(e)

    return extracted


def dir_extract_all(file_path, tmp_dir):
    extracted = False
    try:
        # notice forward slash missing
        if is_dir_or_file("{}{}".format(tmp_dir, file_path.split("/")[-1])):
            rmtree("{}{}".format(tmp_dir, file_path.split("/")[-1]))
        copytree(file_path, "{}{}".format(tmp_dir, file_path.split("/")[-1]))
        extracted = True
    except Exception as e:
        print(e)
    return extracted


def get_fields_from_file(file_path):
    fields = {}
    try:
        patterns = [r"(?P<key>[\w\-]+)", "(?P<val>.+)"]
        with open(file_path, "r") as f:
            for line in f.readlines():
                line = line.strip("\n")

                row_search = re.search(r":?(\s)?".join(patterns), line)
                if row_search:
                    key = row_search.group("key").replace("-", "_").strip()
                    val = row_search.group("val").strip()
                    if key in fields:
                        listval = [fields[key]]
                        listval.append(val)
                        fields[key] = listval
                    else:
                        fields[key] = val
    except Exception as e:
        print(e)

    return fields


def remove_file_or_dir(file_path):
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(e)
            return False
    elif os.path.isdir(file_path):
        try:
            rmtree(file_path)
        except Exception as e:
            print(e)
            return False
    return True


def move_file_or_dir(src, dest):
    try:
        move(src, dest)
    except Exception as e:
        print(e)
        return False


def is_dir_or_file(file_path):
    if os.path.isdir(file_path):
        return True
    if os.path.isfile(file_path):
        return True
    return False


def all_paths_exist(list_of_paths):
    for p in list_of_paths:
        if not is_dir_or_file(p):
            return False
    return True


def get_file_contents(f):
    """returns contents of file as str"""

    data = ""
    try:
        with open(f, "r") as open_file:
            data = open_file.read()
    except Exception as e:
        print(e)
    finally:
        return data


def chown_path_to_root(file_path):
    if is_dir_or_file(file_path):
        root_uid = pwd.getpwnam("root").pw_uid
        os.chown(file_path, root_uid, root_uid)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def update_bag_info(bag_path, data):
    """Adds metadata to `bag-info.txt`"""
    bag = bagit.Bag(bag_path)
    for k, v in data.items():
        bag.info[k] = v
    bag.save()
