from __future__ import annotations
#
from framework.database import models, BaseModel


# 账户
class MacAccount(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'mac_account'
        unique_together = [
            ('username',),
        ]

    id = models.AutoField(primary_key=True)
    #
    username = models.CharField(max_length=255)
    radius_password = models.CharField(max_length=255)
    is_enable = models.BooleanField(default=True)
    #
    expired_at = models.DateTimeField()
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改
