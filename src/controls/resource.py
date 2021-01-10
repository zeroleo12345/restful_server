from django.db import transaction
# 项目库
from models import Order, Account, Tariff, ResourceChange


def increase_user_resource(total_fee, out_trade_no, transaction_id, attach):
    # 根据out_trade_no检查数据库订单
    order = Order.get(out_trade_no=out_trade_no)
    assert order
    assert not order.is_paid()
    account = Account.get(id=order.user_id)
    assert account
    # 计算时长叠加
    tariff = Tariff.attach_to_tariff(attach)
    before = account.expired_at
    after = tariff.increase_duration(before)
    with transaction.atomic():
        # 变更免费资源
        account.update(expired_at=after)
        # 变更订单状态 和 微信订单号
        order.update(status=Order.Status.PAID.value, transaction_id=transaction_id)
        # 插入免费资源历史变更表
        ResourceChange.create(user_id=account.id, order_id=order.id, before=before, after=after)
