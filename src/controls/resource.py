from django.db import transaction
import sentry_sdk
# 项目库
from models import Order, Account, Tariff, ResourceChange, User, Platform
from service.wechat.we_message import WePush


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
    try:
        # 公众号消息通知owner
        platform = Platform.get(id=account.platform_id)
        user = User.get(id=account.user_id)
        WePush.notify_owner_order_paid(openid=platform.owner_user_id, total_fee=order.total_fee, nickname=user.nickname, paid_at=order.updated_at)
    except Exception as e:
        sentry_sdk.capture_exception(e)
