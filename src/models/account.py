from __future__ import annotations
from django.utils import timezone
#
from framework.database import models, BaseModel


# 账户
class Account(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'account'
        unique_together = [
            ('user_id', 'platform_id'),
            ('username',),
        ]

    ROLE = (
        ('platform_owner', '平台属主'),
        ('user', '用户'),
    )

    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=255)
    platform_id = models.IntegerField(null=True)    # TODO 改数据后改为 null=False
    # 头像: JPEG 格式 http://thirdwx.qlogo.cn/mmopen/vi_32/lRUxxd0YsmibtZKWiaw7g/132
    nickname = models.CharField(max_length=255)     # TODO 删除
    picture_url = models.URLField(max_length=512)    # TODO 删除
    #
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_enable = models.BooleanField(default=True)
    role = models.CharField(max_length=32, choices=ROLE, default='user')
    #
    expired_at = models.DateTimeField()
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改

    @classmethod
    def get(cls, id=None, user_id=None, platform_id=None):
        if id:
            obj = cls.objects.filter(id=id).first()
        elif user_id and platform_id:
            obj = cls.objects.filter(user_id=user_id, platform_id=platform_id).first()
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
