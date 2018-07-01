from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import exceptions

from trade.framework.authorization import JWTAuthentication
from trade.user.models import Weixin, User
from trade.user.serializer import UserWeixinSerializer, WeixinInfoValidator
from trade.utils.mp import MP


class UnusedView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
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
            weixin_info = MP.get_user_info_from_wechat(code)

            serializer = WeixinInfoValidator(data=weixin_info)
            serializer.is_valid(raise_exception=True)
            openid = serializer.validated_data['openid']
            nickname = serializer.validated_data['nickname']
            headimgurl = serializer.validated_data['headimgurl']

            user = User.objects.filter(weixin__openid=openid).first()
            if not user:
                user = self.create_new_user(openid, nickname, headimgurl)

        self.request.user = user
        return user

    @staticmethod
    def create_new_user(openid, nickname, headimgurl):
        weixin_fields = {
            'openid': openid,
            'nickname': nickname,
            'headimgurl': headimgurl,
        }
        user_fields = {
            'weixin': Weixin.objects.create(**weixin_fields),
            'username': 'username',
            'password': 'password',
            'role': 'user',
        }
        return User.objects.create(**user_fields)
