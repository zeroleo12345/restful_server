from django.db import transaction
# 项目库
from models import BroadBandOrder, User, Tariff, ResourceChange


def increase_user_resource(total_fee, out_trade_no, transaction_id, attach):
    # 根据out_trade_no检查数据库订单
    order = BroadBandOrder.get(out_trade_no=out_trade_no)
    from pprint import pprint; import pdb; pdb.set_trace()
    assert order
    assert not order.is_paid()
    user = User.get(id=order.user_id)
    assert user
    # 计算时长叠加
    tariff = Tariff.attach_to_tariff(attach)
    before = user.expired_at
    after = tariff.increase_duration(before)
    with transaction.atomic():
        # 变更免费资源
        user.update(expired_at=after)
        # 变更订单状态 和 微信订单号
        order.update(status='paid', transaction_id=transaction_id)
        # 插入免费资源历史变更表
        ResourceChange.create(user=user, order_id=order.id, before=before, after=after)
