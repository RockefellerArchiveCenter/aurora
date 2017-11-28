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


def has_files_to_process():
    files_to_process = []

    #move over functions and replace file logic
    discover_files_to_process()
    uploads = uploads_to_process()

    if uploads:
        print '{} paths to upload'.format(len(uploads))
        for file_path in uploads:
            print file_path

            auto_fail = False
            auto_fail_code = ''
            # auto_fail_data = ''
            bag_it_name = file_path.split('/')[-1]
            file_type = 'OTHER'
            file_size = 0

            # DOES FILE STILL EXIST?
            if len(file_path) <=2 or not is_dir_or_file(file_path):
                BAGLog.log_it('DEXT')
                continue

            print "staring file: {}".format(file_path)


            # convert this into a transfer file object !!! lot less code D.L.
            file_own =      file_owner(file_path)
            file_modtime =  file_modified_time(file_path)
            file_date =     file_modtime.date()
            file_time =     file_modtime.time()

            # CHECK FNAME BASED ON SPEC
            if not is_filename_valid(file_path):
                auto_fail = True
                auto_fail_code = 'BFNM'
            else:

                scanresult = None
                try:
                    # Virus Scanning First
                    virus_checker = VirusScan()
                except ValueError as e:
                    print e
                    BAGLog.log_it('VCONN')
                    continue

                try:
                    scanresult = virus_checker.scan(file_path)

                except ConnectionError as e:
                    print e
                    BAGLog.log_it('VCON2')
                    continue

                except Exception as e:
                    ## more than likely Socket
                    BAGLog.log_it('VSOCK')
                    print e
                    continue
                # ALL The continues Above actually should yield attention to APP Team

                if scanresult:
                    print scanresult
                    print 'VIRUS IDENTIFIED'

                    #quarantine or move
                    remove_file_or_dir(file_path)
                    auto_fail = True
                    auto_fail_code = 'VIRUS'


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

                    else:
                        # IS UNSERIALIZED DIR
                        if not isdir(file_path):
                            # print 'we have problems isnt dir'
                            auto_fail = True
                            auto_fail_code = 'BDIR'

                    #returns filesize in kbs -- need type so moved logic down here
                    file_size = file_get_size(file_path, file_type)

                    if not file_size or (type(file_size) is tuple and not file_size[0]):

                        auto_fail = True
                        auto_fail_code = ('FSERR' if type(file_size) is not tuple else file_size[1])
                        file_size = 0

                    else:

                        transfer_max = (settings.TRANSFER_FILESIZE_MAX * 1000)
                        print "\nFile is {}\n".format(file_size)

                        if file_size > transfer_max:
                            auto_fail = True
                            auto_fail_code = 'FSERR'

                            # handle dir ending in splash
                            bag_it_name = file_path.split('/')[-1]


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
                # 'auto_fail_data' :      auto_fail_data,
                'bag_it_name':          bag_it_name,
                'virus_scanresult' :    scanresult
            }

            files_to_process.append(data)
    else:
        pass
    return files_to_process if files_to_process else False

def open_files_list():

    path_list = []

    for proc in psutil.process_iter():
        open_files = proc.open_files()
        if open_files:
            for fileObj in open_files:
                path_list.append(fileObj.path)
    return path_list

def get_active_org_contents_dict():
    root_path = '/data/{}/upload/'
    target_dirs = []
    org_dir_contents = {}

    active_orgs = Organization.objects.filter(is_active=True)
    if active_orgs:
        for org in active_orgs:
            upload_dir = root_path.format(org.machine_name)
            target_dirs.append(upload_dir)

            dir_content = listdir(upload_dir)
            if dir_content:
                for item in dir_content:
                    item_path = "{}{}".format(upload_dir, item)
                    if org.machine_name not in org_dir_contents:
                        org_dir_contents[org.machine_name] = {
                            'files' : [],
                            'dirs'  : [],
                            'count' : 0
                        }

                    if isfile(item_path):
                        org_dir_contents[org.machine_name]['files'].append(item_path)
                        org_dir_contents[org.machine_name]['count'] +=1
                    elif isdir(item_path):
                        org_dir_contents[org.machine_name]['dirs'].append(item_path)
                        org_dir_contents[org.machine_name]['count'] +=1
    return org_dir_contents

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


def org_contents_in_lsof(contents):
    rm_list = []

    for org, obj in contents.iteritems():
        # GET OPEN FILES
        open_files = open_files_list()
        if obj['count'] < 1:
            continue
        # get files
        for f in obj['files']:
            if f in open_files:
                rm_list.append((org,0,f))

        # get directory
        for d in obj['dirs']:
            # ck files in directory are on list
            for fls in files_in_unserialized(d,True):
                if fls in open_files:
                    rm_list.append((org,1,d))
    return rm_list



def rm_frm_contents(cObj,contents):
    for obj in cObj:
        if obj[1] == 0 and isfile(obj[2]):
            contents[obj[0]]['files'] = [x for x in contents[obj[0]]['files'] if x != obj[2]]

        elif obj[1] == 1 and isdir(obj[2]):
            contents[obj[0]]['dirs'] = [x for x in contents[obj[0]]['dirs'] if x != obj[2]]


def mv_to_processing(contentsObj):
    for org,obj in contentsObj.iteritems():
        mergedlist = obj['files'] + obj['dirs']
        for f in mergedlist:

            processing_path = f.replace('upload','processing')
            print "moving {} to \n{}".format(f, processing_path)
            move(f,processing_path)

def discover_files_to_process():
    active_org_contents = get_active_org_contents_dict()

    if active_org_contents:
        rm_any = org_contents_in_lsof(active_org_contents)

        if rm_any:
            rm_frm_contents(rm_any,active_org_contents)

        # HAVE FILE MOVE ALL TO PROCESSING DIR
        print active_org_contents
        mv_to_processing(active_org_contents)

def uploads_to_process():
    paths = []
    active_orgs = active_orgs = Organization.objects.filter(is_active=True)
    if active_orgs:
        print 'Checking {} active org processing dir'.format(len(active_orgs))
        for org in active_orgs:
            org_processing = '/data/{}/processing/'.format(org.machine_name)
            contents = listdir(org_processing)


            org_paths = ["{}{}".format(org_processing,x) for x in contents]
            paths = paths + org_paths

    return paths

def file_owner(file_path):
    return getpwuid(stat(file_path).st_uid).pw_name

def file_modified_time(file_path):
    return datetime.datetime.fromtimestamp(getmtime(file_path))

def file_get_size(file_path,file_type):
    """returns file size of archive, or of directory; expects top level validation to run already"""

    filesize = 0
    if isfile(file_path):
        if file_type == 'TAR':
            top_level_dir = tar_has_top_level_only(file_path)
            if not top_level_dir:
                return (0, 'BTAR2')

            if tar_extract_all(file_path):
                tmp_dir_path = "{}{}".format('/data/tmp/', top_level_dir)
                filesize = get_dir_size(tmp_dir_path)
                remove_file_or_dir(tmp_dir_path)
        elif file_type == 'ZIP':
            top_level_dir = zip_has_top_level_only(file_path)
            if not top_level_dir:
                return (0, 'BZIP2')
            if zip_extract_all(file_path):
                tmp_dir_path = "{}{}".format('/data/tmp/', top_level_dir)
                filesize = get_dir_size(tmp_dir_path)
                remove_file_or_dir(tmp_dir_path)

        elif file_type == OTHER:
            filesize = getsize(file_path)

    elif isdir(file_path):
        filesize = get_dir_size(file_path)
    return filesize

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


def is_filename_valid(filename):
    is_valid = re.match('^[a-zA-Z0-9\-\_\/\.\s]+$',filename.split('/')[-1])
    return (True if is_valid else False)

def is_dir_or_file(path):
    if isdir(path): return True
    if isfile(path): return True
    return False

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
