from rest_framework.response import Response
from rest_framework.views import APIView

from trade.utils.payjs import Payjs


class OrderView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        notify_url = 'https://api.lynatgz.cn/order/notify'
        result = Payjs.cashier(total_fee=1, title='test', attach=None, notify_url=None)
        # TODO 测试 notify_url 回调通知是否血袋 attach ?
        redirect_url = ''
        if result:
            redirect_url = result.redirect         # 要跳转到的收银台网址
        else:
            print(result.error_msg)        # 错误信息
            print(result)
        data = {
            'redirect_url': redirect_url
        }
        return Response(data)


class OrderNotifyView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        print(request.path)
        print(request.POST)
        print(request.body)
        return Response()
