from orgs.backend import RACLDAPBackend
from django_auth_ldap.backend import _LDAPUser
from orgs.lib.ldap_auth import LDAP_Manager

class _LDAPUserExtension(RACLDAPBackend):
	def set_password(self, username, password):
		ldap_man = LDAP_Manager()
		return ldap_man.set_password(username,password)
