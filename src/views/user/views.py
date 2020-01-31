from rest_framework.views import APIView
from django.db import transaction
# 项目库
from models import User
from service.wechat.we_oauth import WeOAuth
from utils.myrandom import MyRandom
from framework.exception import GlobalException
from framework.authorization import JWTAuthentication
from buffer.token import WechatCode
from framework.restful import BihuResponse


class UserView(APIView):
    authentication_classes = ()
    permission_classes = ()

    # /user     通过微信oauth2接口, 获取微信用户信息
    def get(self, request):
        code = request.GET.get('code', '')
        if not code:
            raise GlobalException(data={'code': 'invalid_code', 'message': f'code字段不能为空'}, status=400)
        openid, nickname, avatar = WechatCode.get(code)    # https://blog.csdn.net/limenghua9112/article/details/81911658
        if not openid:
            openid, nickname, avatar = WeOAuth.get_user_info(code=code)
            if not openid:
                raise GlobalException(data={'code': 'invalid_code', 'message': f'code无效, 请退出重试'}, status=400)
            WechatCode.set(code, openid=openid, nickname=nickname, avatar=avatar)
        # 获取用户信息, 不存在则创建
        user = User.get(openid=openid)
        if not user:
            username = MyRandom.random_digit(length=8)
            user_fields = {
                'openid': openid,
                'nickname': nickname,
                'headimgurl': avatar,
                'username': username,
                'password': username,
                'role': 'user',
            }
            with transaction.atomic():
                user = User.create(**user_fields)   # create 返回 Model 实例
        user_info = user.to_dict()
        authorization = JWTAuthentication.jwt_encode_handler(user_dict=user_info)
        data = {
            'user': user_info,
            'authorization': authorization,
        }
        return BihuResponse(data=data)


class UserSyncView(APIView):
    authentication_classes = ()
    permission_classes = ()

    # /user/sync    同步用户列表
    def get(self, request):
        users = User.objects.all()
        data = [user.to_dict() for user in users]
        return BihuResponse(data=data)
