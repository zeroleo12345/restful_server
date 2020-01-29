from rest_framework import generics
from rest_framework import exceptions
from django.db import transaction
# 自己的库
from trade.framework.authorization import JWTAuthentication
from models import User, Weixin
from user.serializer import UserWeixinSerializer, UserSyncSerializer
from service.wechat.we_oauth import WeOAuth
from trade.utils.myrandom import MyRandom
from models import Resource
from buffer.token import WechatCode


# /user 通过微信oauth2接口, 获取微信用户信息
class UserView(generics.RetrieveAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserWeixinSerializer

    def get_object(self):
        token = self.request.META.get('HTTP_AUTHORIZATION', '')
        if token:
            user = JWTAuthentication.jwt_decode_handler(token)
        else:
            code = self.request.GET.get('code', '')
            if not code:
                raise exceptions.ValidationError('code字段不能为空', 'invalid_code')
            openid, nickname, avatar = WechatCode.get(code)    # https://blog.csdn.net/limenghua9112/article/details/81911658
            if not openid:
                openid, nickname, avatar = WeOAuth.get_user_info(code=code)
                if not openid:
                    raise exceptions.ValidationError('code无效, 请重试', 'invalid_code')
                WechatCode.set(code, openid=openid, nickname=nickname, avatar=avatar)
            # 获取用户信息, 不存在则创建
            user = User.objects.filter(weixin__openid=openid).first()
            if not user:
                weixin_fields = {
                    'openid': openid,
                    'nickname': nickname,
                    'headimgurl': avatar,
                }
                username = MyRandom.random_digit(length=8)
                user_fields = {
                    'weixin': Weixin.objects.create(**weixin_fields),
                    'username': username,
                    'password': username,
                    'role': 'user',
                }
                with transaction.atomic():
                    user = User.objects.create(**user_fields)   # create 返回 Model 实例
                    Resource.objects.create(user=user)

        self.request.user = user    # 用于Response时, 设置JsonWebToken
        return user


# /user/sync 同步用户列表
class UserSyncView(generics.ListAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSyncSerializer
    pagination_class = None

    def get_queryset(self):
        return User.objects.all().select_related('resource')
