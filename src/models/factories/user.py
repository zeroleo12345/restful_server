import factory
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


def get_user_and_authorization():
    user = UserFactory()
    user_dict = user.to_dict()
    authorization = JWTAuthentication.jwt_encode_handler(user_dict=user_dict)
    return user, authorization
