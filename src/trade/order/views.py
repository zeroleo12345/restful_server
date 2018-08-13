import json
# 第三方库
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
# 自己的库
from trade.utils.payjs import Payjs


class OrderView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        tariff_id = request.GET.get('tariff_id')
        attach = json.dumps({'tariff_id': tariff_id})
        print(f'tariff_id: {tariff_id}, attach: {attach}')
        total_fee = 1
        notify_url = f'{settings.API_SERVER_URL}/order/notify'      # 充值后回调地址
        callback_url = settings.MP_WEB_URL
        title = '用户支付提示'
        redirect_url, param = Payjs.Cashier(
            total_fee=total_fee, title=title, attach=attach, notify_url=notify_url, callback_url=callback_url
        )
        print(redirect_url)
        data = {'redirect_url': redirect_url}
        return Response(data)


class OrderNotifyView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        """
        :param request:
        request.POST: {
            'attach': ['{"tariff_id": "month1"}'], 'mchid': ['1511573911'], 'openid': ['o7LFAwUGHPZxyNahwjoNQtKh8EME'],
            'out_trade_no': ['1534167177710ovfltv6a8v7BsFAH0'], 'payjs_order_id': ['2018081321325600636471374'],
            'return_code': ['1'], 'time_end': ['2018-08-13 21:33:02'], 'total_fee': ['1'],
             'transaction_id': ['4200000149201808138100178561'], 'sign': ['3BB0F5C8843A16DEE422012A28CB3D47']
        }
        :return:
        """
        print(request.path)     # 不包含域名: /order/notify
        print(request.POST)
        return Response()
