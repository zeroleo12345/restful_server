from __future__ import annotations
from django.utils import timezone
#
from framework.database import models, BaseModel


# 账户
class Account(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'broadband_user'
        unique_together = [
            ('openid', 'platform_id'),
        ]

    ROLE = (
        ('platform_owner', '平台属主'),
        ('user', '用户'),
        ('guest', '访客'),
    )

    id = models.AutoField(primary_key=True)
    openid = models.CharField(max_length=255, null=False)
    platform_id = models.IntegerField(null=True)    # TODO 改数据后改为 null=False
    # 头像: JPEG 格式 http://thirdwx.qlogo.cn/mmopen/vi_32/lRUxxd0YsmibtZKWiaw7g/132
    nickname = models.CharField(max_length=255)     # TODO 删除
    headimgurl = models.URLField(max_length=512)    # TODO 删除
    #
    username = models.CharField(max_length=255, unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
    is_enable = models.BooleanField(default=True)
    role = models.CharField(max_length=32, choices=ROLE, default='user')
    #
    expired_at = models.DateTimeField()
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改

    @classmethod
    def get(cls, id=None, openid=None, platform_id=None):
        if id:
            obj = cls.objects.filter(id=id).first()
        elif openid and platform_id:
            obj = cls.objects.filter(openid=openid, platform_id=platform_id).first()
        else:
            raise Exception('param error')
        if not obj:
            return None
        return obj

    @classmethod
    def search(cls, nickname__contains):
        users = cls.objects.filter(nickname__contains=nickname__contains)
        if not users:
            return []
        return users

    def get_resource_status(self):
        # expired: 已过期; working: 使用中; inactive: 已停用
        if not self.is_enable:
            return 'inactive'

        if self.expired_at > timezone.localtime():
            return 'working'

        return 'expired'