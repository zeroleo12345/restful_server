from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

from trade.user.models import User, Token


def get_http_token_name():
    return 'HTTP_88_TOKEN'


def get_authorization_header(request):
    http_token = get_http_token_name()
    key = request.META.get(http_token)
    if not key:
        raise exceptions.NotAuthenticated()
    return key


class TokenAuth(BaseAuthentication):
    def authenticate(self, request):
        key = get_authorization_header(request)

        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('token not exist')

        return token.user, token


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)
