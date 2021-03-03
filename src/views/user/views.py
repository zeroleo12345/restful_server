# 第三方库
from rest_framework.views import APIView
# 项目库
from models import Account, User, Platform
from service.wechat.we_oauth import WeOAuth
from framework.exception import GlobalException
from framework.authorization import JWTAuthentication
from buffer.token import WechatCode
from framework.restful import BihuResponse
from trade import settings
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
        if not user:
            return BihuResponse({'code': 'resource_gone', 'message': '请用已缴费的微信号登录'}, status=410)
        account = Account.get(user_id=user.user_id, platform_id=user.bind_platform_id)
        if not account:
            return BihuResponse({'code': 'resource_gone', 'message': '账户不存在, 请联系管理员'}, status=410)
        if user.nickname != nickname or user.picture_url != avatar:
            user.update(nickname=nickname, picture_url=avatar)
        platform = Platform.get(platform_id=user.bind_platform_id)
        account_info = account.to_dict()
        user_info = user.to_dict()
        platform_info = platform.to_dict() if platform else None
        authorization = JWTAuthentication.jwt_encode_handler(user_dict=user_info)
        data = {
            'account': account_info,
            'user': user_info,
            'platform': platform_info,
            'authorization': authorization,
        }
        return BihuResponse(data=data)


class UserSyncView(APIView):
    authentication_classes = ()
    permission_classes = ()

    # /user/sync    同步用户列表
    def get(self, request):
        # 查出所有 platform_id = 1 的用户
        accounts = Account.objects.filter(platform_id=settings.ADMIN_PLATFORM_ID)
        data = [account.to_dict() for account in accounts]
        return BihuResponse(data=data)
