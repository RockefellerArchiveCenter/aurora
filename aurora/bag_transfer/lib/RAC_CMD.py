from subprocess import CalledProcessError, check_output, STDOUT
import grp
import pwd


def set_server_password(user, password):
    command = "sudo usermod --password $(echo {} | openssl passwd -crypt -stdin) {}".format(
        password, user
    )
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        raise RuntimeError(
            "command '{}' returned with error (code {}): {}".format(
                e.cmd, e.returncode, e.output
            )
        )
    return True


def add_org(organization_machine_name):
    command = "sudo /usr/local/bin/RACaddorg {}".format(organization_machine_name)
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        raise RuntimeError(
            "command '{}' returned with error (code {}): {}".format(
                e.cmd, e.returncode, str(e.output)
            )
        )
    return True


def add_user(username):
    has_ERR = False
    home = "/home/{}".format(username)
    shell = "/bin/bash"
    command = "sudo useradd {} -d {} -m -g {} -s {}".format(
        username, home, "users", shell
    )
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print(
            "command '{}' returned with error (code {}): {}".format(
                e.cmd, e.returncode, str(e.output)
            )
        )
        if "Account created" in str(e.output):
            pass
        elif "already exists" in str(e.output):
            pass
        else:
            has_ERR = True
    return True if not has_ERR else False


def add2grp(organization_machine_name, machine_user_id):
    has_ERR = False
    command = "sudo usermod -a -G {} {}".format(
        organization_machine_name, machine_user_id
    )
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print(e.output)
        has_ERR = True
    return True if not has_ERR else False


def delete_system_group(organization_machine_name):
    has_ERR = False
    command = "groupdel {}".format(organization_machine_name)
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        print(e.output)
        has_ERR = True
    return not has_ERR


def del_from_org(machine_user_id):
    ugroups = [g for g in user_groups(machine_user_id)]
    has_ERR = False

    for group in ugroups:
        if group == "users":
            continue
        command = "sudo gpasswd -d {} {}".format(machine_user_id, group)
        try:
            output = check_output(command, shell=True, stderr=STDOUT)
        except CalledProcessError as e:
            print(e.output)
            has_ERR = True
    return True if not has_ERR else False


def user_groups(user):
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    gid = pwd.getpwnam(user).pw_gid
    groups.append(grp.getgrgid(gid).gr_name)
    return groups
