from unittest.mock import MagicMock
# 第三方库
from django.conf import settings
from rest_framework import status
import pytest
# 项目库
from framework.unittest import UnitTestAPIClient
from models.factories.user import UserFactory
from service.wechat.we_client import WeClient

WeClient.create_mp_menu = MagicMock()


@pytest.mark.django_db
class TestUser:

    @pytest.fixture(autouse=True)
    def setup_stuff(self, db):
        pass

    def test_new_user(self):
        settings.DEBUG = True
        client = UnitTestAPIClient()
        user, authorization = UserFactory.new_user_and_authorization(client)

    def test_user_resource_success(self):
        settings.DEBUG = True
        client = UnitTestAPIClient()
        user, authorization = UserFactory.new_user_and_authorization(client)
        #
        client = UnitTestAPIClient(authorization=authorization)
        response = client.get('/resource')
        assert response.status_code == status.HTTP_200_OK
