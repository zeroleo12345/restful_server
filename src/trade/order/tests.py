import pytest
# 第三方库
from rest_framework import status
# 自己的库
from trade.framework.unittest import get_user_and_token, UnitTestAPIClient

# 模块内全部测试案例可使用数据库设置:  https://pytest-django.readthedocs.io/en/latest/database.html
pytestmark = pytest.mark.django_db


def test_payjs_notify_success():
    user, token = get_user_and_token()
    client = UnitTestAPIClient(token=token)
    data = {
        'attach': ['{"tariff_id": "month1"}'], 'mchid': ['1511573911'], 'openid': ['o7LFAwUGHPZxyNahwjoNQtKh8EME'],
        'out_trade_no': ['1534167177710ovfltv6a8v7BsFAH0'], 'payjs_order_id': ['2018081321325600636471374'],
        'return_code': ['1'], 'time_end': ['2018-08-13 21:33:02'], 'total_fee': ['1'],
        'transaction_id': ['4200000149201808138100178561'], 'sign': ['3BB0F5C8843A16DEE422012A28CB3D47']
    }
    response = client.post('/order/notify', data=data, format=None)
    assert response.status_code == status.HTTP_200_OK


def test_payjs_notify_sign_error():
    user, token = get_user_and_token()
    client = UnitTestAPIClient(token=token)
    data = {
        'attach': ['{"tariff_id": "month1"}'], 'mchid': ['1511573911'], 'openid': ['o7LFAwUGHPZxyNahwjoNQtKh8EME'],
        'out_trade_no': ['1534167177710ovfltv6a8v7BsFAH0'], 'payjs_order_id': ['2018081321325600636471374'],
        'return_code': ['1'], 'time_end': ['2018-08-13 21:33:02'], 'total_fee': ['1'],
        'transaction_id': ['4200000149201808138100178561'], 'sign': ['this is error sign']
    }
    response = client.post('/order/notify', data=data, format=None)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_response = response.json()
    assert json_response['code'] == 'invalid_signature'
    assert 'message' in json_response
