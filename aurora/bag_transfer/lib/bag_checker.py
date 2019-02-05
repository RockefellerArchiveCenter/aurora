import bagit
import bagit_profile
import iso8601
import glob
import json
from os.path import isfile, join
from pycountry import languages

from django.conf import settings
from django.urls import reverse

from aurora import config
from bag_transfer.lib import files_helper as FH
from bag_transfer.models import BAGLog, Archives


class bagChecker():

    def __init__(self, archiveObj):

        self.tmp_path = settings.TRANSFER_EXTRACT_TMP
        self.RAC_profile_identifier = 'https://raw.githubusercontent.com/RockefellerArchiveCenter/project_electron/master/transfer/organizational-bag-profile.json'
        self.bag_dates_to_validate = ['Date_Start', 'Date_End', 'Bagging_Date']
        self.archiveObj = archiveObj
        self.archive_extracted = self._extract_archive()
        self.archive_path = '{}{}'.format(self.tmp_path, self.archiveObj.bag_it_name)
        self.ecode = ''
        self.bag = {}
        self.bag_info_data = {}
        self.bag_exception = ''

    def _extract_archive(self):
        if self.archiveObj.machine_file_type == 'TAR':
            if not FH.tar_extract_all(self.archiveObj.machine_file_path, self.tmp_path):
                return False
        elif self.archiveObj.machine_file_type == 'ZIP':
            if not FH.zip_extract_all(self.archiveObj.machine_file_path, self.tmp_path):
                return False
        elif self.archiveObj.machine_file_type == 'OTHER':
            if not FH.dir_extract_all(self.archiveObj.machine_file_path, self.tmp_path):
                return False
        else:
            return False
        return True

    def _is_generic_bag(self):
        try:
            self.bag = bagit.Bag(self.archive_path)
            self.bag.validate()

        except Exception as e:
            print e
            self.bag_exception = e
            return False
        else:
            # save manifest
            for filename in glob.glob('{}/manifest-*.txt'.format(self.archive_path)):
                with open(filename, 'r') as manifest_file:
                    self.archiveObj.manifest = manifest_file.read()
            self._retrieve_bag_info_key_val() # run now to prevent multiple calls below
            return True

    def _is_rac_bag(self):
        """Assumes a valid bag/bag info; returns true if passes rac profile"""

        if 'BagIt_Profile_Identifier' not in self.bag_info_data:
            self.bag_exception = 'No BagIt Profile to validate against'
            return False
        else:

            try:
                profile = bagit_profile.Profile(self.bag_info_data['BagIt_Profile_Identifier'])
            except BaseException:
                self.bag_exception = "Cannot retrieve BagIt Profile from URL {}".format(self.bag_info_data['BagIt_Profile_Identifier'])
                return False
            else:

                # RE IMPLEMENTING  validate() SINCE VALIDATION MESSAGES ARE PRINTED
                # https://github.com/ruebot/bagit-profiles-validator/blob/master/bagit_profile.py
                # line 76

                try:
                    profile.validate_bag_info(self.bag)
                except Exception as e:
                    self.bag_exception = "Error in bag-info.txt: {}".format(e.value)
                    return False
                try:
                    profile.validate_manifests_required(self.bag)
                except Exception as e:
                    self.bag_exception = "Required manifests not found: {}".format(e.value)
                    return False
                try:
                    profile.validate_tag_manifests_required(self.bag)
                except Exception as e:
                    self.bag_exception = "Required tag manifests not found: {}".format(e.value)
                    return False
                try:
                    profile.validate_tag_files_required(self.bag)
                except Exception as e:
                    self.bag_exception = "Required tag files not found: {}".format(e.value)
                    return False
                try:
                    profile.validate_allow_fetch(self.bag)
                except Exception as e:
                    self.bag_exception = "fetch.txt is present but is not allowed: {}".format(e.value)
                    return False
                try:
                    profile.validate_accept_bagit_version(self.bag)
                except Exception as e:
                    self.bag_exception = "Required BagIt version not found: {}".format(e.value)
                    return False

                return True

        return False

    def _has_valid_datatypes(self):
        """Assumes a valid bag/bag info; returns true if all datatypes in bag pass"""
        dates = []
        for k,v in self.bag_info_data.iteritems():
            if k in self.bag_dates_to_validate:
                dates.append(v)

        langz = self.bag_info_data.get('Language', None)
        if dates:
            for date in dates:
                try:
                    iso8601.parse_date(date)
                except Exception as e:
                    print e
                    self.bag_exception = e
                    return False

        if langz:
            if type(langz) is not list:
                langz = [langz]
            for language in langz:
                try:
                    languages.get(alpha_3=language)
                except Exception as e:
                    print e
                    self.bag_exception = "Invalid language value: {}".format(language)
                    return False
        return True

    def _has_valid_metadata_file(self):
        """checks if the metadata file path and is json is correct if exist"""

        metadata_file = "/".join([str(self.bag), 'data', 'metadata.json'])

        if not isfile(metadata_file):
            return True
        else:
            try:
                return json.loads(FH.get_file_contents(metadata_file))
            except ValueError as e:
                # self.bag_exception = 'optional metadata file is not valid json'
                return False

    def bag_passed_all(self):
        if not self.archive_extracted:
            self.ecode = 'EXERR'
            print 'Extract error'
            return self.bag_failed()

        if not self._is_generic_bag():
            print 'Bag validation failed'
            self.ecode = 'GBERR'
            return self.bag_failed()

        if not self.bag_info_data:
            print 'Unreadable bag-info'
            # log internal error here
            return self.bag_failed()

        BAGLog.log_it('PBAG', self.archiveObj)

        if not self._is_rac_bag():
            self.ecode = 'RBERR'
            print 'Bag Profile validation failed'
            return self.bag_failed()

        if not self._has_valid_datatypes():
            self.ecode = 'DTERR'
            print 'Datatype validation failed'
            return self.bag_failed()

        if not self._has_valid_metadata_file():
            self.ecode = 'MDERR'
            print 'Invalid metadata file'
            return self.bag_failed()

        if not self.archiveObj.save_bag_data(self.bag_info_data):
            self.ecode = 'BIERR'
            print 'Failed to save bag-info data'
            return self.bag_failed()

        if not self.archiveObj.assign_rights():
            self.ecode = 'RSERR'
            print 'Failed to assign rights'
            return self.bag_failed()

        BAGLog.log_it('PBAGP', self.archiveObj)

        self.cleanup()
        return True

    def bag_failed(self):
        self.cleanup()
        return False

    def cleanup(self):
        """called on success of failure of bag_checker routine"""
        if self.bag_exception:
            self.archiveObj.additional_error_info = self.bag_exception

    def _retrieve_bag_info_key_val(self):
        """Returns list of key val of bag info fields, only run on valid bag object"""
        if not self.bag.is_valid():
            return False

        self.bag_info_data = FH.get_fields_from_file('{}/{}'.format(self.archive_path,'bag-info.txt'))
