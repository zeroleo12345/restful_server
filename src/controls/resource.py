from django.db import transaction
# 项目库
from models import Order, Account, Tariff, ResourceChange, User, Platform
from service.wechat.we_message import WePush
from trade.settings import log


def increase_user_resource(total_fee: int, out_trade_no: str, transaction_id: str, attach: str):
    # 根据out_trade_no检查数据库订单
    order = Order.get(out_trade_no=out_trade_no)
    assert order
    assert not order.is_paid()
    account = Account.get(user_id=order.user_id, platform_id=order.platform_id)
    assert account
    # 计算时长叠加
    tariff = Tariff.convert_from_attach(attach)
    assert tariff
    before = account.expired_at
    after = tariff.increase_duration(before)
    with transaction.atomic():
        # 变更免费资源
        account.update(expired_at=after)
        # 变更订单状态 和 微信订单号
        order.update(status=Order.Status.PAID.value, transaction_id=transaction_id)
        # 插入免费资源历史变更表
        ResourceChange.create(user_id=account.user_id, out_trade_no=order.out_trade_no, before=before, after=after)
    log.i(f"UPDATE orders SET status = '{order.status}', transaction_id = '{transaction_id}' WHERE out_trade_no = '{out_trade_no}'")
    # 公众号消息通知owner
    platform = Platform.get(platform_id=account.platform_id)
    user = User.get(user_id=account.user_id)
    owner = User.get(user_id=platform.owner_user_id)
    WePush.notify_owner_order_paid(platform_id=platform.platform_id, openid=owner.openid, total_fee=order.total_fee,
                                   nickname=user.nickname, paid_at=order.updated_at, trade_no=out_trade_no)
