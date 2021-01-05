import datetime
# 第三方库
from rest_framework.views import APIView
from django.db import transaction
# 项目库
from models import Account, User
from service.wechat.we_oauth import WeOAuth
from utils.myrandom import MyRandom
from utils.time import Datetime
from framework.exception import GlobalException
from framework.authorization import JWTAuthentication
from buffer.token import WechatCode
from framework.restful import BihuResponse
# from trade.settings import log


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
        assert user   # TODO 待补充返回码给前端, 提示给用户
        account = Account.get(openid=user.openid, platform_id=user.bind_platform_id)
        if not account:
            username = MyRandom.random_digit(length=8)
            expired_at = Datetime.localtime() + datetime.timedelta(minutes=30)
            user_fields = {
                'user_id': user.id,
                'platform_id': user.bind_platform_id,
                'username': username,
                'password': username,
                'role': 'user',
                'expired_at': expired_at,
            }
            with transaction.atomic():
                account = Account.create(**user_fields)   # create 返回 Model 实例
        if user.nickname != nickname or user.picture_url != avatar:
            user.update(nickname=nickname, picture_url=avatar)
        account_info = account.to_dict()
        user_info = user.to_dict()
        authorization = JWTAuthentication.jwt_encode_handler(user_dict=user_info)
        data = {
            'account': account_info,
            'user': user_info,
            'authorization': authorization,
        }
        return BihuResponse(data=data)


class UserSyncView(APIView):
    authentication_classes = ()
    permission_classes = ()

    # /user/sync    同步用户列表
    def get(self, request):
        accounts = Account.objects.all()
        data = [account.to_dict() for account in accounts]
        return BihuResponse(data=data)
