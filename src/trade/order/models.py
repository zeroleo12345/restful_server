import uuid
from django.db import models


# 订单历史
class Order(models.Model):
    class Meta:
        db_table = 'order'

    STATUS = (
        ('unpaid', '未支付'),
        ('paid', '已支付'),
        ('expired', '已过期'),
    )

    uuid = models.UUIDField(editable=False, default=uuid.uuid4)
    openid = models.CharField(max_length=255)
    out_trade_no = models.CharField(max_length=255, unique=True)     # 商家订单号
    attach = models.CharField(max_length=255)           # 附加信息
    transaction_id = models.CharField(default='', max_length=255)   # 微信订单号
    total_fee = models.IntegerField()                   # 单位分
    appid = models.CharField(default='payjs', max_length=32)             # appid
    mch_id = models.CharField(max_length=32)            # 商户号
    status = models.CharField(default='unpaid', max_length=32, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
