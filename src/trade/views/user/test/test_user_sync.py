from unittest.mock import MagicMock
# 第三方库
from rest_framework import status
import pytest
# 项目库
import settings
from framework.unittest import UnitTestAPIClient
from trade.models.factories import UserFactory
from service.wechat.we_client import WeClient

WeClient.create_mp_menu = MagicMock()


@pytest.mark.django_db
class TestUser:

    @pytest.fixture(autouse=True)
    def setup_stuff(self, db):
        pass

    def test_user_sync(self):
        settings.DEBUG = True
        client = UnitTestAPIClient()
        user, authorization = UserFactory.new_user_and_authorization(client)
        client = UnitTestAPIClient(authorization=authorization)
        response = client.get('/user/sync')
        assert response.status_code == status.HTTP_200_OK

        user0 = response.json()['data'][0]
        assert 'expired_at' in user0
        assert 'username' in user0
        assert 'password' in user0
