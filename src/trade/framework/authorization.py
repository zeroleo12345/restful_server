from datetime import datetime, timedelta
from calendar import timegm
# 第三方库
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.settings import APISettings
import jwt
# 项目库
from trade import settings
from trade.framework.exception import GlobalException

jwt_settings = APISettings(user_settings=settings.JWT_AUTH, defaults=settings.JWT_AUTH)


# 收到请求时, 先验证 Token, 再验证 Users
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.META.get('HTTP_AUTHORIZATION')
        if not authorization:
            raise exceptions.NotAuthenticated()

        user = self.authenticate_credentials(authorization)

        return user, authorization

    @staticmethod
    def authenticate_credentials(jwt_token, verify_exp=True):
        """
        :param jwt_token: 解密后的字典
        :param verify_exp: 是否校验失效时间
        :return: user_dict: Users Model Serializer's data.
        """
        user = JWTAuthentication.jwt_decode_handler(jwt_token, verify_exp)
        user_dict = user['user']
        return user_dict

    @staticmethod
    def jwt_decode_handler(jwt_token, verify_exp=True):
        """
        :param jwt_token: JWT Token String
        :param verify_exp: 是否校验失效时间
        :return: user_dict: Users Model Serializer's data.
        """
        options = {}
        if verify_exp:
            options['verify_exp'] = True
        else:
            options['verify_exp'] = False
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
            raise GlobalException({'code': 'authentication_failed', 'message': '认证凭证已失效, 请刷新'}, status=200)
        except jwt.DecodeError:
            raise GlobalException({'code': 'authentication_failed', 'message': '认证凭证解码错误'}, status=401)
        except jwt.InvalidTokenError:
            raise GlobalException({'code': 'authentication_failed', 'message': '认证凭证头校验错误'}, status=401)

        return payload

    @staticmethod
    def jwt_encode_handler(user_dict, exp=jwt_settings.JWT_EXPIRATION_DELTA):
        """
        :param user_dict: Users Model Serializer's data. like: UserSerializer(user).data
        :param exp: 失效秒数. <class 'datetime.timedelta'>
        :return: JWT Token String
        """
        assert isinstance(exp, timedelta)
        #
        payload = {
            'user': user_dict,
            'exp': datetime.utcnow() + exp,
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


# 收到请求时, 先验证 Token, 再验证 Users, 不强制要求登陆
class JWTNoAuthentication(JWTAuthentication):
    def authenticate(self, request):
        authorization = request.META.get('HTTP_AUTHORIZATION')
        user = self.authenticate_credentials(authorization)

        return user, authorization

    @staticmethod
    def authenticate_credentials(jwt_token):
        """
        :param jwt_token: 解密后的字典
        :return: user_dict: Users Model Serializer's data.
        """
        user_dict = {}
        if jwt_token:
            user = JWTAuthentication.jwt_decode_handler(jwt_token)
            user_dict = user['user']
        return user_dict
