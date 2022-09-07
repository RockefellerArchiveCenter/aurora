import pwd
import random
import string
from datetime import datetime
from os import chown, listdir, path

from asterism.file_helpers import copy_file_or_dir
from django.test import TestCase, modify_settings, override_settings
from django.utils.timezone import make_aware

from bag_transfer.models import (LanguageCode, Organization, RecordCreators,
                                 User)
from bag_transfer.rights.models import (RecordType, RightsStatement,
                                        RightsStatementCopyright,
                                        RightsStatementLicense,
                                        RightsStatementOther,
                                        RightsStatementRightsGranted,
                                        RightsStatementStatute)

BAGS_REF = (
    ("valid_bag", ""),
    ("changed_file", "GBERR", True),
    ("missing_bag_manifest", "GBERR", True),
    ("missing_bag_declaration", "GBERR", True),
    ("missing_payload_directory", "GBERR", True),
    ("missing_payload_manifest", "GBERR", True),
    ("missing_description", "RBERR", True),
    ("missing_record_type", "RBERR", True),
    ("missing_source_organization", "RBERR", True),
    ("missing_title", "RBERR", True),
    ("repeating_record_type", "RBERR", True),
    ("repeating_source_organization", "RBERR", True),
    ("repeating_title", "RBERR", True),
    ("unauthorized_record_type", "RBERR", True),
    ("unauthorized_source_organization", "RBERR", True),
    ("invalid_metadata_file", "MDERR", True),
    ("invalid_datatype_date", "DTERR", True),
    ("invalid_datatype_language", "DTERR", True),
)

BAGINFO_FIELD_CHOICES = (
    ("source_organization", "Source-Organization"),
    ("organization_address", "Organization-Address"),
    ("contact_name", "Contact-Name"),
    ("contact_phone", "Contact-Phone"),
    ("contact_email", "Contact-Email"),
    ("external_description", "External-Description"),
    ("external_identifier", "External-Identifier"),
    ("internal_sender_description", "Internal-Sender-Description"),
    ("internal_sender_identifier", "Internal-Sender-Identifier"),
    ("title", "Title"),
    ("date_start", "Date-Start"),
    ("date_end", "Date-End"),
    ("record_creators", "Record-Creators"),
    ("record_type", "Record-Type"),
    ("language", "Language"),
    ("bagging_date", "Bagging-Date"),
    ("bag_group_identifier", "Bag-Group-Identifier"),
    ("bag_count", "Bag-Count"),
    ("bag_size", "Bag-Size"),
    ("payload_oxum", "Payload-Oxum"),
)

RIGHTS_BASIS_DATA = [
    {
        "rights_basis": "Copyright",
        "applies_to_type": [2],
        "rightsstatementcopyright_set-INITIAL_FORMS": 0,
        "rightsstatementcopyright_set-TOTAL_FORMS": 1,
        "rightsstatementcopyright_set-0-copyright_note": "Test note",
        "rightsstatementcopyright_set-0-copyright_status": "copyrighted",
        "rightsstatementcopyright_set-0-copyright_jurisdiction": "us",
    },
    {
        "rights_basis": "Statute",
        "applies_to_type": [2],
        "rightsstatementstatute_set-INITIAL_FORMS": 0,
        "rightsstatementstatute_set-TOTAL_FORMS": 1,
        "rightsstatementstatute_set-0-statute_note": "Test note",
        "rightsstatementstatute_set-0-statute_citation": "Test statute citation",
        "rightsstatementstatute_set-0-statute_jurisdiction": "us",
    },
    {
        "rights_basis": "License",
        "applies_to_type": [2],
        "rightsstatementlicense_set-INITIAL_FORMS": 0,
        "rightsstatementlicense_set-TOTAL_FORMS": 1,
        "rightsstatementlicense_set-0-license_note": "Test note",
    },
    {
        "rights_basis": "Other",
        "applies_to_type": [2],
        "rightsstatementother_set-INITIAL_FORMS": 0,
        "rightsstatementother_set-TOTAL_FORMS": 1,
        "rightsstatementother_set-0-other_rights_note": "Test note",
        "rightsstatementother_set-0-other_rights_basis": "Donor",
    },
]

RIGHTS_GRANTED_DATA = {
    "rights_granted-TOTAL_FORMS": 1,
    "rights_granted-INITIAL_FORMS": 0,
    "rights_granted-0-act": random.choice(
        ["publish", "disseminate", "replicate", "migrate", "modify", "use", "delete"]
    ),
    "rights_granted-0-restriction": random.choice(
        ["allow", "disallow", "conditional"]
    ),
    "rights_granted-0-rights_granted_note": "Grant note",
}


def random_string(length):
    """Returns a random string of specified length."""
    return "".join(random.choice(string.ascii_letters) for m in range(length))


def random_date(year):
    """Returns a random date in a given year."""
    try:
        return datetime.strptime("{} {}".format(random.randint(1, 366), year), "%j %Y")
    # accounts for leap year values
    except ValueError:
        random_date(year)


def create_test_record_types(record_types=None):
    """Creates a RecordType object for each value in list provided.
    If no list is given, RecordTypes are create for each item in a default list."""
    objects = []
    record_types = record_types if record_types else [
        "administrative records",
        "board materials",
        "communications and publications",
        "grant records",
        "annual reports",
    ]
    for record_type in record_types:
        object = RecordType.objects.create(name=record_type)
        objects.append(object)
    return objects


def create_target_bags(target_str, test_bags_dir, org, username="root"):
    """Creates target bags to be picked up by a TransferRoutine based on a string.
    This allows processing of bags serialized in multiple formats at once."""
    moved_bags = []
    target_bags = [b for b in listdir(test_bags_dir) if b.startswith(target_str)]
    if len(target_bags) < 1:
        return False
    for bag_name in target_bags:
        new_path = path.join(org.org_machine_upload_paths()[0], bag_name)
        copy_file_or_dir(path.join(test_bags_dir, bag_name), new_path)
        chown(new_path, pwd.getpwnam(username).pw_uid, -1)
        moved_bags.append(new_path)
    return moved_bags


def create_rights_statement(record_type=None, org=None, rights_basis=None):
    """Creates a rights statement given a record type, organization and rights basis.
    If any one of these values are not given, random values are assigned."""
    if len(RecordType.objects.all()) == 0:
        create_test_record_types()
    record_type = (
        record_type if record_type else random.choice(RecordType.objects.all())
    )
    if org is None:
        org = random.choice(Organization.objects.all())
    if rights_basis is None:
        rights_basis = random.choice(["Copyright", "Statute", "License", "Other"])
    rights_statement = RightsStatement(organization=org, rights_basis=rights_basis,)
    rights_statement.save()
    rights_statement.applies_to_type.add(record_type)
    return rights_statement


def create_test_rights_info(rights_statement=None):
    """Creates a rights info object given a rights statement
    If no rights statement is given, a random value is selected"""
    rights_statement = (
        rights_statement
        if rights_statement
        else random.choice(RightsStatement.objects.all())
    )
    if rights_statement.rights_basis == "Statute":
        rights_info = RightsStatementStatute(
            statute_citation=random_string(50),
            statute_applicable_start_date=random_date(1960),
            statute_applicable_end_date=random_date(1990),
            statute_end_date_period=20,
            statute_note=random_string(40),
        )
    elif rights_statement.rights_basis == "Other":
        rights_info = RightsStatementOther(
            other_rights_basis=random.choice(["Donor", "Policy"]),
            other_rights_applicable_start_date=random_date(1978),
            other_rights_end_date_period=20,
            other_rights_end_date_open=True,
            other_rights_note=random_string(50),
        )
    elif rights_statement.rights_basis == "Copyright":
        rights_info = RightsStatementCopyright(
            copyright_status=random.choice(["copyrighted", "public domain", "unknown"]),
            copyright_applicable_start_date=random_date(1950),
            copyright_end_date_period=40,
            copyright_note=random_string(70),
        )
    elif rights_statement.rights_basis == "License":
        rights_info = RightsStatementLicense(
            license_applicable_start_date=random_date(1980),
            license_start_date_period=10,
            license_end_date_open=True,
            license_note=random_string(60),
        )
    rights_info.rights_statement = rights_statement
    rights_info.save()


def create_test_rights_granted(rights_statement=None, granted_count=1):
    """Creates one or more rights granted objects, based on the grant count.
    If no rights statement is given, a random value is selected."""
    rights_statement = (
        rights_statement
        if rights_statement
        else random.choice(RightsStatement.objects.all())
    )
    all_rights_granted = []
    for x in range(granted_count):
        rights_granted = RightsStatementRightsGranted(
            rights_statement=rights_statement,
            act=random.choice(
                [
                    "publish",
                    "disseminate",
                    "replicate",
                    "migrate",
                    "modify",
                    "use",
                    "delete",
                ]
            ),
            start_date=random_date(1984),
            end_date_period=15,
            rights_granted_note=random_string(100),
            restriction=random.choice(["allow", "disallow", "conditional"]),
        )
        rights_granted.save()
        all_rights_granted.append(rights_granted)
    return all_rights_granted


def create_test_record_creators(count=1):
    record_creators = []
    for n in range(count):
        record_creator = RecordCreators(name=random_string(50))
        record_creator.save()
        record_creators.append(record_creator)
    return record_creators


def create_test_languages(count=1):
    languages = []
    for n in range(count):
        language = LanguageCode(code=random_string(3))
        language.save()
        languages.append(language)
    return languages


def get_accession_data(creator=None):
    creator = creator if creator else create_test_record_creators()[0]
    language = create_test_languages()[0]
    accession_data = {
        "use_restrictions": random_string(100),
        "access_restrictions": random_string(100),
        "resource": "http://example.org",
        "description": random_string(150),
        "end_date": make_aware(random_date(1990)),
        "extent_size": "17275340",
        "acquisition_type": random.choice(["donation", "deposit", "gift"]),
        "title": random_string(255),
        "accession_number": "2018.184",
        "start_date": make_aware(random_date(1960)),
        "extent_files": "14",
        "appraisal_note": random_string(150),
        "language": language,
    }
    return accession_data


def get_accession_form_data(creator=None):
    creator = creator if creator else create_test_record_creators()[0]
    language = create_test_languages()[0]
    accession_data = {
        "use_restrictions": random_string(100),
        "access_restrictions": random_string(100),
        "resource": "http://example.org",
        "description": random_string(150),
        "end_date": random_date(1990),
        "extent_size": "17275340",
        "acquisition_type": random.choice(["donation", "deposit", "gift"]),
        "title": random_string(255),
        "accession_number": "2018.184",
        "start_date": random_date(1960),
        "extent_files": "14",
        "appraisal_note": random_string(150),
        "language": language.id,
        "creators": [creator.id],
        "form-0-id": creator.id,
        "form-MIN_NUM_FORMS": 0,
        "form-0-name": creator.name,
        "form-TOTAL_FORMS": 1,
        "form-INITIAL_FORMS": 1,
        "form-MAX_NUM_FORMS": 1000,
        "form-0-type": "organization",
    }
    return accession_data


@modify_settings(MIDDLEWARE={"remove": "bag_transfer.middleware.cognito.CognitoUserMiddleware"})
@override_settings(COGNITO_USE=False)
class TestMixin(TestCase):

    def setUp(self):
        self.client.force_login(User.objects.get(username="admin"))

    def assert_status_code(self, method, url, status_code, data=None, ajax=False):
        """Asserts that a request returns the expected HTTP status_code."""
        if ajax:
            response = getattr(self.client, method)(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        else:
            response = getattr(self.client, method)(url, data)
        self.assertEqual(
            response.status_code, status_code,
            f"Unexpected status code {response.status_code} for url {url}")
        return response
