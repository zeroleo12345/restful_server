import uuid
from django.db import models


# 微信号, 账号, 密码
class User(models.Model):
    class Meta:
        db_table = 'user'

    ROLE = (
        ('admin', '管理员'),
        ('user', '用户'),
        ('guest', '访客'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    openid = models.CharField(max_length=255, null=False, unique=True)
    nickname = models.CharField(max_length=255)
    headimgurl = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    account = models.CharField(max_length=255, unique=True, null=True)
    password = models.CharField(max_length=255)
    is_enable = models.BooleanField(default=True)
    role = models.CharField(max_length=32, choices=ROLE, default='user')


# 免费资源
class Resource(models.Model):
    class Meta:
        db_table = 'resource'

    ROLE = (
        ('admin', '管理员'),
        ('user', '用户'),
        ('guest', '访客'),
    )
    user = models.ForeignKey(User)
    amount = models.IntegerField(default=0)     # 单位条
    expired_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


# 交易历史
class TradeHistory(models.Model):
    class Meta:
        db_table = 'trade_history'

    STATUS = (
        'unpaid', '未支付',
        'paid', '已支付',
        'expired', '已过期',
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
