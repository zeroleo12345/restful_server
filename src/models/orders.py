from __future__ import annotations
import uuid
# 第三方库
from django.db import models, transaction
# 项目库
from models import User, Resource, Tariff, ResourceChange


# 订单
class Orders(models.Model):
    class Meta:
        app_label = 'trade'
        db_table = 'orders'

    STATUS = (
        ('unpaid', '未支付'),
        ('paid', '已支付'),
        ('expired', '已过期'),
    )

    uuid = models.UUIDField(editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    openid = models.CharField(max_length=255)
    out_trade_no = models.CharField(max_length=255, unique=True)        # 商家订单号
    attach = models.CharField(max_length=255)                           # 附加信息
    transaction_id = models.CharField(default='', max_length=255)       # 微信订单号
    total_fee = models.IntegerField()                                   # 单位分
    appid = models.CharField(default='payjs', max_length=32)            # appid
    mch_id = models.CharField(max_length=32)                            # 商户号
    status = models.CharField(default='unpaid', max_length=32, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get(self, out_trade_no):
        order = Orders.objects.filter(out_trade_no=out_trade_no).first()
        if not order:
            return None
        return order

    def is_paid(self):
        if self.status == 'paid':
            return True
        return False

    @staticmethod
    def increase_user_resource(total_fee, out_trade_no, transaction_id, attach):
        # 根据out_trade_no检查数据库订单
        order = Orders.get(out_trade_no=out_trade_no)
        assert order
        if order.is_paid():
            return
        user = User.get(id=order.user_id)
        assert user
        resource = Resource.get(user_id=order.user_id)
        assert resource
        # 计算时长叠加
        tariff = Tariff.attach_to_tariff(attach)
        before = resource.expired_at
        after = tariff.increase_duration(before)
        with transaction.atomic():
            # 变更免费资源
            resource.expired_at = after
            resource.save()
            # 变更订单状态 和 微信订单号
            order.status = 'paid'
            order.transaction_id = transaction_id
            order.save()
            # 插入免费资源历史变更表
            ResourceChange.objects.create(user=user, orders=order, before=before, after=after)
