from unittest.mock import MagicMock
# 第三方库
from django.conf import settings
from rest_framework import status
import pytest
# 项目库
from framework.unittest import UnitTestAPIClient
from models.factories.user import get_user_and_authorization
from service.wechat.we_client import WeClient

WeClient.create_mp_menu = MagicMock()


@pytest.mark.django_db
class TestUser:

    @pytest.fixture(autouse=True)
    def setup_stuff(self, db):
        pass

    def test_user_with_token(self):
        settings.DEBUG = True
        user, authorization = get_user_and_authorization()
        client = UnitTestAPIClient(authorization=authorization)
        response = client.get('/user?code=001yROix1KtF1c0waVgx1k6Bix1yROiR')
        assert response.status_code == status.HTTP_200_OK

        res_dict = response.json()
        assert 'ok' == res_dict['code']
        assert 'openid' in res_dict['data']['user']['weixin']
        assert 'nickname' in res_dict['data']['user']['weixin']
        assert 'headimgurl' in res_dict['data']['user']['weixin']
        assert 'created_at' in res_dict['data']['user']['weixin']
        assert 'username' in res_dict['data']['user']
        assert 'is_enable' in res_dict['data']['user']
        assert 'role' in res_dict['data']['user']

    def test_user_without_token(self):
        settings.DEBUG = True
        # httpClient 没有 authorization
        client = UnitTestAPIClient()
        response = client.get('/user?code=001yROix1KtF1c0waVgx1k6Bix1yROiR')
        assert response.status_code == status.HTTP_200_OK

        res_dict = response.json()
        assert 'ok' == res_dict['code']
        assert 'openid' in res_dict['data']['user']['weixin']
        assert 'nickname' in res_dict['data']['user']['weixin']
        assert 'headimgurl' in res_dict['data']['user']['weixin']
        assert 'created_at' in res_dict['data']['user']['weixin']
        assert 'username' in res_dict['data']['user']
        assert 'is_enable' in res_dict['data']['user']
        assert 'role' in res_dict['data']['user']
        # assert response.has_header('Authorization')

    def test_user_resource_success(self):
        settings.DEBUG = True
        user, authorization = get_user_and_authorization()
        client = UnitTestAPIClient(authorization=authorization)
        response = client.get('/resource')
        assert response.status_code == status.HTTP_200_OK
