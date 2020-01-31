from rest_framework import serializers
# 项目库
from models import User


class UserSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('id', 'weixin', 'is_enable', 'role')

    expired_at = serializers.CharField(source='resource.expired_at')
