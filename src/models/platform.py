from __future__ import annotations
#
from framework.database import models, BaseModel


class Platform(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'platform'
        unique_together = [
            ('owner_user_id',),
        ]

    id = models.AutoField(primary_key=True)
    owner_user_id = models.IntegerField()
    ssid = models.CharField(max_length=255, null=True)
    qrcode_url = models.URLField(max_length=512, null=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改

    @classmethod
    def get(cls, id=None, owner_user_id=None) -> 'Platform':
        if id:
            obj = cls.objects.filter(id=id).first()
        elif owner_user_id:
            obj = cls.objects.filter(owner_user_id=owner_user_id).first()
        else:
            raise Exception('param error')

        return obj or None
