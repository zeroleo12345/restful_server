from __future__ import annotations
#
from framework.database import models, BaseModel
from utils.snowflake import new_id


class User(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'user'
        unique_together = [
            ('user_id',),
            ('openid',),
        ]

    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField(default=new_id)
    openid = models.CharField(max_length=255)
    bind_platform_id = models.BigIntegerField()
    # 头像: JPEG 格式 http://thirdwx.qlogo.cn/mmopen/vi_32/lRUxxd0YsmibtZKWiaw7g/132
    nickname = models.CharField(max_length=255)
    picture_url = models.URLField(max_length=512)
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改

    @classmethod
    def get(cls, user_id=None, openid=None) -> 'User':
        if user_id:
            obj = cls.objects.filter(user_id=user_id).first()
        elif openid:
            obj = cls.objects.filter(openid=openid).first()
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
