from __future__ import annotations
from django.utils import timezone
#
from framework.database import models, BaseModel
from framework.field import ModelEnum


# 账户
class Account(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'account'
        unique_together = [
            ('user_id', 'platform_id'),
            ('username',),
        ]

    class Role(ModelEnum):
        PLATFORM_OWNER = 'platform_owner'   # 平台属主
        PAY_USER = 'pay_user'               # 付费用户
        FREE_USER = 'free_user'             # 免费用户

    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    platform_id = models.BigIntegerField()
    #
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    radius_password = models.CharField(max_length=255)
    is_enable = models.BooleanField(default=True)
    role = models.CharField(max_length=32, choices=Role.choices(), default=Role.PAY_USER.value)
    #
    expired_at = models.DateTimeField()
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改

    @classmethod
    def get(cls, user_id, platform_id) -> 'Account':
        obj = cls.objects.filter(user_id=user_id, platform_id=platform_id).first()
        return obj or None

    @classmethod
    def search(cls, user_id):
        accounts = cls.objects.filter(user_id=user_id)
        if not accounts:
            return []
        return accounts

    def get_resource_status(self):
        # expired: 已过期; working: 使用中; inactive: 已停用
        if not self.is_enable:
            return 'inactive'

        if self.expired_at > timezone.localtime():
            return 'working'

        return 'expired'

    def to_dict(self, fields=None, exclude=None):
        data = super(self.__class__, self).to_dict(fields=fields, exclude=exclude)
        data['status'] = self.get_resource_status()
        return data
