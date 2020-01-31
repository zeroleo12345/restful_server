from __future__ import annotations
#
from framework.database import models, BaseModel


# 账本变更明细
class ResourceChange(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'resource_change'

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=False)
    order_id = models.IntegerField(null=False)
    before = models.DateTimeField()
    after = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)    # ﻿auto_now_add only generated on 新创建
