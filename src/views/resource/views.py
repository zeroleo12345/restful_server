from rest_framework.views import APIView
# 项目库
from framework.authorization import JWTAuthentication
from models import Resource
from views.resource.serializer import ResourceSerializer
from controls.auth import Authentication
from framework.restful import BihuResponse


class UserResourceView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = ()

    # /resource     获取免费资源
    def get(self, request):
        auth = Authentication(request)
        resource = Resource.objects.get(user_id=auth.user_id)
        data = ResourceSerializer(resource).data
        return BihuResponse(data=data)
