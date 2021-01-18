from rest_framework import status
#
from models import Account


class UserFactory(object):
    @classmethod
    def new_user_and_authorization(cls, client):
        # 发送注册验证码
        data = {
            'code': '001yROix1KtF1c0waVgx1k6Bix1yROiR'
        }
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
        assert 'id' in res_dict['data']['user']
        authorization = res_dict['data']['authorization']
        # FIXME
        account = Account.get(user_id=res_dict['data']['user']['id'], platform_id=1)
        assert account
        return account, authorization
