from rest_framework import generics
from rest_framework import exceptions
from django.db import transaction
# 自己的库
from trade.framework.authorization import JWTAuthentication
from trade.user.models import User, Weixin
from trade.user.serializer import UserWeixinSerializer, UserSyncSerializer
from trade.user.validators import WeixinInfoValidator
from trade.utils.mp import MediaPlatform
from trade.utils.myrandom import MyRandom
from trade.resource.models import Resource


# /user 通过微信OAUTH接口, 获取微信用户信息
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
            # 调用OAUTH
            weixin_info = MediaPlatform.get_user_info_from_wechat(code)

            serializer = WeixinInfoValidator(data=weixin_info)
            serializer.is_valid(raise_exception=True)
            openid = serializer.validated_data['openid']
            nickname = serializer.validated_data['nickname']
            headimgurl = serializer.validated_data['headimgurl']

            # 获取用户信息, 不存在则创建
            user = User.objects.filter(weixin__openid=openid).first()
            if not user:
                weixin_fields = {
                    'openid': openid,
                    'nickname': nickname,
                    'headimgurl': headimgurl,
                }
                user_fields = {
                    'weixin': Weixin.objects.create(**weixin_fields),
                    'username': MyRandom.random_digit(length=8),
                    'password': MyRandom.random_digit(length=8),
                    'role': 'user',
                }
                with transaction.atomic():
                    user = User.objects.create(**user_fields)   # create 返回 Model 实例
                    Resource.objects.create(user)

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
