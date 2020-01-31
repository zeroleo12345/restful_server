from unittest.mock import patch
import pytest
# 第三方库
from rest_framework import status
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
# 项目库
from framework.field import new_uuid
from framework.unittest import UnitTestAPIClient
from models.factories.user import UserFactory
from models.factories.order import BroadbandOrderFactory


def test_payjs_notify_success():
    client = UnitTestAPIClient()
    user, authorization = UserFactory.new_user_and_authorization(client)
    client = UnitTestAPIClient(authorization=authorization)
    order = BroadbandOrderFactory.new_order(client)
    with patch('service.wechat.we_pay.WePay.parse_payment_result') as _mock:
        _mock.return_value = {
            'appid': order.appid,
            'attach': order.attach,
            'bank_type': 'CFT',
            'return_code': 'SUCCESS',
            'out_trade_no': order.out_trade_no,
            'total_fee': order.total_fee,
            'transaction_id': new_uuid(),
            'openid': new_uuid(),
            'time_end': '20190101000000',
        }
        #
        # 充值通知
        data = {
            'attach': order.attach, 'mchid': order.mch_id, 'openid': order.openid,
            'out_trade_no': order.out_trade_no,
            'return_code': '1', 'time_end': '2018-08-13 21:33:02', 'total_fee': '1',
            'transaction_id': '4200000149201808138100178561', 'sign': '061BC78497952DB19B3F337760A95647'
        }
        response = client.post('/order/notify', data=data, format=None)
    assert response.status_code == status.HTTP_200_OK

    # 检查用户时长是否已经叠加
    response = client.get('/resource')
    assert response.status_code == status.HTTP_200_OK
    """
    {
        'code': 'ok',
        'data': {
            'id': 1, 'status': 'working', 'expired_at': '2018-09-18T12:28:50.649466+08:00',
            'updated_at': '2018-08-18T12:28:50.650826+08:00'
        }
    }
    """
    json_resposne = response.json()
    assert json_resposne['data']['status'] == 'working'
    expired_at = timezone.localtime(parse_datetime(json_resposne['data']['expired_at']))
    assert expired_at >= timezone.localtime() + relativedelta(months=1) - relativedelta(hours=1)
