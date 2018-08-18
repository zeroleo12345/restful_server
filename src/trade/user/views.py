from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import exceptions
# 自己的库
from trade.framework.authorization import JWTAuthentication, UserPermission
from trade.user.models import User, Resource
from trade.user.serializer import UserWeixinSerializer, WeixinInfoValidator, ResourceSerializer
from trade.utils.mp import MediaPlatform


class TestView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        token = self.request.META.get('HTTP_AUTHORIZATION', '')
        if token:
            print(f'11111111111111111: {token}')
            user = JWTAuthentication.jwt_decode_handler(token)
            print(f'22222222222222222: {user}')
        return Response()

    def post(self, request):
        return Response()


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
            weixin_info = MediaPlatform.get_user_info_from_wechat(code)

            serializer = WeixinInfoValidator(data=weixin_info)
            serializer.is_valid(raise_exception=True)
            openid = serializer.validated_data['openid']
            nickname = serializer.validated_data['nickname']
            headimgurl = serializer.validated_data['headimgurl']

            user = User.get_or_create_user(openid, nickname, headimgurl)

        self.request.user = user    # 用于Response时, 设置JsonWebToken
        return user


class UserResourceView(generics.RetrieveAPIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = (UserPermission, )             # 默认配置
    serializer_class = ResourceSerializer

    def get_object(self):
        # TODO webstorm 未改造
        user = self.request.user
        resource, is_created = Resource.objects.get_or_create(user=user)
        return resource
