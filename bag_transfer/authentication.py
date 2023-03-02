import requests
from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
from django.conf import settings
from django.contrib.auth import login
from django.core.cache import cache
from jose import jwt
from rest_framework import authentication, exceptions

from .models import Application, User


class CognitoAppAuthentication(authentication.BaseAuthentication):
    """Ensures AWS Cognito is used to log in other applications using the API."""

    def authenticate(self, request):
        """Main method which returns authenticated Application."""
        if request.headers.get('Accept') == 'application/json':
            return (self.get_application(request), None)

    def get_application(self, request):
        token = self.get_auth_token(request)
        try:
            claims = self.get_claims(token)
            if len(claims) > 0:
                application = Application.objects.get(client_id=claims['client_id'])
                application.is_authenticated = True
                application.save()
                return application
            raise exceptions.AuthenticationFailed("The authentication token does not have claims associated with it.")
        except Application.DoesNotExist:
            raise exceptions.AuthenticationFailed("The application associated with this token does not exist.")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"The authentication token provided is invalid. {e}")

    def get_auth_token(self, request):
        try:
            auth_header = request.META["HTTP_AUTHORIZATION"]
            bearer, _, token = auth_header.partition(' ')
            if bearer != 'Bearer':
                raise ValueError('Invalid token')
            return token
        except KeyError:
            raise exceptions.AuthenticationFailed('Expected an Authorization header but got none.')

    @staticmethod
    def _fetch_cognito_keys():
        jwks = requests.get(settings.COGNITO_CLIENT['jwks_url']).json()
        cache.set('jwks', jwks, timeout=None)
        return jwks

    def get_claims(self, token):
        jwks = cache.get('jwks', None) or self._fetch_cognito_keys()
        headers = jwt.get_unverified_header(token)

        for key in jwks['keys']:
            if key['kid'] == headers['kid']:
                rsa_key = key
                alg = key['alg']

        if not rsa_key:
            print('No correct keys found to decode the auth payload!')
            cache.delete('jwks')
            return []

        return jwt.decode(
            token,
            rsa_key,
            audience=settings.COGNITO_CLIENT['client_id'],
            algorithms=[alg])


class CognitoUserAuthentication(authentication.BaseAuthentication):

    def authenticate(self, sso_client, request):
        """Fetches user information from Cognito and logs the matching user in."""
        token = request.session.get('token', None)
        if token is None or 'access_token' not in token:
            return None

        if not OAuth2Token.from_dict(token).is_expired() and 'user' in request.session:
            return request.session['user']

        try:
            res = sso_client.get(settings.COGNITO_CLIENT['userinfo_endpoint'], token=OAuth2Token(token))
            if res.ok:
                user_data = res.json()
                user = User.objects.get(username=user_data['username'], email=user_data['email'])
                if not (request.user == user) or not (user.is_authenticated):
                    user.token = request.session['token']
                    user.save()
                    login(request, user)
                return user_data
        except OAuthError as e:
            print(e)
        return None
