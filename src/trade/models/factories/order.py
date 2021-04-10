from unittest.mock import patch
#
from rest_framework import status
#
from trade.models import Order


class OrderFactory(object):
    @classmethod
    def new_order(cls, client):
        with patch('service.wechat.we_pay.WePay.create_jsapi_order') as _mock:
            _mock.return_value = {
                'return_code': 'SUCCESS',
                'return_msg': 'OK',
                'appid': 'wx14d296959e000000',
                'mch_id': '1517000000',
                'nonce_str': 'RDX6pxz2GT000000',
                'sign': '796CC22F8EDD664372BE9ACF7E000000',
                'result_code': 'SUCCESS',
                'prepay_id': 'wx242238115691612efb08d4092661000000',
                'trade_type': 'JSAPI',
            }
            #
            data = {
                'tariff_name': 'month1',
            }
            response = client.post('/order', data=data)
        assert response.status_code == status.HTTP_200_OK
        res_dict = response.json()
        assert 'ok' == res_dict['code']
        order = res_dict['data']['order']
        param = res_dict['data']['param']
        assert 'appId' in param
        assert 'nonceStr' in param
        assert 'package' in param
        assert 'paySign' in param
        assert 'signType' in param
        assert 'timeStamp' in param
        out_trade_no = order['out_trade_no']
        order = Order.get(out_trade_no=out_trade_no)
        assert order
        return order
