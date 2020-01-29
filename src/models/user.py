from django.db import models
from django.contrib.auth.models import AbstractBaseUser


# 微信号
class Weixin(models.Model):
    class Meta:
        db_table = 'weixin'

    openid = models.CharField(max_length=255, null=False, unique=True)
    nickname = models.CharField(max_length=255)
    headimgurl = models.URLField(max_length=512)
    #
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
    is_enable = models.BooleanField(default=True)
    role = models.CharField(max_length=32, choices=ROLE, default='user')

    def __str__(self):
        return self.username
