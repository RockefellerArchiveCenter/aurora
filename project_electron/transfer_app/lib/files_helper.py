from os import stat, remove
from os.path import isdir, getmtime, getsize, splitext, isfile
from pwd import getpwuid
import re
import datetime
import tarfile
import zipfile
from distutils.dir_util import copy_tree
from shutil import rmtree


from django.conf import settings
from orgs.models import BAGLog


def has_files_to_process():
    files_to_process = []

    with open(settings.UPLOAD_LOG_FILE) as f:
        lines_with_data = []
        for line in f.readlines():

            # Fail somewhere below and will not do processing
            auto_fail = False
            auto_fail_code = ''
            bag_it_name = ''
            file_type = 'OTHER'

            patterns = [
                'New file: (?P<file_path>.+)'
            ]

            get_uploads = re.search('.+'.join(patterns), line);
            if get_uploads:
                file_path = str(get_uploads.group('file_path'))

                # DOES FILE STILL EXIST?
                if len(file_path) <=2 or not is_dir_or_file(file_path):
                    BAGLog.log_it('DEXT')
                    continue

                print "staring file: {}".format(file_path)


                # CHECK FNAME BASED ON SPEC
                if not is_filename_valid(file_path):
                    auto_fail = True
                    auto_fail_code = 'BFNM'
                else:
                    extension = splitext_(file_path)
                    tar_accepted_ext = ['tar.gz', '.tar']

                    if extension[-1] in tar_accepted_ext:
                        file_type = 'TAR'
                        tar_passed = False
                        try:
                            if tarfile.is_tarfile(file_path):
                                tar_passed = True
                        except Exception as e:
                            print e

                        if not tar_passed:
                            auto_fail = True
                            auto_fail_code = 'BTAR'
                        else:
                            bag_it_name = tar_has_top_level_only(file_path)
                            if not bag_it_name:
                                auto_fail = True
                                auto_fail_code = 'BTAR2'
                                # print 'tar has more than one top level'
                        

                    elif extension[-1] == '.zip':
                        file_type = 'ZIP'
                        if not zipfile.is_zipfile(file_path):
                            print 'zip failed due to not being a zipfile'
                            auto_fail = True
                            auto_fail_code = 'BZIP'
                        else:
                            bag_it_name = zip_has_top_level_only(file_path)
                            if not bag_it_name:
                                auto_fail = True
                                auto_fail_code = 'BZIP2'
                                # print 'zip has more than one top level'

                    else:
                        # IS UNSERIALIZED DIR
                        if not isdir(file_path):
                            # print 'we have problems isnt dir'
                            auto_fail = True
                            auto_fail_code = 'BDIR'
                        

                        # handle dir ending in splash
                        bag_it_name = file_path.split('/')[-1]

                file_modtime =  file_modified_time(file_path)
                file_size =     file_get_size(file_path)
                file_own =      file_owner(file_path)
                file_date =     file_modtime.date()
                file_time =     file_modtime.time()



                # GETTING ORGANIZATION
                get_org = re.search('\/(?P<organization>org\d+)\/',file_path)
                if not get_org:
                    BAGLog.log_it('NORG')
                    continue

                data = {
                    'date':                 file_date,
                    'time':                 file_time,
                    'file_path':            file_path,
                    'file_name':            file_path.split('/')[-1],
                    'file_type' :           file_type,
                    'org':                  get_org.group('organization'),
                    'file_modtime':         file_modtime,
                    'file_size':            file_size,
                    'upload_user' :         file_own,
                    'auto_fail' :           auto_fail,
                    'auto_fail_code' :      auto_fail_code,
                    'bag_it_name':          bag_it_name,
                }

                files_to_process.append(data)
            else:
                pass
    return files_to_process if files_to_process else False

def file_owner(file_path):
    return getpwuid(stat(file_path).st_uid).pw_name

def file_modified_time(file_path):
    return datetime.datetime.fromtimestamp(getmtime(file_path))

def file_get_size(file_path):
    return getsize(file_path)

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

def zip_extract_all(file_path):
    extracted = False
    try:
        zf = zipfile.ZipFile(file_path,'r')
        zf.extractall('/data/tmp/')
        zf.close()
        extracted = True
    except Exception as e:
        print e
    return extracted

def tar_extract_all(file_path):
    extracted = False
    try:
        tf = tarfile.open(file_path, 'r:*')
        tf.extractall('/data/tmp/')
        tf.close()
        extracted = True
    except Exception as e:
        print e

    return extracted

def dir_extract_all(file_path):
    extracted = False
    try:
        # notice forward slash missing
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        copy_tree(file_path,'/data/tmp/{}'.format(file_path.split('/')[-1]), update=1)
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

                row_search = re.search(": ".join(patterns), line)
                if row_search:
                    fields[row_search.group('key').replace('-','_')] = row_search.group('val')
    except Exception as e:
        print e

    return fields


def remove_file_or_dir(path):
    print 'delete it ------ {}'.format(path)
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


def is_filename_valid(filename):
    is_valid = re.match('^[a-zA-Z0-9\-\_\/\.]+$',filename.split('/')[-1])
    return (True if is_valid else False)

def is_dir_or_file(path):
    if isdir(path): return True
    if isfile(path): return True
    return False