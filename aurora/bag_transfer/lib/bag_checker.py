import glob
import json
import logging
from os.path import isfile, join

import bagit
import bagit_profile
import iso8601
from asterism.bagit_helpers import get_bag_info_fields
from asterism.file_helpers import (dir_extract_all, tar_extract_all,
                                   zip_extract_all)
from bag_transfer.lib import files_helper as FH
from bag_transfer.models import BAGLog
from django.conf import settings
from iso639 import languages

# sets logging levels to reduce garbage printed in logs
logging.getLogger("bagit").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.CRITICAL)


class BagChecker:
    def __init__(self, transferObj):

        self.tmp_path = settings.TRANSFER_EXTRACT_TMP
        self.bag_dates_to_validate = ["Date_Start", "Date_End", "Bagging_Date"]
        self.transferObj = transferObj
        self.transfer_extracted = self._extract_transfer()
        self.transfer_path = join(self.tmp_path, self.transferObj.bag_it_name)
        self.ecode = ""
        self.bag = {}
        self.bag_info_data = {}
        self.bag_exception = ""

    def _extract_transfer(self):
        if self.transferObj.machine_file_type == "TAR":
            if not tar_extract_all(self.transferObj.machine_file_path, self.tmp_path):
                return False
        elif self.transferObj.machine_file_type == "ZIP":
            if not zip_extract_all(self.transferObj.machine_file_path, self.tmp_path):
                return False
        elif self.transferObj.machine_file_type == "OTHER":
            if not dir_extract_all(self.transferObj.machine_file_path, self.tmp_path):
                return False
        else:
            return False
        return True

    def _is_generic_bag(self):
        """Basic BagIt validation."""
        try:
            self.bag = bagit.Bag(self.transfer_path)
            self.bag.validate()
        except ValueError as e:
            self.bag_exception = "Error during BagIt validation (likely caused by presence of unsupported md5 checksum): {}".format(e)
            return False
        except Exception as e:
            self.bag_exception = "Error during BagIt validation: {}".format(e)
            return False
        else:
            for filename in glob.glob(join(self.transfer_path, "manifest-*.txt")):
                with open(filename, "r") as manifest_file:
                    self.transferObj.manifest = manifest_file.read()
            self._retrieve_bag_info_key_val()  # run now to prevent multiple calls below
            return True

    def _is_rac_bag(self):
        """Assumes a valid bag/bag info; returns true if passes rac profile"""

        if "BagIt_Profile_Identifier" not in self.bag_info_data:
            self.bag_exception = "No BagIt Profile to validate against"
            return False
        else:
            try:
                profile = bagit_profile.Profile(self.bag_info_data["BagIt_Profile_Identifier"])
            except BaseException:
                self.bag_exception = "Cannot retrieve BagIt Profile from URL {}".format(
                    self.bag_info_data["BagIt_Profile_Identifier"])
                return False
            else:
                if not profile.validate(self.bag):
                    self.bag_exception = profile.report.errors
                    return False
                return True

        return False

    def _has_valid_datatypes(self):
        """Assumes a valid bag/bag info; returns true if all datatypes in bag pass"""
        dates = []
        for k, v in self.bag_info_data.items():
            if k in self.bag_dates_to_validate:
                dates.append(v)

        langz = self.bag_info_data.get("Language", None)
        if dates:
            for date in dates:
                try:
                    iso8601.parse_date(date)
                except Exception:
                    self.bag_exception = "Invalid date value: {}".format(date)
                    return False

        if langz:
            if not isinstance(langz, list):
                langz = [langz]
            for language in langz:
                try:
                    languages.get(part2b=language)
                except KeyError:
                    self.bag_exception = "Invalid language value: {}".format(language)
                    return False
        return True

    def _has_valid_metadata_file(self):
        """checks if the metadata file path and is json is correct if exist"""

        metadata_file = join(str(self.bag), "data", "metadata.json")

        if not isfile(metadata_file):
            return True
        else:
            try:
                return json.loads(FH.get_file_contents(metadata_file))
            except ValueError:
                return False

    def bag_passed_all(self):
        if not self.transfer_extracted:
            self.ecode = "EXERR"
            return self.bag_failed()

        if not self._is_generic_bag():
            self.ecode = "GBERR"
            return self.bag_failed()

        if not self.bag_info_data:
            return self.bag_failed()

        BAGLog.log_it("PBAG", self.transferObj)

        if not self._is_rac_bag():
            self.ecode = "RBERR"
            return self.bag_failed()

        if not self._has_valid_datatypes():
            self.ecode = "DTERR"
            return self.bag_failed()

        if not self._has_valid_metadata_file():
            self.ecode = "MDERR"
            return self.bag_failed()

        if not self.transferObj.save_bag_data(self.bag_info_data):
            self.ecode = "BIERR"
            return self.bag_failed()

        if not self.transferObj.assign_rights():
            self.ecode = "RSERR"
            return self.bag_failed()

        BAGLog.log_it("PBAGP", self.transferObj)

        self.cleanup()
        return True

    def bag_failed(self):
        self.cleanup()
        return False

    def cleanup(self):
        """called on success of failure of bag_checker routine"""
        if self.bag_exception:
            self.transferObj.additional_error_info = self.bag_exception

    def _retrieve_bag_info_key_val(self):
        """Returns list of key val of bag info fields, only run on valid bag object"""
        if not self.bag.is_valid():
            return False

        self.bag_info_data = get_bag_info_fields(self.transfer_path)
