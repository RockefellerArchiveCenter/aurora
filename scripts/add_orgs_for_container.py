from bag_transfer.models import Organization, User
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
    },
    {
        "username": "appraiser",
        "password": "password",
        "superuser": False,
        "staff": True,
    },
    {
        "username": "accessioner",
        "password": "password",
        "superuser": False,
        "staff": True,
    }
]

if len(orgs) == 0:
    Organization.objects.create(name="Test Organization")
    orgs = Organization.objects.all()
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
    print "Creating Users"
    for user in DEFAULT_USERS:
        new_user = User.objects.create_user(user['username'], password=user['password'])
        new_user.is_superuser = user['superuser']
        new_user.is_staff = user['staff']
        new_user.organization = orgs[0]
        new_user.save()
