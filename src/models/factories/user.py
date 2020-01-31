import factory
from rest_framework import status
#
from models import User
from framework.authorization import JWTAuthentication


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'username_{n}')
    password = factory.Sequence(lambda n: f'password_{n}')
    is_enable = True
    role = factory.Iterator([role[0] for role in User.ROLE])

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


def get_user_and_authorization():
    user = UserFactory()
    user_dict = user.to_dict()
    authorization = JWTAuthentication.jwt_encode_handler(user_dict=user_dict)
    return user, authorization
