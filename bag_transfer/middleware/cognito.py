from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework.request import Request

from bag_transfer.authentication import (CognitoAppAuthentication,
                                         CognitoUserAuthentication)


class CognitoMiddleware(MiddlewareMixin):
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

        """Handle requests from Cognito Applications."""
        if request.headers.get('Accept') == 'application/json':
            request.user = self.get_application(request)

        """Handle requests from Cognito Users."""
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
            if CognitoUserAuthentication().authenticate(sso_client, request) is not None:
                redirect_uri = request.session.pop('redirect_uri', None)
                if redirect_uri is not None:
                    return redirect(redirect_uri)
                return redirect('app_home')

        if request.session.get('token', None) is not None:
            """Navigate to requested page."""
            if CognitoUserAuthentication().authenticate(sso_client, request) is not None:
                return self.get_response(request)

        """Initiate authorization."""
        request.session['redirect_uri'] = request.path
        return sso_client.authorize_redirect(request, settings.COGNITO_CLIENT['redirect_uri'])

    @staticmethod
    def clear_session(request):
        try:
            del request.session['user']
            del request.session['token']
        except KeyError:
            pass

    def get_application(self, request):
        application = CognitoAppAuthentication().authenticate(Request(request))
        if application is not None:
            request.csrf_processing_done = True
            return application[0]
        return application
