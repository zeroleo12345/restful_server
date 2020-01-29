from datetime import datetime
from calendar import timegm

from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.settings import APISettings
import jwt

from models.models import User
from trade.user.serializer import UserWeixinSerializer

jwt_settings = APISettings(user_settings=settings.JWT_AUTH, defaults=settings.JWT_AUTH)


# 收到请求时, 先验证 Token, 再验证 User
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            raise exceptions.NotAuthenticated()

        user = self.authenticate_credentials(token)

        return user, token

    def authenticate_credentials(self, jwt_token):
        """
        :param jwt_token: 解密后的字典
        :return: User Model
        """
        user = JWTAuthentication.jwt_decode_handler(jwt_token)
        return user

    @staticmethod
    def jwt_decode_handler(jwt_token):
        """
        :param jwt_token: JWT Token String
        :return: User Model
        """
        options = {
            'verify_exp': jwt_settings.JWT_VERIFY_EXPIRATION,
        }
        try:
            payload = jwt.decode(
                jwt_token,
                jwt_settings.JWT_PUBLIC_KEY or jwt_settings.JWT_SECRET_KEY,
                jwt_settings.JWT_VERIFY,
                options=options,
                leeway=jwt_settings.JWT_LEEWAY,
                audience=jwt_settings.JWT_AUDIENCE,
                issuer=jwt_settings.JWT_ISSUER,
                algorithms=[jwt_settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignature:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding signature.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid Token.')

        username = payload['user']['username']
        user = User.objects.filter(username=username).select_related('weixin').first()
        return user

    @staticmethod
    def jwt_encode_handler(user):
        """
        :param user: User Model
        :return: JWT Token String
        """
        payload = {
            'user': UserWeixinSerializer(user).data,
            'exp': datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA
        }

        # Include original issued at time for a brand new token, to allow token refresh
        if jwt_settings.JWT_ALLOW_REFRESH:
            payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
            )

        if jwt_settings.JWT_AUDIENCE is not None:
            payload['aud'] = jwt_settings.JWT_AUDIENCE

        if jwt_settings.JWT_ISSUER is not None:
            payload['iss'] = jwt_settings.JWT_ISSUER

        key = jwt_settings.JWT_PRIVATE_KEY or jwt_settings.JWT_SECRET_KEY
        return jwt.encode(
            payload,
            key,
            jwt_settings.JWT_ALGORITHM
        ).decode('utf-8')


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)

    @staticmethod
    def is_user(user):
        return isinstance(user, User)
