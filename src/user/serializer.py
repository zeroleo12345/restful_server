from rest_framework import serializers
# 自己的库
from models import Weixin, User


class WeixinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weixin
        fields = '__all__'


class UserWeixinSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('id',)

    weixin = WeixinSerializer()


class UserSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('id', 'weixin', 'is_enable', 'role')

    expired_at = serializers.CharField(source='resource.expired_at')