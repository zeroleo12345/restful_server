from django.contrib.auth.hashers import make_password
from django.utils import timezone
import factory
#
from models import Weixin, User
from trade.framework.authorization import JWTAuthentication


class WeixinFactory(factory.DjangoModelFactory):
    class Meta:
        model = Weixin

    openid = 'o0FSR0Zh3rotbOog_b2lytxzKrYo'     # zeroleo12345 在畅玩竹仔园下的openid
    nickname = factory.Sequence(lambda n: f'nickname_{n}')
    headimgurl = factory.Sequence(lambda n: f'http://www.headimgurl.com/{n}')

    created_at = timezone.localtime()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    weixin = factory.SubFactory(WeixinFactory)
    username = factory.Sequence(lambda n: f'username_{n}')
    password = factory.Sequence(lambda n: make_password(f'password_{n}'))
    is_enable = True
    role = factory.Iterator([role[0] for role in User.ROLE])


def get_user_and_authorization():
    user = UserFactory()
    user_dict = {
        'trader_id': user.trader_id,
        'shop_id': user.shop_id,
    }
    jwt_token = JWTAuthentication.jwt_encode_handler(user_dict=user_dict)
    return user, jwt_token
