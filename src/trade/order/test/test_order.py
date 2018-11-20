import pytest
# 第三方库
from django.conf import settings
from rest_framework import status
# 自己的库
from trade.framework.unittest import get_user_and_token, UnitTestAPIClient

# 模块内测试案例需要使用数据库. 设置参考:  https://pytest-django.readthedocs.io/en/latest/database.html
pytestmark = pytest.mark.django_db


@pytest.mark.skipif(condition=settings.ENVIRONMENT.is_unittest(), reason="手动触发测试")
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

    wepay_params = json_response['data']
    assert 'appId' in wepay_params
    assert 'nonceStr' in wepay_params
    assert 'package' in wepay_params
    assert 'paySign' in wepay_params
    assert 'signType' in wepay_params
    assert 'timeStamp' in wepay_params
