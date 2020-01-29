from rest_framework.views import APIView
# 自己的库
from trade.framework.authorization import JWTAuthentication
from models import Resource
from resource.serializer import ResourceSerializer


# /resource
class UserResourceView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = ()
    serializer_class = ResourceSerializer

    def get(self):
        user = self.request.user
        resource = Resource.objects.get(user=user)
        data = ResourceSerializer(resource).data
        return data
