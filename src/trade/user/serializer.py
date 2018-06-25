from rest_framework import serializers

from trade.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('id', 'password')

    uuid = serializers.UUIDField(read_only=True, format='hex')


class UserInfoFromWechatFormSerializer(serializers.Serializer):
    openid = serializers.CharField()
    nickname = serializers.CharField()
    headimgurl = serializers.CharField()
