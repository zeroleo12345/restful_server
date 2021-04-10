from __future__ import annotations
#
from framework.database import models, BaseModel


class StatUser(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'stat_user'

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    user_mac = models.CharField(max_length=24)     # 连接符"-", 全部大写. 5E-DA-F9-68-41-2B
    ap_mac = models.CharField(max_length=24)       # 连接符"-", 全部大写. 5E-DA-F9-68-41-2B
    accept_count = models.IntegerField()
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建


class StatAp(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'stat_ap'

    id = models.AutoField(primary_key=True)
    ap_mac = models.CharField(max_length=24)       # 连接符"-", 全部大写. 5E-DA-F9-68-41-2B
    last_auth_user = models.CharField(max_length=255)
    last_auth_date = models.DateField()
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
