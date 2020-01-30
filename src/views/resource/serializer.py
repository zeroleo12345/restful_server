from rest_framework import serializers
from django.utils import timezone
# 项目库
from models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        exclude = ('id', 'user',)

    status = serializers.SerializerMethodField()

    def get_status(self, row):
        # expired: 已过期; working: 使用中; inactive: 已停用
        if not row.user.is_enable:
            return 'inactive'

        if row.expired_at > timezone.localtime():
            return 'working'

        return 'expired'
