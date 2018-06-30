import uuid
from django.db import models


# 微信号, 账号, 密码
class User(models.Model):
    class Meta:
        db_table = 'user'

    ROLE = (
        ('vip', 'VIP用户'),
        ('user', '用户'),
        ('guest', '访客'),
    )

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    openid = models.CharField(max_length=255, null=False, unique=True)
    nickname = models.CharField(max_length=255)
    headimgurl = models.URLField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    username = models.CharField(max_length=255, unique=True, null=True)
    password = models.CharField(max_length=255)
    is_enable = models.BooleanField(default=True)
    expired_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=32, choices=ROLE, default='user')


class Token(models.Model):
    class Meta:
        db_table = 'token'

    key = models.UUIDField(unique=True, default=uuid.uuid4)
    user = models.OneToOneField(User, related_name='auth_token', on_delete=models.CASCADE, verbose_name="User")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Auto Convert To uuid.hex
        return self.key.hex


# 交易历史
class TradeHistory(models.Model):
    class Meta:
        db_table = 'trade_history'

    STATUS = (
        ('unpaid', '未支付'),
        ('paid', '已支付'),
        ('expired', '已过期'),
    )
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
