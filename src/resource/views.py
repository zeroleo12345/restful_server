from rest_framework import generics
# 自己的库
from trade.framework.authorization import JWTAuthentication, UserPermission
from models.models import Resource
from resource import ResourceSerializer


# /resource
class UserResourceView(generics.RetrieveAPIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = (UserPermission, )             # 默认配置
    serializer_class = ResourceSerializer

    def get_object(self):
        user = self.request.user
        resource = Resource.objects.get(user=user)
        return resource
