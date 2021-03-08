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
    ap_mac = models.CharField(max_length=24)       # 连接符"-", 全部大写. 5E-DA-F9-68-41-2B
    is_enable = models.BooleanField(default=True)
    bind_username = models.CharField(max_length=255, null=True)
    #
    expired_at = models.DateTimeField()
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
