import pytest
from unittest.mock import patch
from rest_framework import status
from trade.models import Platform
#
from trade.models import Account, User


class UserFactory(object):
    @classmethod
    def new_user_and_authorization(cls, client):
        platform = Platform.get(owner_user_id=1)
        if not platform:
            platform = Platform.create(owner_user_id=1)
            platform.update(platform_id=platform.id, ssid=f'WIFI-{platform.platform_id}')
        from wechatpy.events import SubscribeScanEvent
        from collections import OrderedDict
        #
        from_user_openid = 'o0FSR0RqA2oXc6x1uW0MGVKayp'
        with patch('service.wechat.we_crypto.WeCrypto.decrypt_and_parse_message') as _mock:
            _mock.return_value = SubscribeScanEvent(OrderedDict([
                ('ToUserName', 'gh_d71de39dd1'),
                ('FromUserName', from_user_openid),
                ('CreateTime', '1617715451'),
                ('MsgType', 'event'),
                ('Event', 'subscribe_scan'),
                ('EventKey', f'{platform.platform_id}'),
                ('Ticket', 'nFxLmNvbS9xLzAydXI0bHQ3Z2tlaGgxMDAwME0wN2cAAgTl_-pfAw')
            ]))
            data = {
                'body': 'xxx'
            }
            response = client.post('/mp/echostr', data=data)
            assert response.status_code == status.HTTP_200_OK
        #
        # TODO 注册流程 改为 扫描带参数二维码!
        user = User.get(openid=from_user_openid)
        res_dict = response.json()
        assert 'ok' == res_dict['code']
        assert 'user' in res_dict['data']
        assert 'openid' in res_dict['data']['user']
        assert 'nickname' in res_dict['data']['user']
        assert 'picture_url' in res_dict['data']['user']
        assert 'created_at' in res_dict['data']['user']
        assert 'updated_at' in res_dict['data']['user']
        assert 'expired_at' in res_dict['data']['user']
        assert 'username' in res_dict['data']['user']
        assert 'is_enable' in res_dict['data']['user']
        assert 'role' in res_dict['data']['user']
        assert 'user_id' in res_dict['data']['user']
        authorization = res_dict['data']['authorization']
        account = Account.get(user_id=res_dict['data']['user']['user_id'], platform_id=1)
        assert account
        return account, authorization
