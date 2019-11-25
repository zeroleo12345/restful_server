from unittest.mock import MagicMock
# 第三方库
from django.conf import settings
from rest_framework import status
import pytest
# 自己的库
from trade.resource.factories import ResourceFactory
from trade.framework.unittest import get_user_and_token, UnitTestAPIClient
from trade.utils.mp import WechatPlatform

WechatPlatform.create_mp_menu = MagicMock()


@pytest.mark.django_db
class TestUser:

    @pytest.fixture(autouse=True)
    def setup_stuff(self, db):
        pass

    def test_user_sync(self):
        settings.DEBUG = True
        user, token = get_user_and_token()
        ResourceFactory(user=user)

        client = UnitTestAPIClient(token=token)
        response = client.get('/user/sync')
        assert response.status_code == status.HTTP_200_OK

        user0 = response.json()['data'][0]
        assert 'expired_at' in user0
        assert 'username' in user0
        assert 'password' in user0
