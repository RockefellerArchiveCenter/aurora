from django.contrib.auth.models import Group
from subprocess import *

from bag_transfer.models import Organization, User, BagItProfile, BagItProfileBagInfo, BagItProfileBagInfoValues, ManifestsRequired, AcceptSerialization, AcceptBagItVersion, TagManifestsRequired, TagFilesRequired
from bag_transfer.rights.models import RightsStatement, RightsStatementCopyright, RightsStatementOther, RightsStatementRightsGranted, RecordType
from bag_transfer.lib.RAC_CMD import add_org, add_user
from aurora import settings

orgs = Organization.objects.all()
org_ids = []
DEFAULT_ORGS = [
    {
        "name": "Archival Repository",
        "acquisition_type": "donation"
    },
    {
        "name": "Donor Organization",
        "acquisition_type": "deposit"
    }
]
DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "password",
        "first_name": "System",
        "last_name": "Administrator",
        "superuser": True,
        "staff": True,
        "org": "Archival Repository"
    },
    {
        "username": "donor",
        "password": "password",
        "first_name": "Donor",
        "last_name": "Representative",
        "superuser": False,
        "staff": False,
        "org": "Donor Organization"
    },
    {
        "username": "manager",
        "password": "password",
        "first_name": "Managing",
        "last_name": "Archivist",
        "superuser": False,
        "staff": True,
        "groups": ["managing_archivists"],
        "org": "Archival Repository"
    },
    {
        "username": "appraiser",
        "password": "password",
        "first_name": "Appraisal",
        "last_name": "Archivist",
        "superuser": False,
        "staff": True,
        "groups": ["appraisal_archivists"],
        "org": "Archival Repository"
    },
    {
        "username": "accessioner",
        "password": "password",
        "first_name": "Accessioning",
        "last_name": "Archivist",
        "superuser": False,
        "staff": True,
        "groups": ["accessioning_archivists"],
        "org": "Archival Repository"
    }
]

print "Creating record types"
for type in ['administrative records', 'board materials', 'grant records',
             'communications and publications', 'annual reports']:
    RecordType.objects.get_or_create(name=type)

print "Creating organizations"
if len(orgs) == 0:
    for org in DEFAULT_ORGS:
        new_org = Organization.objects.create(name=org['name'], acquisition_type=org['acquisition_type'])
        archive_org = Organization.objects.get(name="Archival Repository")

        print "Creating BagIt Profile for {}".format(new_org)
        profile = BagItProfile.objects.create(
            applies_to_organization=new_org,
            source_organization=archive_org,
            external_description="Test BagIt Profile",
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
        source_organization = BagItProfileBagInfo.objects.get(field='source_organization', bagit_profile=profile)
        BagItProfileBagInfoValues.objects.create(
            bagit_profile_baginfo=source_organization,
            name=new_org.name
        )
        record_type = BagItProfileBagInfo.objects.get(field='record_type', bagit_profile=profile)
        for name in ['administrative records', 'board materials', 'grant records',
                     'communications and publications', 'annual reports']:
            BagItProfileBagInfoValues.objects.create(
                bagit_profile_baginfo=record_type,
                name=name
            )

        print "Creating Rights Statements for {}".format(new_org)
        copyright_statement = RightsStatement.objects.create(
            organization=new_org,
            rights_basis="Copyright",
        )
        for record_type in RecordType.objects.all():
            copyright_statement.applies_to_type.add(record_type)

        donor_statement = RightsStatement.objects.create(
            organization=new_org,
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
        new_user = User.objects.create_user(
            user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            email="{}@example.org".format(user['username']),
            is_superuser=user['superuser'],
            is_staff=user['staff'],
            organization=Organization.objects.get(name=user['org']))
        new_user.set_password(user['password'])
        if 'groups' in user:
            for group in user['groups']:
                g = Group.objects.get_or_create(name=group)[0]
                new_user.groups.add(g)
        new_user.save()
else:
    for user in User.objects.all():
        user.save()
