from rest_framework.views import APIView
# 项目库
from framework.authorization import JWTAuthentication
from controls.auth import Authentication
from framework.restful import BihuResponse
from models import Account, User
from trade.settings import log


class AccountView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = ()

    # /account     获取免费资源
    def get(self, request):
        auth = Authentication(request)
        #
        log.i(f'user_id: {auth.user_id}')
        user = User.get(user_id=auth.user_id)
        account = Account.get(user_id=user.user_id, platform_id=user.bind_platform_id)
        data = account.to_dict()
        return BihuResponse(data=data)
