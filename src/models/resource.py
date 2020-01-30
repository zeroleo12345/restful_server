from django.db import models
# 自己的库
from models import User
from models import Orders


# 用户免费资源
class Resource(models.Model):
    class Meta:
        app_label = 'trade'
        db_table = 'resource'

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    expired_at = models.DateTimeField(auto_now_add=True)    # ﻿auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # ﻿auto_now is generated on 每次修改


# 账本变更明细
class ResourceChange(models.Model):
    class Meta:
        app_label = 'trade'
        db_table = 'resource_change'

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    orders = models.ForeignKey(Orders, on_delete=models.CASCADE, null=False)
    before = models.DateTimeField()
    after = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)    # ﻿auto_now_add only generated on 新创建
