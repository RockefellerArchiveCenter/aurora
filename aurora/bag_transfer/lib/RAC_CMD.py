import sys
from subprocess import *
import grp, pwd


def add_org(organization_machine_name):
    command = 'sudo sh /usr/local/bin/RACaddorg {}'.format(organization_machine_name)
    output = None
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        raise RuntimeError("command '{}' returned with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    return True


def add_user(username):
    # try add user
    has_ERR = False
    home = '/home/{}'.format(username)
    shell = '/bin/bash'
    command = 'useradd {} -d {} -m -g {} -s {}'.format(username, home, 'users', shell)
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print "command '{}' returned with error (code {}): {}".format(e.cmd, e.returncode, e.output)
        # error codes not isolated..
        if 'Account created' in e.output:
            pass
        elif 'already exists' in e.output:
            pass
        else:
            has_ERR = True
        # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode,e.output))

    return (True if not has_ERR else False)


def add2grp(organization_machine_name, machine_user_id):
    has_ERR = False
    command = 'usermod -G {} {}'.format(organization_machine_name, machine_user_id)

    output = None
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print e.output
        has_ERR = True
    return (True if not has_ERR else False)


def delete_system_group(organization_machine_name):
    has_ERR = False
    command = 'groupdel {}'.format(organization_machine_name)
    output = None
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print e.output
        has_ERR = True
    return not has_ERR


def del_from_org(machine_user_id):
    ugroups = [g for g in user_groups(machine_user_id)]
    has_ERR = False

    for group in ugroups:

        command = 'gpasswd -d $1 $2 {} {}'.format(machine_user_id,group)

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
