from rest_framework.test import APIClient
from trade.user.auth import get_http_token_name
from trade.user.factories import UserFactory, TokenFactory


def get_token_and_user():
    user = UserFactory()
    token = TokenFactory(user=user)
    return token, user


class UnitTestAPIClient(APIClient):
    def __init__(self, token=None):
        super().__init__(**{
            get_http_token_name(): str(token) if token else None
        })

    def post(self, *args, **kwargs):
        return super().post(format='json', *args, **kwargs)

    def put(self, *args, **kwargs):
        return super().put(format='json', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return super().patch(format='json', *args, **kwargs)
