from __future__ import annotations
#
from framework.database import models, BaseModel


class Platform(models.Model, BaseModel):
    class Meta:
        app_label = 'trade'
        db_table = 'platform'
        unique_together = [
            ('platform_id',),
            ('owner_user_id',),
        ]

    id = models.AutoField(primary_key=True)
    platform_id = models.BigIntegerField(null=True)
    owner_user_id = models.BigIntegerField(null=True)
    ssid = models.CharField(max_length=255, null=True)
    #
    qrcode_content = models.URLField(max_length=512, null=True)     # 二维码内容, 例如: http://weixin.qq.com/q/02SE2_xxx
    owner_profit_percent = models.DecimalField(null=True, max_digits=9, decimal_places=6)   # 利润比例.(单位%, 例如 30%)
    #
    created_at = models.DateTimeField(auto_now_add=True)    # auto_now_add only generated on 新创建
    updated_at = models.DateTimeField(auto_now=True)        # auto_now is generated on 每次修改

    @classmethod
    def get(cls, platform_id) -> 'Platform':
        obj = cls.objects.filter(platform_id=platform_id).first()
        return obj or None

    def is_platform_owner(self, user_id: str) -> bool:
        return self.owner_user_id == user_id
