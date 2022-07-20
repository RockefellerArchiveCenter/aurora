from authlib.integrations.base_client import OAuthError
from authlib.integrations.django_client import OAuth
from authlib.oauth2.rfc6749 import OAuth2Token
from django.contrib.auth import login
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from aurora import settings
from bag_transfer.models import User


class CognitoMiddleware(MiddlewareMixin):
    """Ensures OAuth is used to log in users.

    Taken from https://songrgg.github.io/programming/django-oauth-client-setup/
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.oauth = OAuth()

    def process_request(self, request):
        """Handles main OAuth flow."""
        def update_token(token, refresh_token, access_token):
            request.session['token'] = token
            return None

        sso_client = self.oauth.register(
            'cognito', overwrite=True, **settings.COGNITO_CLIENT, update_token=update_token
        )

        if request.path in settings.COGNITO_CLIENT_CALLBACK_URL:
            self.clear_session(request)
            request.session['token'] = sso_client.authorize_access_token(request)
            if self.get_current_user(sso_client, request) is not None:
                redirect_uri = request.session.pop('redirect_uri', None)
                if redirect_uri is not None:
                    return redirect(redirect_uri)
                return redirect('app_home')

        if request.session.get('token', None) is not None:
            current_user = self.get_current_user(sso_client, request)
            if current_user is not None:
                return self.get_response(request)

        # remember redirect URI for redirecting to the original URL.
        request.session['redirect_uri'] = request.path
        return sso_client.authorize_redirect(request, settings.COGNITO_CLIENT['redirect_uri'])

    @staticmethod
    def get_current_user(sso_client, request):
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
                if not user.is_authenticated:
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
