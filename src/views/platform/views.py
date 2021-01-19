# 第三方库
from rest_framework.views import APIView
# 项目库
from models import Platform
from framework.restful import BihuResponse


class PlatformView(APIView):
    authentication_classes = ()
    permission_classes = ()

    # /platform/:platform_id
    def get(self, request, platform_id):
        platform = Platform.get(platform_id=platform_id)
        data = {}
        if platform:
            data = platform.to_dict()
        return BihuResponse(data=data)
