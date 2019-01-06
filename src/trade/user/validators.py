from rest_framework import serializers


class WeixinInfoValidator(serializers.Serializer):
    openid = serializers.CharField()
    nickname = serializers.CharField()
    headimgurl = serializers.CharField()


