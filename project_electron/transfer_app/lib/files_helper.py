from os import stat
from os.path import isfile, getmtime, getsize
from pwd import getpwuid
import re
import datetime

from django.conf import settings


def has_files_to_process():
    files_to_process = []

    with open(settings.UPLOAD_LOG_FILE) as f:
        lines_with_data = []
        for line in f.readlines():
            patterns = [
                'Date:(?P<date>\d{4}\-\d{2}\-\d{2})',
                'Time:(?P<time>[\d\:\-\.]+)\s',
                'File:(?P<file_path>[\w\/\.]+)'
            ]

            get_uploads = re.search('.+'.join(patterns), line);
            if get_uploads:
                # DOES FILE CURRENTLY EXIST
                if not isfile(get_uploads.group('file_path')):
                    print get_uploads.group('file_path')
                    print 'we have problems'
                    continue

                # GETTING ORGANIZATION
                get_org = re.search('\/(?P<organization>org\d+)\/',get_uploads.group('file_path'))
                if not get_org:
                    print 'throw message in log'
                    continue


                files_to_process.append({
                    'date':                 get_uploads.group('date'),
                    'time':                 get_uploads.group('time'),
                    'file_path':            get_uploads.group('file_path'),
                    'file_modtime':         file_modified_time(get_uploads.group('file_path')),
                    'file_size':            file_get_size(get_uploads.group('file_path')),
                    'org':                  get_org.group('organization'),
                    'upload_user' :         file_owner(get_uploads.group('file_path'))
                })
            else:
                # report to logs
                go = 1
    return files_to_process if files_to_process else False

def file_owner(file_path):
    return getpwuid(stat(file_path).st_uid).pw_name

def file_modified_time(file_path):
    return datetime.datetime.fromtimestamp(getmtime(file_path))

def file_get_size(file_path):
    return getsize(file_path)

