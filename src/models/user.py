from __future__ import annotations
from framework.database import models, BaseModel


class User(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'user'

    ROLE = (
        ('vip', 'VIP用户'),
        ('user', '用户'),
        ('guest', '访客'),
    )

    openid = models.CharField(max_length=255, unique=True, null=False)
    nickname = models.CharField(max_length=255)
    headimgurl = models.URLField(max_length=512)
    #
    username = models.CharField(max_length=255, unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
    is_enable = models.BooleanField(default=True)
    role = models.CharField(max_length=32, choices=ROLE, default='user')
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get(cls, id, openid):
        if id:
            user = cls.objects.filter(id=id).first()
        elif openid:
            user = cls.objects.filter(openid=openid).first()
        else:
            raise Exception('param error')
        if not user:
            return None
        return user
