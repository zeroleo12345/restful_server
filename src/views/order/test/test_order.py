# 项目库
from framework.unittest import UnitTestAPIClient
from models.factories.user import UserFactory
from models.factories.order import BroadbandOrderFactory


def test_order_create():
    client = UnitTestAPIClient()
    user, authorization = UserFactory.new_user_and_authorization(client)
    client = UnitTestAPIClient(authorization=authorization)
    BroadbandOrderFactory.new_order(client)
