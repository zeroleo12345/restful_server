from django.contrib.auth.hashers import make_password
from django.utils import timezone

import factory
from trade.user.models import Weixin, User


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
