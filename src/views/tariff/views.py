from rest_framework.views import APIView
# 项目库
from framework.authorization import JWTAuthentication
from framework.restful import BihuResponse
from models import Tariffs


class TariffsView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = ()

    # /tariff     获取所有套餐
    def get(self, request):
        #
        tariffs = Tariffs.all
        data = []
        for t in tariffs:
            data.append(t.to_dict())
        return BihuResponse(data=data)
