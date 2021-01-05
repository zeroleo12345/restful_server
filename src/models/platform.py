from __future__ import annotations
#
from framework.database import models, BaseModel


class Platform(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'platform'

    id = models.AutoField(primary_key=True)
    owner_user_id = models.IntegerField(null=False)
    ssid = models.CharField(max_length=255)
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改

    @classmethod
    def get(cls, id) -> 'Platform':
        obj = cls.objects.filter(id=id).first()
        return obj or None
