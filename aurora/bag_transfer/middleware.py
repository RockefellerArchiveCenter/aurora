from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user

from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def get_user_jwt(request):
    user = get_user(request)
    if user.is_authenticated:
        return user
    try:
        user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
        if user_jwt is not None:
            request.csrf_processing_done = True
            return user_jwt[0]
    except Exception:
        pass
    return user


class AuthenticationMiddlewareJWT(MiddlewareMixin):
    """Checks for the presence of a JSON Web Token and, if found, authenticates
    using that token."""

    def process_request(self, request):
        assert hasattr(
            request, "session"
        ), "The Django authentication middleware requires session middleware to be installed. \
           Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        request.user = SimpleLazyObject(lambda: get_user_jwt(request))
