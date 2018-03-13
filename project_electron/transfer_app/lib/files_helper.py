import os
from os import stat, remove, listdir, walk
from os.path import isdir, getmtime, getsize, splitext, isfile
from pwd import getpwuid
import re
import datetime
import tarfile
import zipfile
from distutils.dir_util import copy_tree
from shutil import rmtree, move
import psutil

from transfer_app.lib.virus_scanner import VirusScan

from django.conf import settings
from orgs.models import BAGLog, Organization

import transfer_app.lib.log_print as Pter


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

            #resolve new dir to check
            if not to_check:
                break
            live_dir = to_check[0]

            for path in listdir(live_dir):
                fullpath = "{}/{}".format(live_dir,path)
                if isdir(fullpath):
                    dirpaths.append(fullpath)

                    if fullpath not in checked_dirs:
                        to_check.append(fullpath)

            checked_dirs.append(live_dir)
            if live_dir in to_check:
                to_check = [x for x in to_check if x != live_dir]

        # check all dirs -- can narrow to /data since payload requirement or not
        if dirpaths:
            for dire in dirpaths:

                d = listdir(dire)
                if d:
                    for contents in d:
                        fullpath = "{}/{}".format(dire,contents)
                        if isfile(fullpath):
                            files.append(fullpath)

            #print to console
            if files:
                print "\n\nCURRENT FILES STILL OPEN"
                for f in files:
                    print f
                print '\n'

    else:
        for f1 in listdir(dirpath):
            if isfile(f1):
                files.append(f1)

    return files

def file_owner(file_path):
    return getpwuid(stat(file_path).st_uid).pw_name

def file_modified_time(file_path):
    return datetime.datetime.fromtimestamp(getmtime(file_path))

def get_dir_size(start_path):
    """returns size of contents of dir https://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python"""
    total_size = 0
    for dirpath, dirnames, filenames in walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += getsize(fp)
        for d in dirnames:
            dp = os.path.join(dirpath,d)
            total_size += getsize(dp)
    return ((total_size / 1000) if total_size else False)

def splitext_(path):
    # https://stackoverflow.com/questions/37896386/how-to-get-file-extension-correctly
    if len(path.split('.')) > 2:
        return path.split('.')[0],'.'.join(path.split('.')[-2:])
    return splitext(path)

def zip_has_top_level_only(file_path):
    items = []
    with zipfile.ZipFile(file_path, 'r') as zfile:

        items = zfile.namelist()

    top_dir = items[0].split('/')[0]

    for item in items[1:]:
        if item.split('/')[0] != top_dir:
            return False

    return top_dir

def tar_has_top_level_only(file_path):
    items = []
    with tarfile.open(file_path,'r:*') as tfile:
        items = tfile.getnames()
        if not tfile.getmembers()[0].isdir():
            return False
    if not items:
        return False
    # items 0 should be the first of every split
    top_dir = items[0]
    for item in items:
        if item.split('/')[0] != top_dir:
            return False
    return top_dir

def zip_extract_all(file_path, tmp_dir):
    extracted = False
    try:
        zf = zipfile.ZipFile(file_path,'r')
        zf.extractall(tmp_dir)
        zf.close()
        extracted = True
    except Exception as e:
        print e
    return extracted

def tar_extract_all(file_path, tmp_dir):
    extracted = False
    try:
        tf = tarfile.open(file_path, 'r:*')
        tf.extractall(tmp_dir)
        tf.close()
        extracted = True
    except Exception as e:
        print e

    return extracted

def dir_extract_all(file_path,tmp_dir):
    extracted = False
    try:
        # notice forward slash missing
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        copy_tree(file_path,'{}{}'.format(tmp_dir, file_path.split('/')[-1]), update=1)
        extracted = True
    except Exception as e:
        print e
    return extracted

def get_fields_from_file(fpath):
    fields = {}
    try:
        patterns = [
            '(?P<key>[\w\-]+)',
            '(?P<val>.+)'
        ]
        with open(fpath,'rb') as f:
            for line in f.readlines():
                line = line.strip('\n')

                row_search = re.search(":?(\s)?".join(patterns), line)
                if row_search:
                    key = row_search.group('key').replace('-','_').strip()
                    val = row_search.group('val').strip()
                    if key in fields:
                        listval = [fields[key]]
                        listval.append(val)
                        fields[key] = listval
                    else:
                        fields[key] = val
    except Exception as e:
        print e

    return fields

def remove_file_or_dir(path):
    print '@@@-- deleting file/dir ------ {}'.format(path)
    if isfile(path):
        try:
            remove(path)
        except Exception as e:
            print e
            return False

    elif isdir(path):

        try:
            rmtree(path)
        except Exception as e:
            print e
            return False
    return True

def is_dir_or_file(path):
    if isdir(path): return True
    if isfile(path): return True
    return False

def all_paths_exist(list_of_paths):
    for p in list_of_paths:
        if not is_dir_or_file(p):
            return False
    return True

def get_file_contents(f):
    """returns contents of file as str"""

    data = ''
    try:
        with open(f,'r') as open_file:
            data = open_file.read()
    except Exception as e:
        print e
    finally:
        return data
