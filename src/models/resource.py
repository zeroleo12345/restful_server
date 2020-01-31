from __future__ import annotations
#
from framework.database import models, BaseModel


# 用户免费资源
class Resource(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'resource'

    user_id = models.IntegerField(unique=True, null=False)
    expired_at = models.DateTimeField(auto_now_add=True)    # ﻿auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # ﻿auto_now is generated on 每次修改

    @classmethod
    def get(cls, user_id):
        resource = Resource.objects.filter(user_id=user_id).first()
        if not resource:
            return None
        return resource


# 账本变更明细
class ResourceChange(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'resource_change'

    user_id = models.IntegerField(null=False)
    orders_id = models.IntegerField(null=False)
    before = models.DateTimeField()
    after = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)    # ﻿auto_now_add only generated on 新创建
