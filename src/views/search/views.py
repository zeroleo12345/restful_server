from rest_framework.views import APIView
# 项目库
from framework.authorization import JWTAuthentication
from controls.auth import Authentication
from framework.restful import BihuResponse
from models import Account


class SearchView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = ()

    # /resource     获取免费资源
    def get(self, request):
        auth = Authentication(request)
        account = Account.get(id=auth.user_id)
        data = account.to_dict()
        data['status'] = account.get_resource_status()
        return BihuResponse(data=data)
