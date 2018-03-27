import string
import random

from orgs.models import Organization

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

def create_rand_name(p1,p3):
	return "{} {} {}".format(
		p1[random.randrange(len(p1))],
		random.choice(string.letters),
		p3[random.randrange(len(p3))]
	)

def create_test_orgs(org_count=TEST_ORG_COUNT):
	"""creates random orgs based on org_count"""
	if org_count < 1:
		return False

	generated_orgs = []
	while True:
		if len(generated_orgs) == org_count:
			break
		new_org_name = create_rand_name(POTUS_NAMES,COMPANY_SUFFIX)
		try:
			org_exist = Organization.objects.get(name=new_org_name)
			continue
		except Organization.DoesNotExist as e:
			pass
		
		test_org = Organization(
			name = new_org_name,
			machine_name = 'org{}'.format((len(generated_orgs)+1))
		)
		test_org.save()
		generated_orgs.append(test_org)

		print 'Test organization {} -- {} created'.format(test_org.name,test_org.machine_name)

	return generated_orgs
		

def delete_test_orgs(orgs = []):
	for org in orgs:
		org.delete()