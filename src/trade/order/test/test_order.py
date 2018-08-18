import pytest
# 第三方库
from rest_framework import status
# 自己的库
from trade.framework.unittest import get_user_and_token, UnitTestAPIClient

# 模块内全部测试案例可使用数据库设置:  https://pytest-django.readthedocs.io/en/latest/database.html
pytestmark = pytest.mark.django_db


def test_order_create():
    user, jwt_token = get_user_and_token()
    client = UnitTestAPIClient(token=jwt_token)
    data = {
        'tariff_name': 'month1',
    }
    response = client.post('/order', data=data)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response['code'] == 'ok'
    assert 'redirect_url' in json_response['data']
