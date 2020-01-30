import uuid
# 第三方库
from django.db import models
# 自己的库
from models import User


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

    def is_paid(self):
        if self.status == 'paid':
            return True
        return False
