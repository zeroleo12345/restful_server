from django.conf import settings
import pytest
from unittest.mock import MagicMock
from rest_framework import status
from trade.framework.unittest import get_token_and_user, UnitTestAPIClient
from trade.utils import mp

mp.create_mp_menu = MagicMock()


@pytest.mark.django_db
def test_user():
    # NOTE: pytest 里面的 settings.DEBUG = True
    settings.DEBUG = True
    token, user = get_token_and_user()
    client = UnitTestAPIClient(token=token)
    response = client.get('/user?code=001yROix1KtF1c0waVgx1k6Bix1yROiR')
    assert response.status_code == status.HTTP_200_OK

    res_dict = response.json()
    assert 'ok' == res_dict['code']
    assert 'uuid' in res_dict['data']
    assert 'openid' in res_dict['data']
    assert 'nickname' in res_dict['data']
    assert 'headimgurl' in res_dict['data']
    assert 'created_at' in res_dict['data']
    assert 'updated_at' in res_dict['data']
    assert 'username' in res_dict['data']
    assert 'is_enable' in res_dict['data']
    assert 'role' in res_dict['data']
