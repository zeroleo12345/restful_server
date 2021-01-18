from django.db import transaction
import sentry_sdk
# 项目库
from models import Order, Account, Tariff, ResourceChange, User, Platform
from service.wechat.we_message import WePush


def increase_user_resource(total_fee: int, out_trade_no: str, transaction_id: str, attach: str):
    # 根据out_trade_no检查数据库订单
    order = Order.get(out_trade_no=out_trade_no)
    assert order
    assert not order.is_paid()
    account = Account.get(user_id=order.user_id, platform_id=order.platform_id)
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
    try:
        # 公众号消息通知owner
        platform = Platform.get(id=account.platform_id)
        user = User.get(id=account.user_id)
        owner = User.get(id=platform.owner_user_id)
        WePush.notify_owner_order_paid(openid=owner.openid, total_fee=order.total_fee, nickname=user.nickname,
                                       paid_at=order.updated_at, trade_no=out_trade_no)
    except Exception as e:
        # TODO 稳定后删除try except
        sentry_sdk.capture_exception(e)
