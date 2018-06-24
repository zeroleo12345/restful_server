from rest_framework import serializers

from trade.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('id', 'password')

    uuid = serializers.UUIDField(read_only=True, format='hex')


class UserInfoFromWechatFormSerializer(serializers.Serializer):
    """
    get_user_info:
    {
        u'province': u'\u5e7f\u4e1c', u'openid': u'ovj3E0l9vffwBuqz_PNu25yL_is4',
        u'headimgurl': u'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7AianZsHE6LefhQuSmwibx4KZ9LYkRmIibrFKmSbAVjlpBg/0',
        u'language': u'zh_CN', u'city': u'\u5e7f\u5dde', u'country': u'\u4e2d\u56fd', u'sex': 1, u'privilege': [],
        u'nickname': u'\u5468\u793c\u6b23'
    }
    """
    openid = serializers.CharField()
    nickname = serializers.CharField()
    headimgurl = serializers.CharField()
