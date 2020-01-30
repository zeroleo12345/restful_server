import pytest
# 第三方库
from django.conf import settings
from rest_framework import status
# 自己的库
from framework.unittest import UnitTestAPIClient
from models.factories.user import get_user_and_authorization

# 模块内测试案例需要使用数据库. 设置参考:  https://pytest-django.readthedocs.io/en/latest/database.html
pytestmark = pytest.mark.django_db


@pytest.mark.skipif(condition=settings.ENV.is_unittest(), reason="手动触发测试")
def test_order_create():
    user, authorization = get_user_and_authorization()
    client = UnitTestAPIClient(authorization=authorization)
    data = {
        'tariff_name': 'month1',
    }
    response = client.post('/order', data=data)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response['code'] == 'ok'

    jsapi_params = json_response['data']
    assert 'appId' in jsapi_params
    assert 'nonceStr' in jsapi_params
    assert 'package' in jsapi_params
    assert 'paySign' in jsapi_params
    assert 'signType' in jsapi_params
    assert 'timeStamp' in jsapi_params
