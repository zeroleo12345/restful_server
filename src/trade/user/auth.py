from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

from trade.framework import get_authorization_header
from trade.user.models import User, Token


class TokenAuth(BaseAuthentication):
    def authenticate(self, request):
        key = get_authorization_header(request)

        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('token not exist')

        return token.user, token


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)
