import ldap
from project_electron import config as CF

class LDAP_Manager():



    def __init__(self):
        self.lconn = None
        self.connected = False
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
            self.connected = True
        except Exception as e:
            print e

    def get_all_users(self):
        if not self.connected: 
            return False
        results = []
        try:
            results = self.lconn.search_s(CF.LDAP_SEARCH_DN, ldap.SCOPE_SUBTREE)
        except Exception as e:
            print e
            return False
        self.lconn.unbind_s()
        
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
            print result
            if type(result) is tuple:
                if not result[0] and not result[1]:
                    WAS_RESET = True
            # don't need to do anything cause will return false
        finally:
            self.lconn.unbind_s()

        return WAS_RESET


        
