import sys
from subprocess import *
def add_org(org_name):
	command = ['sudo','-S','/usr/local/bin/RACaddorg', '{}'.format(org_name)]
	command = 'sudo -S /usr/local/bin/RACaddorg {}'.format(org_name)
	# proc = Popen(command, shell=True,stdout=PIPE,stdin=PIPE,stderr=STDOUT)
	try:
		out = check_output(command, shell=True,stderr=STDOUT)
	except CalledProcessError as e:
		raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
	

	# print out

	# output = []
	# while True:
	# 	data = proc.stdout.readline()
	# 	if len(data) == 0:
	# 		break
	# 	# sys.stdout.write(data)
	# 	output.append(data)
	# # proc.communicate('Deenell31')
	# print data
	return out