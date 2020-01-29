from unittest.mock import MagicMock
# 第三方库
from django.conf import settings
from rest_framework import status
import pytest
# 自己的库
from models.factories.resource import ResourceFactory
from trade.framework.unittest import UnitTestAPIClient
from models.factories.user import get_user_and_authorization
from service.wechat.we_client import WeClient

WeClient.create_mp_menu = MagicMock()


@pytest.mark.django_db
class TestUser:

    @pytest.fixture(autouse=True)
    def setup_stuff(self, db):
        pass

    def test_user_sync(self):
        settings.DEBUG = True
        user, authorization = get_user_and_authorization()
        ResourceFactory(user=user)

        client = UnitTestAPIClient(authorization=authorization)
        response = client.get('/user/sync')
        assert response.status_code == status.HTTP_200_OK

        user0 = response.json()['data'][0]
        assert 'expired_at' in user0
        assert 'username' in user0
        assert 'password' in user0
