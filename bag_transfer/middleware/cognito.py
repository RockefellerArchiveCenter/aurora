import requests
from authlib.integrations.base_client import OAuthError
from authlib.integrations.django_client import OAuth
from authlib.oauth2.rfc6749 import OAuth2Token
from django.conf import settings
from django.contrib.auth import login, logout
from django.core.cache import cache
from django.shortcuts import redirect, reverse
from django.utils.deprecation import MiddlewareMixin
from jose import jwt

from bag_transfer.models import Application, User


class CognitoUserMiddleware(MiddlewareMixin):
    """Ensures AWS Cognito is used to log in users.

    Taken from https://songrgg.github.io/programming/django-oauth-client-setup/
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.oauth = OAuth()

    def process_request(self, request):
        """Handles OAuth flow.

        Unauthenticated requests are redirected to Cognito login page, which
        returns a token to the configured COGNITO_CLIENT_CALLBACK_URL. This
        token is then parsed and the current user is set in the request.session
        and the token is saved to the authenticated user's model instance.
        """
        def update_token(token, refresh_token, access_token):
            request.session['token'] = token
            return None

        if request.user and not request.user.is_anonymous:
            return self.get_response(request)

        sso_client = self.oauth.register(
            'cognito',
            overwrite=True,
            **settings.COGNITO_CLIENT,
            update_token=update_token)

        if request.path == "/":
            """Redirect requests to root to the application home page."""
            return redirect("app_home")

        if request.path in settings.COGNITO_CLIENT_CALLBACK_URL:
            """Handle OAuth callback."""
            self.clear_session(request)
            request.session['token'] = sso_client.authorize_access_token(request)
            if self.get_current_user(sso_client, request) is not None:
                redirect_uri = request.session.pop('redirect_uri', None)
                if redirect_uri is not None:
                    return redirect(redirect_uri)
                return redirect('app_home')

        if request.path == "/logout/":
            """Handle logout requests."""
            self.clear_session(request)
            logout(request)
            return redirect(f"{settings.COGNITO_CLIENT['api_base_url']}/logout?client_id={settings.COGNITO_CLIENT['client_id']}&logout_uri={request.build_absolute_uri(reverse('app_home'))}")

        if request.session.get('token', None) is not None:
            """Navigate to requested page."""
            current_user = self.get_current_user(sso_client, request)
            if current_user is not None:
                return self.get_response(request)

        """Initiate authorization."""
        request.session['redirect_uri'] = request.path
        return sso_client.authorize_redirect(request, settings.COGNITO_CLIENT['redirect_uri'])

    def get_current_user(self, sso_client, request):
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

    @staticmethod
    def clear_session(request):
        try:
            del request.session['user']
            del request.session['token']
        except KeyError:
            pass


class CognitoAppMiddleware(MiddlewareMixin):

    def process_request(self, request):
        assert hasattr(
            request, "session"
        ), "The Django authentication middleware requires session middleware to be installed. \
           Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        if "api" in request.path and request.headers.get('Accept') == 'application/json':
            request.user = self.get_application(request)

    def get_application(self, request):
        """Ensures AWS Cognito is used to log in other applications using the API."""
        token = self.get_auth_token(request)
        try:
            claims = self.get_claims(token)
            if len(claims) > 0:
                application = Application.objects.get(client_id=claims['client_id'])
                application.is_authenticated = True
                application.save()
                return application
            raise Exception("The authentication token does not have claims associated with it.")
        except Application.DoesNotExist:
            raise Exception("The application associated with this token does not exist.")
        except Exception as e:
            raise Exception(f"The authentication token provided is invalid. {e}")

    def get_auth_token(self, request):
        try:
            auth_header = request.META["HTTP_AUTHORIZATION"]
            bearer, _, token = auth_header.partition(' ')
            if bearer != 'Bearer':
                raise ValueError('Invalid token')
            return token
        except KeyError:
            raise Exception('Expected an Authorization header but got none.')

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
