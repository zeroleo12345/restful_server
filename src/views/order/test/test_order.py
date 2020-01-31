# 项目库
from framework.unittest import UnitTestAPIClient
from models.factories.user import UserFactory
from models.factories.orders import OrdersFactory


def test_order_create():
    client = UnitTestAPIClient()
    user, authorization = UserFactory.new_user_and_authorization(client)
    client = UnitTestAPIClient(authorization=authorization)
    OrdersFactory.new_order(client)
