import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser


# 微信号
class Weixin(models.Model):
    class Meta:
        db_table = 'weixin'

    openid = models.CharField(max_length=255, null=False, unique=True)
    nickname = models.CharField(max_length=255)
    headimgurl = models.URLField(max_length=512)

    created_at = models.DateTimeField(auto_now_add=True)


# 账户, 密码
class User(AbstractBaseUser):
    class Meta:
        db_table = 'user'

    ROLE = (
        ('vip', 'VIP用户'),
        ('user', '用户'),
        ('guest', '访客'),
    )

    weixin = models.OneToOneField(Weixin, on_delete=models.CASCADE, null=False)
    username = models.CharField(max_length=255, unique=True, null=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=32, choices=ROLE, default='user')

    expired_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# 交易历史
class TradeHistory(models.Model):
    class Meta:
        db_table = 'trade_history'

    STATUS = (
        ('unpaid', '未支付'),
        ('paid', '已支付'),
        ('expired', '已过期'),
    )

    uuid = models.UUIDField(editable=False, default=uuid.uuid4)
    openid = models.CharField(max_length=255)
    out_trade_no = models.CharField(max_length=255, unique=True)     # 商家订单号
    attach = models.CharField(max_length=255)           # 附加信息
    transaction_id = models.CharField(max_length=255)   # 微信订单号
    total_fee = models.IntegerField()                   # 单位分
    appid = models.CharField(max_length=32)             # appid
    mch_id = models.CharField(max_length=32)            # 商户号
    status = models.CharField(max_length=32, choices=STATUS, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
