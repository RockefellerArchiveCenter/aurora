import random
from bag_transfer.rights.models import RightsStatementCopyright, RightsStatementLicense, RightsStatementOther, RightsStatementStatute

POTUS_NAMES = [
    'Ford',
    'Obama',
    'Trump',
    'Bush',
    'Clinton'
]
COMPANY_SUFFIX = [
    'Foundation', 'Group', 'Org'
]
TEST_ORG_COUNT = 3

# tuple of tuples
# (str that test bag starts with, ecode, test on bag checker, test on transfer routine)
bags_ref = (
    ('invalid<filename', 'BFNM', False, True),

    ('valid_bag', ''),

    ('changed_file', 'GBERR', True),
    ('missing_bag_manifest', 'GBERR', True),
    ('missing_bag_declaration', 'GBERR', True),
    ('missing_payload_directory', 'GBERR', True),
    ('missing_payload_manifest', 'GBERR', True),

    ('missing_description', 'RBERR', True),
    ('missing_record_type', 'RBERR', True),
    ('missing_source_organization', 'RBERR', True),
    ('missing_title', 'RBERR', True),
    ('repeating_record_type', 'RBERR', True),
    ('repeating_source_organization', 'RBERR', True),
    ('repeating_title', 'RBERR', True),
    ('unauthorized_record_type', 'RBERR', True),
    ('unauthorized_source_organization', 'RBERR', True),

    ('invalid_metadata_file', 'MDERR', True),
    ('invalid_datatype_date', 'DTERR', True),
    ('invalid_datatype_language', 'DTERR', True),

    # The following are valid bags, and should not fail
    # ('no_metadata_file', '', ''),
    # ('empty_payload_directory', 'GBERR', True),
)

BAGINFO_FIELD_CHOICES = (
    ('source_organization', 'Source-Organization'),
    ('organization_address', 'Organization-Address'),
    ('contact_name', 'Contact-Name'),
    ('contact_phone', 'Contact-Phone'),
    ('contact_email', 'Contact-Email'),
    ('external_descripton', 'External-Description'),
    ('external_identifier', 'External-Identifier'),
    ('internal_sender_description', 'Internal-Sender-Description'),
    ('internal_sender_identifier', 'Internal-Sender-Identifier'),
    ('title', 'Title'),
    ('date_start', 'Date-Start'),
    ('date_end', 'Date-End'),
    ('record_creators', 'Record-Creators'),
    ('record_type', 'Record-Type'),
    ('language', 'Language'),
    ('bagging_date', 'Bagging-Date'),
    ('bag_group_identifier', 'Bag-Group-Identifier'),
    ('bag_count', 'Bag-Count'),
    ('bag_size', 'Bag-Size'),
    ('payload_oxum', 'Payload-Oxum'),
)

user_data = {'active': True, 'first_name': 'John', 'last_name': 'Doe', 'email':'test@example.org'}

org_data = {'active': True, 'name': 'Test Organization', 'acquisition_type': 'donation'}

# Variables and setup routines for RightsStatements

record_types = [
    "administrative records", "board materials",
    "communications and publications", "grant records",
    "annual reports"]
rights_bases = ['Copyright', 'Statute', 'License', 'Other']
basis_data = [
    {
        'rights_basis': 'Copyright',
        'applies_to_type': [1, ],
        'rightsstatementcopyright_set-INITIAL_FORMS': 0,
        'rightsstatementcopyright_set-TOTAL_FORMS': 1,
        'rightsstatementcopyright_set-0-copyright_note': "Test note",
        'rightsstatementcopyright_set-0-copyright_status': 'copyrighted',
        'rightsstatementcopyright_set-0-copyright_jurisdiction': 'us',
    },
    {
        'rights_basis': 'Statute',
        'applies_to_type': [1, ],
        'rightsstatementstatute_set-INITIAL_FORMS': 0,
        'rightsstatementstatute_set-TOTAL_FORMS': 1,
        'rightsstatementstatute_set-0-statute_note': "Test note",
        'rightsstatementstatute_set-0-statute_citation': 'Test statute citation',
        'rightsstatementstatute_set-0-statute_jurisdiction': 'us',
    },
    {
        'rights_basis': 'License',
        'applies_to_type': [1, ],
        'rightsstatementlicense_set-INITIAL_FORMS': 0,
        'rightsstatementlicense_set-TOTAL_FORMS': 1,
        'rightsstatementlicense_set-0-license_note': "Test note",
    },
    {
        'rights_basis': 'Other',
        'applies_to_type': [1, ],
        'rightsstatementother_set-INITIAL_FORMS': 0,
        'rightsstatementother_set-TOTAL_FORMS': 1,
        'rightsstatementother_set-0-other_rights_note': "Test note",
        'rightsstatementother_set-0-other_rights_basis': 'Donor',
    }
]
grant_data = {
    'rightsstatementrightsgranted_set-TOTAL_FORMS': 1,
    'rightsstatementrightsgranted_set-INITIAL_FORMS': 0,
    'rightsstatementrightsgranted_set-0-act': random.choice(['publish', 'disseminate', 'replicate', 'migrate', 'modify', 'use', 'delete']),
    'rightsstatementrightsgranted_set-0-restriction': random.choice(['allow', 'disallow', 'conditional']),
    'rightsstatementrightsgranted_set-0-rights_granted_note': 'Grant note'
}


def get_rights_basis_type(rights_statement):
    if rights_statement.rights_basis == 'Statute':
        return RightsStatementStatute
    elif rights_statement.rights_basis == 'Other':
        return RightsStatementOther
    elif rights_statement.rights_basis == 'Copyright':
        return RightsStatementCopyright
    elif rights_statement.rights_basis == 'License':
        return RightsStatementLicense
