from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings

from trade.framework.authorization import get_http_token_name
from trade.user.factories import UserFactory

# from rest_framework_jwt.utils import jwt_payload_handler
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER
JWT_AUTH_HEADER_PREFIX = api_settings.JWT_AUTH_HEADER_PREFIX


def get_user_and_token():
    user = UserFactory()
    payload = JWT_PAYLOAD_HANDLER(user)
    token = JWT_ENCODE_HANDLER(payload)
    return user, token


class UnitTestAPIClient(APIClient):
    def __init__(self, token=None):
        http_token = get_http_token_name()
        token = str(token) if token else None

        super().__init__(**{
            http_token: token
        })

    def post(self, *args, **kwargs):
        return super().post(format='json', *args, **kwargs)

    def put(self, *args, **kwargs):
        return super().put(format='json', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return super().patch(format='json', *args, **kwargs)
