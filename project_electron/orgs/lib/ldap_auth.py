import ldap
import ldap.modlist as modlist

from aurora import config as CF

from orgs.transfers import RAC_CMD

class LDAP_Manager():



    def __init__(self):
        self.lconn = None
        self.__connected = False
        self.conn()

        self.users = []



    def conn(self):

        try:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            l = ldap.initialize(CF.AUTH_LDAP_SERVER_URI)
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            l.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
            l.set_option( ldap.OPT_X_TLS_DEMAND, True )
            l.set_option( ldap.OPT_DEBUG_LEVEL, 255 )
            l.simple_bind_s(CF.AUTH_LDAP_BIND_DN,CF.AUTH_LDAP_BIND_PASSWORD)
            self.lconn = l
            self.__connected = True
        except Exception as e:
            print e

    def get_all_users(self, unbind = True):
        if not self.__connected:
            return False
        results = []
        try:
            results = self.lconn.search_s(CF.LDAP_SEARCH_DN, ldap.SCOPE_SUBTREE)
        except Exception as e:
            print e
            return False
        if unbind:
            self.__unbind()

        for result in results[1:]:
            self.users.append(result[1]['uid'][0])
        return True

    def set_password(self, username, password):
        WAS_RESET = False
        try:
            results = self.lconn.passwd_s("uid={},ou=People,dc=ROCK,dc=org,dc=gke".format(username.strip()),None,password)
        except Exception as e:
            print e
        else:
            if type(result) is tuple:
                if not result[0] and not result[1]:
                    WAS_RESET = True
            # don't need to do anything cause will return false
        finally:
            self.__unbind()

        return WAS_RESET

    def create_user(self, org, email, full_name, last_name):
        """gets next LDAP id (org prefix + auto incr); creates user in system; adds user to grp"""
        if not self.__connected:
            return False

        # create user in ldap
        uid = self.__next_uid_increment()
        if not uid:
            print 'wasn\'t able to create UID'
            return False

        dn = "uid={},{}".format(uid, CF.LDAP_SEARCH_DN)
        attr = {
            "objectClass":  CF.LDAP_OBJECT_CLASSES,
            "uid":          [uid],
            "sn" :          [str(last_name)],
            "cn" :          [str(full_name)],
            "uidNumber":    [str(900000 + int(uid[len(CF.LDAP_UID_PREFIX):]))],
            "gidNumber":    CF.LDAP_GID_NUMBER,
            "userPassword": ["ractest1"],
            "homeDirectory":["na"],
            "mail":         [str(email)]
        }

        try:
            result = self.lconn.add_s(dn, modlist.addModlist(attr))
        except Exception as e:
            print e
            return False

        return uid if (RAC_CMD.add_user(uid) and RAC_CMD.add2grp(org, uid)) else False


    def __next_uid_increment(self):
        """return next incremental value based on XX00000 defined in config; run inside conn, doesn't bind or unbind"""
        if not self.__connected or not self.get_all_users(False):
            return False

        int_template = 5
        tar_users_ids = sorted([int(u[len(CF.LDAP_UID_PREFIX):]) for u in self.users if CF.LDAP_UID_PREFIX.lower() in u.lower()],reverse=True)

        if tar_users_ids[0] >= 99999:
            print "alert admin of limitation"
            return False
        next_increment_id = str(tar_users_ids[0] + 1)

        return "{}{}".format(CF.LDAP_UID_PREFIX.lower(), next_increment_id.zfill(int_template))

    def __unbind(self):
        self.lconn.unbind_s()
