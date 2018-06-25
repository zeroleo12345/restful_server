from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import exceptions

from trade.user.models import User
from trade.user.serializer import UserSerializer, UserInfoFromWechatFormSerializer
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
    serializer_class = UserSerializer

    def get_object(self):
        code = self.request.GET.get('code', '')
        if not code:
            raise exceptions.ValidationError('code字段不能为空', 'invalid_code')

        user_info = MP.get_user_info_from_wechat(code)

        serializer = UserInfoFromWechatFormSerializer(data=user_info)
        serializer.is_valid(raise_exception=True)

        openid = serializer.validated_data['openid']
        nickname = serializer.validated_data['nickname']
        headimgurl = serializer.validated_data['headimgurl']
        defaults = {
            'nickname': nickname,
            'headimgurl': headimgurl,
            'username': 'username',
            'password': 'password',
            'is_enable': True,
            'role': 'user',
        }
        user, is_created = User.objects.get_or_create(openid=openid, defaults=defaults)

        return user
