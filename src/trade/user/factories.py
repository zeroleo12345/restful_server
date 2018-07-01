from django.contrib.auth.hashers import make_password
from django.utils import timezone

import factory
from trade.user.models import Weixin, User


class WeixinFactory(factory.DjangoModelFactory):
    class Meta:
        model = Weixin

    openid = factory.Sequence(lambda n: f'openid:{n}')
    nickname = factory.Sequence(lambda n: f'nickname:{n}')
    headimgurl = factory.Sequence(lambda n: f'http://www.headimgurl.com/{n}')

    created_at = timezone.localtime()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'username:{n}')
    password = factory.Sequence(lambda n: make_password(f'password:{n}'))
    is_active = True
    role = factory.Iterator([role[0] for role in User.ROLE])
    expired_at = timezone.localtime()
    updated_at = timezone.localtime()

    weixin = factory.SubFactory(WeixinFactory)
