from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
# 自己的库
from trade.utils.payjs import Payjs


class OrderView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        total_fee = 1
        notify_url = f'{settings.MP_WEB_URL}/order/notify'
        redirect_url = Payjs.Cashier(total_fee=total_fee, title='test', attach=None, notify_url=notify_url)
        data = {'redirect_url': redirect_url}
        # TODO 测试 notify_url 回调通知是否携带 attach ?
        return Response(data)


class OrderNotifyView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        print(request.path)
        print(request.POST)
        print(request.body)
        return Response()
