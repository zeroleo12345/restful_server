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

    def post(self, path, data=None, format='json', *args, **kwargs):
        """
        :param path:
        :param data:
        :param format:
             json - request.data.get
             None - request.POST.get
        :return:
        """
        return super().post(path, data, format=format, *args, **kwargs)

    def put(self, path, data=None, format='json', *args, **kwargs):
        return super().put(path, data=None, format=format, *args, **kwargs)

    def patch(self, path, data=None, format='json', *args, **kwargs):
        return super().patch(path, data, format=format, *args, **kwargs)
