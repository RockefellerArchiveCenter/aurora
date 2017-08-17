import os
def add_org(org_name):
	# os.setuid(1000)
	return os.popen("sudo -S  sh /usr/local/bin/RACaddorg {}".format(org_name), 'w').write("Deenell31")