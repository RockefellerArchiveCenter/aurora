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

user_data = {'active': True, 'first_name': 'John', 'last_name': 'Doe', 'email':'test@example.org'}

org_data = {'active': True, 'name': 'Test Organization', 'acquisition_type': 'donation'}

views = {
    'all': {
        'list': [],
        'org': [],
        'archive': [],
        'rights': [],
        'profiles': [],
    }
    'donor': {
        'list': [],
        'org': [],
        'archive': [],
        'rights': [],
        'profiles': [],
    }
    'managing_archivists': {
        'list': [],
        'org': [],
        'archive': [],
        'rights': [],
        'profiles': [],
    }
    'accessioning_archivists': {
        'list': [],
        'org': [],
        'archive': [],
        'rights': [],
        'profiles': [],
    }
    'appraisal_archivists': {
        'list': [],
        'org': [],
        'archive': [],
        'rights': [],
        'profiles': [],
    }
}
