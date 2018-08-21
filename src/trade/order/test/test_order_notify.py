import pytest
# 第三方库
from rest_framework import status
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
# 自己的库
from trade.framework.unittest import get_user_and_token, UnitTestAPIClient
from trade.order.factories import OrdersFactory

# 使全部测试案例能用数据库, 参考:  https://pytest-django.readthedocs.io/en/latest/database.html
pytestmark = pytest.mark.django_db


def test_payjs_notify_success():
    user, token = get_user_and_token()
    data = {
        'attach': '{"tariff_name": "month1"}', 'mchid': '1511573911', 'openid': 'o7LFAwUGHPZxyNahwjoNQtKh8EME',
        'out_trade_no': '1534167177710ovfltv6a8v7BsFAH0', 'payjs_order_id': '2018081321325600636471374',
        'return_code': '1', 'time_end': '2018-08-13 21:33:02', 'total_fee': '1',
        'transaction_id': '4200000149201808138100178561', 'sign': '061BC78497952DB19B3F337760A95647'
    }
    # 插入订单
    OrdersFactory(
        user=user,
        openid=user.weixin.openid,
        out_trade_no=data['out_trade_no'],
        attach=data['attach'],
        transaction_id=data['transaction_id'],
        total_fee=data['total_fee'],
        mch_id=data['mchid'],
        status='unpaid',
    )

    # 充值状态通知
    client = UnitTestAPIClient(token=token)
    response = client.post('/order/notify', data=data, format=None)
    assert response.status_code == status.HTTP_200_OK

    # 检查用户时长是否已经叠加
    response = client.get('/resource')
    assert response.status_code == status.HTTP_200_OK
    """
    {
        'code': 'ok', 'data': {
            'id': 1, 'status': 'working', 'expired_at': '2018-09-18T12:28:50.649466+08:00',
            'updated_at': '2018-08-18T12:28:50.650826+08:00'
         }
    }
    """
    json_resposne = response.json()
    assert json_resposne['data']['status'] == 'working'
    expired_at = timezone.localtime(parse_datetime(json_resposne['data']['expired_at']))
    assert expired_at >= timezone.localtime() + relativedelta(months=1) - relativedelta(hours=1)


def test_payjs_notify_order_not_exist():
    user, token = get_user_and_token()
    data = {
        'attach': '{"tariff_name": "month1"}', 'mchid': '1511573911', 'openid': 'o7LFAwUGHPZxyNahwjoNQtKh8EME',
        'out_trade_no': '1534167177710ovfltv6a8v7BsFAH0', 'payjs_order_id': '2018081321325600636471374',
        'return_code': '1', 'time_end': '2018-08-13 21:33:02', 'total_fee': '1',
        'transaction_id': '4200000149201808138100178561', 'sign': '061BC78497952DB19B3F337760A95647'
    }

    # 充值状态通知
    client = UnitTestAPIClient(token=token)
    response = client.post('/order/notify', data=data, format=None)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == 'invalid_order'


def test_payjs_notify_sign_error():
    user, token = get_user_and_token()
    client = UnitTestAPIClient(token=token)
    data = {
        'attach': ['{"tariff_name": "month1"}'], 'mchid': ['1511573911'], 'openid': ['o7LFAwUGHPZxyNahwjoNQtKh8EME'],
        'out_trade_no': ['1534167177710ovfltv6a8v7BsFAH0'], 'payjs_order_id': ['2018081321325600636471374'],
        'return_code': ['1'], 'time_end': ['2018-08-13 21:33:02'], 'total_fee': ['1'],
        'transaction_id': ['4200000149201808138100178561'], 'sign': ['this is error sign']
    }
    response = client.post('/order/notify', data=data, format=None)     # 以 Form 形式
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == 'invalid_signature'
