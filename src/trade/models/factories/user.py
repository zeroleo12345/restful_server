from rest_framework import status
#
from trade.models import Account


class UserFactory(object):
    @classmethod
    def new_user_and_authorization(cls, client):
        data = {
            'code': '001yROix1KtF1c0waVgx1k6Bix1yROiR'
        }
        # TODO 注册流程 改为 扫描带参数二维码!
        response = client.get('/user', data=data)
        assert response.status_code == status.HTTP_200_OK
        #
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
