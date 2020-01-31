from rest_framework import status
#
from models import User


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
        assert 'headimgurl' in res_dict['data']['user']
        assert 'created_at' in res_dict['data']['user']
        assert 'username' in res_dict['data']['user']
        assert 'is_enable' in res_dict['data']['user']
        assert 'role' in res_dict['data']['user']
        assert 'id' in res_dict['data']['user']
        authorization = res_dict['data']['authorization']
        #
        user = User.get(id=res_dict['data']['user']['id'])
        assert user
        return user, authorization
