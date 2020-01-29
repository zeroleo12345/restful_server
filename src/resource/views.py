from rest_framework.views import APIView
# 自己的库
from trade.framework.authorization import JWTAuthentication
from models import Resource
from resource.serializer import ResourceSerializer
from controls.auth import Authentication
from trade.framework.restful import BihuResponse


class UserResourceView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = ()

    # /resource     获取免费资源
    def get(self, request):
        auth = Authentication(request)
        resource = Resource.objects.get(user_id=auth.user_id)
        data = ResourceSerializer(resource).data
        return BihuResponse(data=data)
