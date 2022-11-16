import glob
import json
import logging
from os.path import isfile, join

import bagit
import bagit_profile
import iso8601
from asterism.bagit_helpers import get_bag_info_fields
from iso639 import languages

from bag_transfer.api.serializers import BagItProfileSerializer
from bag_transfer.lib import files_helper as FH
from bag_transfer.models import BagItProfile, BAGLog

# sets logging levels to reduce garbage printed in logs
logging.getLogger("bagit").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.CRITICAL)


class BagCheckerException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class BagChecker:
    def __init__(self, transferObj):

        self.bag_dates_to_validate = ["Date_Start", "Date_End", "Bagging_Date"]
        self.transferObj = transferObj
        self.transfer_path = self.transferObj.machine_file_path
        self.ecode = ""
        self.bag = {}
        self.bag_info_data = {}
        self.bag_exception = ""

    def _is_generic_bag(self):
        """Basic BagIt validation."""
        try:
            self.bag = bagit.Bag(self.transfer_path)
            self.bag.validate()
        except ValueError as e:
            raise BagCheckerException(
                "GBERR",
                f"Error during BagIt validation (likely caused by presence of unsupported md5 checksum): {e}")
        except Exception as e:
            raise BagCheckerException("GBERR", f"Error during BagIt validation: {e}")
        else:
            for filename in glob.glob(join(self.transfer_path, "manifest-*.txt")):
                with open(filename, "r") as manifest_file:
                    self.transferObj.manifest = manifest_file.read()
            self._retrieve_bag_info_key_val()  # run now to prevent multiple calls below
            if not self.bag_info_data:
                raise BagCheckerException("GBERR", "Unable to fetch metadata from bag_info.txt")
            return True

    def _is_rac_bag(self):
        """Assumes a valid bag/bag info; returns true if passes rac profile"""

        if "BagIt_Profile_Identifier" not in self.bag_info_data:
            raise BagCheckerException("RBERR", "No BagIt Profile to validate against")
        else:
            try:
                profile = bagit_profile.Profile(self.bag_info_data["BagIt_Profile_Identifier"])
            except BaseException:
                profile_obj = BagItProfile.objects.get(organization=self.transferObj.organization)
                profile_data = BagItProfileSerializer(profile_obj, context={"request": None}).data
                profile = bagit_profile.Profile(self.bag_info_data["BagIt_Profile_Identifier"], profile=profile_data)
            else:
                if not profile.validate(self.bag):
                    raise BagCheckerException("RBERR", profile.report.errors)
                return True

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
                    raise BagCheckerException("DTERR", f"Invalid date value: {date}")
        if langz:
            if not isinstance(langz, list):
                langz = [langz]
            for language in langz:
                try:
                    languages.get(part2b=language)
                except KeyError:
                    raise BagCheckerException("DTERR", f"Invalid language value: {language}")
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
                raise BagCheckerException("MDERR", "Invalid JSON file")

    def _retrieve_bag_info_key_val(self):
        """Returns list of key val of bag info fields, only run on valid bag object"""
        if not self.bag.is_valid():
            return False
        self.bag_info_data = get_bag_info_fields(self.transfer_path)

    def bag_passed_all(self):
        try:
            self._is_generic_bag()
            BAGLog.log_it("PBAG", self.transferObj)
            self._is_rac_bag()
            self._has_valid_datatypes()
            self._has_valid_metadata_file()
        except BagCheckerException as err:
            self.ecode = err.code
            self.bag_exception = err.message
            return self.bag_failed()

        if not self.transferObj.save_bag_data(self.bag_info_data):
            self.ecode = "BIERR"

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
