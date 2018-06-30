from rest_framework import serializers
from django.utils import timezone

from trade.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('id', 'password')

    uuid = serializers.UUIDField(read_only=True, format='hex')
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        # 已过期; 使用中; 已停用
        if not obj.is_enable:
            return 'disabled'

        if obj.expired_at > timezone.localtime():
            return 'working'

        return 'expired'


class UserInfoFromWechatFormSerializer(serializers.Serializer):
    openid = serializers.CharField()
    nickname = serializers.CharField()
    headimgurl = serializers.CharField()
