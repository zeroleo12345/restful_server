from rest_framework import serializers
from django.utils import timezone
# 自己的库
from trade.resource.models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        exclude = ('id', 'user',)

    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        # expired: 已过期; working: 使用中; inactive: 已停用
        if not obj.user.is_enable:
            return 'inactive'

        if obj.expired_at > timezone.localtime():
            return 'working'

        return 'expired'
