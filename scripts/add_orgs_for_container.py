from orgs.models import Organization
from transfer_app.RAC_CMD import add_org
orgs = Organization.objects.all()
org_ids = []
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
