import bagit
import bagit_profile
import iso8601
import json
from os.path import isfile, join
from pycountry import languages

from transfer_app.lib import files_helper as FH
from transfer_app.form import BagInfoForm
from orgs.models import BAGLog, Archives



class bagChecker():

    def __init__(self,archiveObj):

        self.RAC_profile_identifier = 'https://raw.githubusercontent.com/RockefellerArchiveCenter/project_electron/master/transfer/organizational-bag-profile.json'
        self.bag_dates_to_validate = ['Date_Start', 'Date_End', 'Bagging_Date']

        self.archiveObj = archiveObj
        self.archive_extracted = self._extract_archive()
        self.archive_path = '/data/tmp/{}'.format(self.archiveObj.bag_it_name)
        self.ecode = ''
        self.bag = {}
        self.bag_info_data = []
        self.bag_exception = ''



    def _extract_archive(self):
        print 'attempts to archive'
        if self.archiveObj.machine_file_type == 'TAR':
            if not FH.tar_extract_all(self.archiveObj.machine_file_path):
                return False
        elif self.archiveObj.machine_file_type == 'ZIP':
            if not FH.zip_extract_all(self.archiveObj.machine_file_path):
                return False
        elif self.archiveObj.machine_file_type == 'OTHER':
            if not FH.dir_extract_all(self.archiveObj.machine_file_path):
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
            self._retrieve_bag_info_key_val() # run now to prevent multiple calls below
            return True

    def _is_rac_bag(self):
        """Assumes a valid bag/bag info; returns true if passes rac profile"""

        if not 'BagIt_Profile_Identifier' in self.bag_info_data:
            self.bag_exception = 'No BagIt Profile to validate against'
            return False
        else:

            if self.bag_info_data['BagIt_Profile_Identifier'] != self.RAC_profile_identifier:
                self.bag_exception = "Bag Identifier is not RAC version"
                return False

            try:
                profile = bagit_profile.Profile(self.bag_info_data['BagIt_Profile_Identifier'])

            except Exception as e:
                self.bag_exception = e
            else:

                # RE IMPLEMENTING  validate() SINCE VALIDATION MESSAGES ARE PRINTED
                # https://github.com/ruebot/bagit-profiles-validator/blob/master/bagit_profile.py
                # line 76

                try:
                    profile.validate_bag_info(self.bag)
                except Exception as e:
                    print e
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

                print "Bag valid according to RAC profile"
                return True

        return False

    def _has_valid_datatypes(self):
        """Assumes a valid bag/bag info; returns true if all datatypes in bag pass"""
        dates = []
        langz = []


        for k,v in self.bag_info_data.iteritems():
            if k in self.bag_dates_to_validate:
                dates.append(v)
            if k == 'Language':
                langz.append(v)

        if dates:
            for date in dates:
                try:
                    iso8601.parse_date(date)
                except Exception as e:
                    print e
                    self.bag_exception = e
                    return False

        if langz:
            for language in langz:
                try:
                    languages.lookup(language)
                except Exception as e:
                    print e
                    self.bag_exception = e
                    return False
        return True

    def _has_valid_metadata_file(self):
        """checks if the metadata file path and is json is correct if exist"""

        metadata_file = "/".join([str(self.bag), 'data', 'metadata.json'])

        if not isfile(metadata_file):
            print 'no metadata file'
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
            print 'bag didnt pass due to extract error'
            return self.bag_failed()

        if not self._is_generic_bag():
            self.ecode = 'GBERR'
            return self.bag_failed()

        if not self.bag_info_data:
            print 'couldnt read baginfo'
            # log internal error here
            return self.bag_failed()
        if not self.archiveObj.save_bag_data(self.bag_info_data):
            self.ecode = 'BIERR'
            return self.bag_failed()


        BAGLog.log_it('PBAG', self.archiveObj)

        if not self._is_rac_bag():
            self.ecode = 'RBERR'
            print 'didnt pass rac bag profile'
            return self.bag_failed()

        if not self._has_valid_datatypes():
            self.ecode = 'DTERR'
            print 'didnt pass rac datatype specs'
            return self.bag_failed()

        if not self._has_valid_metadata_file():
            self.ecode = 'MDERR'
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
