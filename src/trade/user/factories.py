import factory
from trade.user.models import Token, User
from django.contrib.auth.hashers import make_password


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    openid = factory.Sequence(lambda n: f'openid:{n}')
    nickname = factory.Sequence(lambda n: f'nickname:{n}')
    headimgurl = factory.Sequence(lambda n: f'http://www.headimgurl.com/{n}')

    username = factory.Sequence(lambda n: f'username:{n}')
    password = factory.Sequence(lambda n: make_password(f'password:{n}'))
    is_enable = True
    role = factory.Iterator(['vip', 'user', 'guest'])


class TokenFactory(factory.DjangoModelFactory):
    class Meta:
        model = Token
