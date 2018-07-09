from rest_framework.response import Response
from rest_framework.views import APIView

from trade.utils.mp import WeixinPay


class OrderView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        notify_url = 'https://api.lynatgz.cn/order/notify'
        result = WeixinPay.cashier(total_fee=1, title='test', attach=None, notify_url=None)
        # TODO 测试 notify_url 回调通知是否血袋 attach ?
        if result:
            print(result.redirect)         # 要跳转到的收银台网址
        else:
            print(result.error_msg)        # 错误信息
            print(result)
        return Response()


class OrderNotifyView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        print(request.path)
        print(request.POST)
        print(request.body)
        return Response()
