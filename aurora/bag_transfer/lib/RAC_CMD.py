import sys
from subprocess import *
import grp, pwd


def add_org(org_name):
    command = 'sudo sh /usr/local/bin/RACaddorg {}'.format(org_name)

    output = None
    try:
        output = check_output(command, shell=True,stderr=STDOUT)
    except CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    if output is not None:

        for line in output.split('\n'):
            if line.startswith('org='):
                orgname = line[4:].strip()
                print orgname
                # check server for actual dir location for 2nd validation

                return (1, orgname)
    return (0, '')


def add_user(machine_user_id):
    # try add user
    has_ERR = False
    command = 'sudo /usr/local/bin/RACcreateuser {}'.format(machine_user_id)
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print "command '{}' return with error (code {}): {}".format(e.cmd, e.returncode,e.output)
        # error codes not isolated..
        if 'Account created' in e.output:
            pass
        elif 'already exists' in e.output:
            pass
        else:
            has_ERR = True
        # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode,e.output))

    return (True if not has_ERR else False)

    # possible check next account exist in LDAP


def add2grp(organization_machine_name, machine_user_id):
    has_ERR = False
    command = 'sudo /usr/local/bin/RACadd2grp {} {}'.format(organization_machine_name, machine_user_id)

    output = None
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print e.output
        has_ERR = True
    return (True if not has_ERR else False)


def delete_system_group(organization_machine_name):
    if not organization_machine_name.startswith('org'):
        return False
    has_ERR = False
    command = 'sudo sh /usr/local/bin/RACdelorg {}'.format(organization_machine_name)
    output = None
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print e.output
        has_ERR = True
    return not has_ERR


def del_from_org(machine_user_id):
    ugroups = [g for g in user_groups(machine_user_id) if g[:3] == "org"]
    has_ERR = False

    for group in ugroups:

        command = 'sudo sh /usr/local/bin/RACdelfromorg {} {}'.format(machine_user_id,group)

        output = None
        try:
            output = check_output(command, shell=True, stderr=STDOUT)
        except CalledProcessError as e:
            print e
            print e.output
            has_ERR = True
    return (True if not has_ERR else False)


def user_groups(user):
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    gid = pwd.getpwnam(user).pw_gid
    groups.append(grp.getgrgid(gid).gr_name)
    return groups
