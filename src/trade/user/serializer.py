from rest_framework import serializers
from django.utils import timezone

from trade.user.models import Weixin, User


class WeixinInfoValidator(serializers.Serializer):
    openid = serializers.CharField()
    nickname = serializers.CharField()
    headimgurl = serializers.CharField()


class WeixinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weixin
        fields = '__all__'


class UserWeixinSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

    weixin = WeixinSerializer()
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        # 已过期; 使用中; 已停用
        if not obj.is_active:
            return 'disabled'

        if obj.expired_at > timezone.localtime():
            return 'working'

        return 'expired'
