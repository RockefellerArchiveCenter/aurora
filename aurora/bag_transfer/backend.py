from django_auth_ldap.backend import LDAPBackend, _LDAPUser
from django.contrib.auth import get_user_model
from bag_transfer.models import User

class RACLDAPBackend(LDAPBackend):
    """ A custom LDAP authentication backend """



    def authenticate(self, request=None, username=None, password=None, **kwargs):
        if bool(password) or self.settings.PERMIT_EMPTY_PASSWORD:

            # IF not authorized by RAC
            try:
                user_record = User.objects.get(username=username)
            except Exception as e:
                print e
                print 'trying to sign in from ldap without RAC Authorization'
                return None

            ldap_user = _LDAPUser(self, username=username.strip())
            user = ldap_user.authenticate(password)
        else:
            # logger.debug('Rejecting empty password for %s' % username)
            user = None

        return user

    def get_or_create_user(self, username, ldap_user):
        """
        This must return a (User, created) 2-tuple for the given LDAP user.
        username is the Django-friendly username of the user. ldap_user.dn is
        the user's DN and ldap_user.attrs contains all of their LDAP attributes.
        """
        model = self.get_user_model()
        username_field = getattr(model, 'USERNAME_FIELD', 'username')

        kwargs = {
            username_field + '__iexact': username,
            'defaults': {username_field: username.lower(), 'from_ldap': True}
        }

        return model.objects.get_or_create(**kwargs)
