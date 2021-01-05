from __future__ import annotations
#
from framework.database import models, BaseModel


class User(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'user'

    id = models.AutoField(primary_key=True)
    openid = models.CharField(max_length=255, unique=True, null=False)
    bind_platform_id = models.IntegerField(null=False)
    # 头像: JPEG 格式 http://thirdwx.qlogo.cn/mmopen/vi_32/lRUxxd0YsmibtZKWiaw7g/132
    nickname = models.CharField(max_length=255)
    headimgurl = models.URLField(max_length=512)
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改

    @classmethod
    def get(cls, openid) -> 'User':
        obj = cls.objects.filter(openid=openid).first()
        if not obj:
            return None
        return obj

    @classmethod
    def search(cls, nickname__contains) -> 'User':
        users = cls.objects.filter(nickname__contains=nickname__contains)
        if not users:
            return []
        return users
