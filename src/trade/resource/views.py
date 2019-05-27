from rest_framework import generics
# 自己的库
from trade.framework.authorization import JWTAuthentication, UserPermission
from trade.resource.models import Resource
from trade.resource.serializer import ResourceSerializer


# /resource
class UserResourceView(generics.RetrieveAPIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = (UserPermission, )             # 默认配置
    serializer_class = ResourceSerializer

    def get_object(self):
        user = self.request.user
        resource, is_created = Resource.objects.get(user=user)
        return resource
