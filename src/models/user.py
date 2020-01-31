from __future__ import annotations
from django.db import models


# 微信号
class Weixin(models.Model):
    class Meta:
        app_label = 'trade'
        db_table = 'weixin'

    openid = models.CharField(max_length=255, null=False, unique=True)
    nickname = models.CharField(max_length=255)
    headimgurl = models.URLField(max_length=512)
    user_id = models.IntegerField(unique=True, null=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get(cls, openid=None, user_id=None):
        if openid:
            weixin = cls.objects.filter(openid=openid).first()
        elif user_id:
            weixin = cls.objects.filter(user_id=user_id).first()
        else:
            raise Exception('param error')
        if not weixin:
            return None
        return weixin

    @classmethod
    def create(cls, **kwargs):
        obj = cls.objects.create(**kwargs)
        return obj


# 账户, 密码
class User(models.Model):
    class Meta:
        app_label = 'trade'
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

    @classmethod
    def get(cls, id):
        user = cls.objects.filter(id=id).first()
        if not user:
            return None
        return user

    @classmethod
    def create(cls, **kwargs):
        obj = cls.objects.create(**kwargs)
        return obj
