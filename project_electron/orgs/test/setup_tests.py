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
