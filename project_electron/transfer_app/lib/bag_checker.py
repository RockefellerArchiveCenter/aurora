import bagit
import bagit_profile
import iso8601
import json
from os.path import isfile, join
from pycountry import languages

from transfer_app.lib import files_helper as FH
from transfer_app.form import BagInfoForm
from orgs.models import BAGLog

class bagChecker():

    def __init__(self,archiveObj):
        self.archiveObj = archiveObj
        self.archive_extracted = self._extract_archive()
        self.archive_path = '/data/tmp/{}'.format(self.archiveObj.bag_it_name)
        self.ecode = ''
        self.bag = {}


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
        is_bag = {}
        try:
            self.bag = bagit.Bag(self.archive_path)
            is_bag = self.bag.is_valid()
        except Exception as e:
            print e
        return is_bag

    def _is_rac_bag(self):

        # LOAD bag-info.txt key var
        BI_fields = FH.get_fields_from_file('{}/{}'.format(self.archive_path,'bag-info.txt'))

        if not BI_fields:
            print 'couldnt read baginfo'
            return False

        if not 'BagIt_Profile_Identifier' in BI_fields:
            print 'No BagIt Profile to validate against'
            return False
        else:
            if BI_fields['BagIt_Profile_Identifier'] != 'https://raw.githubusercontent.com/RockefellerArchiveCenter/project_electron/master/transfer/organizational-bag-profile.json':
                print "Bag Identifier is not RAC version"
                return False

            # self.bag = bagit.Bag(self.archive_path)
            profile = bagit_profile.Profile(BI_fields['BagIt_Profile_Identifier'])

            if profile.validate(self.bag):
                print "Bag valid according to RAC profile"
                return True
            else:
                print "Bag invalid according to RAC profile"
                return False

        return False

    def _has_valid_datatypes(self):
        dates = []
        languages = []

        # LOAD bag-info.txt key var
        BI_fields = FH.get_fields_from_file('{}/{}'.format(self.archive_path,'bag-info.txt'))

        if not BI_fields:
            print 'couldnt read baginfo'
            return False

        for k,v in BI_fields.items():
            if k in ['Date-Start', 'Date-End', 'Bagging-Date']:
                dates.append(v)
            if k == 'Languages':
                languages.append(v)

        if dates:
            for date in dates.items():
                try:
                    iso8601.parse_date(date)
                except:
                    print "invalid date: %s' % date"
                    return False

        if languages:
            for language in languages.items():
                try:
                    languages.lookup(language)
                except:
                    print "invalid language code: %s' % language"
                    return False

    def _has_valid_metadata_file(self):
        # is this the right path?
        metadata_file = join(self.bag, 'data', 'metadata.json')
        # check to see if data/metadata.json exists
        if isfile(metadata_file):
            try:
                return json.loads(metadata_file)
            except ValueError as e:
                print "invalid json: %s' % e"
                return False

    def bag_passed_all(self):
        if not self.archive_extracted:
            self.ecode = 'EXERR'
            print 'bag didnt pass due to extract error'
            return self.bag_failed()

        if not self._is_generic_bag():
            self.ecode = 'GBERR'
            print 'bag didnt pass due to not being valid bag'
            return self.bag_failed()
        BAGLog.log_it('PBAG', self.archiveObj)

        if not self._is_rac_bag():
            self.ecode = 'RBERR'
            print 'didnt pass rac bag profile'
            return self.bag_failed()

        if not self._has_valid_datatypes():
            self.ecode = 'RBERR'
            print 'didnt pass rac datatype specs'
            return self.bag_failed()

        if not self._has_valid_metadata_file():
            self.ecode = 'RBERR'
            print 'optional metadata file is not valid json'
            return self.bag_failed()
        BAGLog.log_it('PBAGP', self.archiveObj)

        self.cleanup()
        return True

    def bag_failed(self):
        self.cleanup()
        return False
    def cleanup(self):
        # FH.remove_file_or_dir(self.archive_path)
        pass
