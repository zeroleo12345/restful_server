from rest_framework import status


class OrdersFactory(object):
    @classmethod
    def new_order(cls, client):
        data = {
            'tariff_name': 'month1',
        }
        response = client.post('/order', data=data)
        assert response.status_code == status.HTTP_200_OK
        #
        res_dict = response.json()
        assert 'ok' == res_dict['code']
        assert 'user' in res_dict['data']
        assert 'openid' in res_dict['data']['user']['weixin']
        assert 'nickname' in res_dict['data']['user']['weixin']
        assert 'headimgurl' in res_dict['data']['user']['weixin']
        assert 'created_at' in res_dict['data']['user']['weixin']
        assert 'username' in res_dict['data']['user']
        assert 'is_enable' in res_dict['data']['user']
        assert 'role' in res_dict['data']['user']
        assert 'id' in res_dict['data']['user']
        # {'appId': 'wx54d296959ee50c0b',
        #  'nonceStr': '603sd7IpN4M2OqCVvZazxrXY9bT5lBcR',
        #  'package': 'prepay_id=wx242238115691612efb08d4092661275602',
        #  'paySign': '6D2340AC7276C93852461E130A404E87',
        #  'signType': 'MD5',
        #  'timeStamp': '1540391991'}
