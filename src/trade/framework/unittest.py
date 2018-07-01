from rest_framework.test import APIClient

from trade.user.factories import UserFactory
from trade.framework.authorization import JWTAuthentication


def get_user_and_token():
    user = UserFactory()
    token = JWTAuthentication.jwt_encode_handler(user)
    return user, token


class UnitTestAPIClient(APIClient):
    def __init__(self, token=None):
        http_token = 'HTTP_AUTHORIZATION'
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
