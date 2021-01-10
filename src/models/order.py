from __future__ import annotations
# 第三方库
from framework.database import models, BaseModel
from framework.field import BaseEnum


# 宽带订单
class Order(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'orders'
        unique_together = [
            ('out_trade_no',),
        ]

    class Status(BaseEnum):
        UNPAID = 'unpaid'       # 未支付
        PAID = 'paid'           # 已支付
        EXPIRED = 'expired'     # 已过期

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    openid = models.CharField(max_length=255)
    out_trade_no = models.CharField(max_length=255)        # 商家订单号
    attach = models.CharField(max_length=255)                           # 附加信息
    transaction_id = models.CharField(default='', max_length=255)       # 微信订单号
    total_fee = models.IntegerField()                                   # 单位分
    appid = models.CharField(max_length=32)                             # appid
    mch_id = models.CharField(max_length=32)                            # 商户号
    status = models.CharField(default='unpaid', max_length=32, choices=Status.model_choices())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get(cls, out_trade_no) -> Order:
        order = cls.objects.filter(out_trade_no=out_trade_no).first()
        if not order:
            return None
        return order

    def is_paid(self) -> bool:
        return self.status == Order.Status.PAID.value
