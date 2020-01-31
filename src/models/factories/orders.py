from unittest.mock import patch
#
from rest_framework import status
#
from utils.wepay import WePay


class OrdersFactory(object):
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
            data = {
                'tariff_name': 'month1',
            }
            response = client.post('/order', data=data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['code'] == 'ok'
        prepay_id = data['prepay_id']
        #
        jsapi_params = WePay.get_jsapi_params(prepay_id=prepay_id)
        assert data
        assert 'appId' in jsapi_params
        assert 'nonceStr' in jsapi_params
        assert 'package' in jsapi_params
        assert 'paySign' in jsapi_params
        assert 'signType' in jsapi_params
        assert 'timeStamp' in jsapi_params
