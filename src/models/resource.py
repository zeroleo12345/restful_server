from __future__ import annotations
#
from django.db import models
# 项目库
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

    def get(self, user_id):
        resource = Resource.objects.filter(user_id=user_id).first()
        if not resource:
            return None
        return resource

    def update(self, **kwargs):
        for k, v in kwargs.items():
            assert hasattr(self, k)
            setattr(self, k, v)
        self.save()

    @classmethod
    def create(cls, **kwargs):
        obj = cls.objects.create(**kwargs)
        return obj


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

    @classmethod
    def create(cls, **kwargs):
        obj = cls.objects.create(**kwargs)
        return obj
