from django.contrib.auth.models import Group

from bag_transfer.models import Organization, User, BagItProfile, BagItProfileBagInfo, BagItProfileBagInfoValues, ManifestsRequired, AcceptSerialization, AcceptBagItVersion, TagManifestsRequired, TagFilesRequired
from bag_transfer.rights.models import RightsStatement, RightsStatementCopyright, RightsStatementOther, RightsStatementRightsGranted, RecordType
from bag_transfer.lib.RAC_CMD import add_org
from aurora import settings

orgs = Organization.objects.all()
org_ids = []
DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "password",
        "superuser": True,
        "staff": True,
    },
    {
        "username": "donor",
        "password": "password",
        "superuser": False,
        "staff": False,
    },
    {
        "username": "manager",
        "password": "password",
        "superuser": False,
        "staff": True,
        "groups": ["managing_archivists"],
    },
    {
        "username": "appraiser",
        "password": "password",
        "superuser": False,
        "staff": True,
        "groups": ["appraisal_archivists"],
    },
    {
        "username": "accessioner",
        "password": "password",
        "superuser": False,
        "staff": True,
        "groups": ["accessioning_archivists"],
    }
]

print "Creating organizations"
if len(orgs) == 0:
    Organization.objects.create(name="Test Organization", acquisition_type="donation")
    orgs = Organization.objects.all()

    print "Creating BagIt Profile for {}".format(orgs[0])
    profile = BagItProfile.objects.create(
        applies_to_organization=orgs[0],
        source_organization=orgs[0],
        external_descripton="Test BagIt Profile",
        contact_email="archive@example.org",
    )
    AcceptSerialization.objects.create(
        name='application/zip',
        bagit_profile=profile
    )
    AcceptSerialization.objects.create(
        name='application/x-tar',
        bagit_profile=profile
    )
    AcceptSerialization.objects.create(
        name='application/x-gzip',
        bagit_profile=profile
    )
    AcceptBagItVersion.objects.create(
        name='0.97',
        bagit_profile=profile
    )
    for field in ['external_identifier', 'internal_sender_description', 'title',
                  'date_start', 'date_end', 'bagging_date', 'payload_oxum',
                  'source_organization', 'record_type']:
        BagItProfileBagInfo.objects.create(
            bagit_profile=profile,
            field=field,
            required=True,
            repeatable=False
        )
    for field in ['record_creators', 'language']:
        BagItProfileBagInfo.objects.create(
            bagit_profile=profile,
            field=field,
            required=True,
            repeatable=True
        )
    for field in ['bag_count', 'bag_group_identifier']:
        BagItProfileBagInfo.objects.create(
            bagit_profile=profile,
            field=field,
            required=False,
            repeatable=False
        )
    source_organization = BagItProfileBagInfo.objects.get(field='source_organization')
    BagItProfileBagInfoValues.objects.create(
        bagit_profile_baginfo=source_organization,
        name='Test Organization'
    )
    record_type = BagItProfileBagInfo.objects.get(field='record_type')
    for name in ['administrative records', 'board materials', 'grant records',
                 'communications and publications', 'annual reports']:
        BagItProfileBagInfoValues.objects.create(
            bagit_profile_baginfo=record_type,
            name=name
        )

    for type in ['administrative records', 'board materials', 'grant records',
                 'communications and publications', 'annual reports']:
        RecordType.objects.get_or_create(name=type)

    print "Creating Rights Statements for {}".format(orgs[0])
    copyright_statement = RightsStatement.objects.create(
        organization=orgs[0],
        rights_basis="Copyright",
    )
    for record_type in RecordType.objects.all():
        copyright_statement.applies_to_type.add(record_type)

    donor_statement = RightsStatement.objects.create(
        organization=orgs[0],
        rights_basis="Other",
    )
    for record_type in RecordType.objects.all():
        donor_statement.applies_to_type.add(record_type)

    RightsStatementCopyright.objects.create(
        rights_statement=copyright_statement,
        copyright_status='copyrighted',
        copyright_end_date_period=40,
        copyright_note='Work for hire, under copyright until 40 years after creation.',
    )
    RightsStatementOther.objects.create(
        rights_statement=donor_statement,
        other_rights_basis='Donor',
        other_rights_end_date_period=10,
        other_rights_note='Records embargoed for 10 years after date of creation.',
    )
    RightsStatementRightsGranted.objects.create(
        rights_statement=copyright_statement,
        act='publish',
        end_date_period=40,
        rights_granted_note='Records under copyright may not be republished without permission from the copyright holder.',
        restriction='disallow',
    )
    RightsStatementRightsGranted.objects.create(
        rights_statement=donor_statement,
        act='disseminate',
        start_date_period=10,
        rights_granted_note='Records are open for research after expiration of embargo period.',
        restriction='allow',
    )
    RightsStatementRightsGranted.objects.create(
        rights_statement=donor_statement,
        act='disseminate',
        end_date_period=10,
        rights_granted_note='Records are open for research after expiration of embargo period.',
        restriction='disallow',
    )
else:
    for org in orgs:
        org_ids.append(org.machine_name[3:])

    org_ids = sorted(org_ids, key=int)

    for i in range(int(org_ids[-1])):
        org_to_add = 'placeholder org'
        org_id = "org{}".format(i+1)
        if str(i+1) in org_ids:
            for org in orgs:
                if org_id == org.machine_name:
                    org_to_add = org.name
        add_org(org_to_add)

if len(User.objects.all()) == 0:
    print "Creating users"
    for user in DEFAULT_USERS:
        new_user = User.objects.create_user(user['username'], password=user['password'])
        new_user.is_superuser = user['superuser']
        new_user.is_staff = user['staff']
        new_user.organization = orgs[0]
        if 'groups' in user:
            for group in user['groups']:
                g = Group.objects.get_or_create(name=group)[0]
                new_user.groups.add(g)
        new_user.save()
