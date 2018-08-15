import json
# 第三方库
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.db import transaction
from rest_framework.renderers import StaticHTMLRenderer
# 自己的库
from trade.utils.payjs import Payjs
from trade.order.models import Orders


class OrderView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        # 获取参数
        tariff_id = request.GET.get('tariff_id')
        #
        attach = json.dumps({'tariff_id': tariff_id})
        print(f'tariff_id: {tariff_id}, attach: {attach}')
        total_fee = 1
        notify_url = f'{settings.API_SERVER_URL}/order/notify'      # 充值状态通知地址
        callback_url = settings.MP_WEB_URL      # 充值后用户跳转地址
        title = '用户支付提示'
        redirect_url, param = Payjs.Cashier(
            total_fee=total_fee, title=title, attach=attach, notify_url=notify_url, callback_url=callback_url
        )
        print(redirect_url)
        # 订单入库
        Orders.objects.create(
            openid='testuser',
            out_trade_no=param['out_trade_no'],
            attach=param['attach'],
            total_fee=param['total_fee'],
            appid='payjs',
            mch_id=param['mchid'],
            status='unpaid',
        )
        data = {'redirect_url': redirect_url}
        return Response(data)


class OrderNotifyView(APIView):
    authentication_classes = ()
    permission_classes = ()
    renderer_classes = (StaticHTMLRenderer,)    # response的content-type方式, 会使用指定类序列化body

    @transaction.atomic
    def post(self, request):
        """
        :param request:
        request.path:  不包含域名 /order/notify
        url参数 request.GET: {}
        form参数 request.POST:
        {
            'attach': ['{"tariff_id": "month1"}'], 'mchid': ['1511573911'], 'openid': ['o7LFAwUGHPZxyNahwjoNQtKh8EME'],
            'out_trade_no': ['1534167177710ovfltv6a8v7BsFAH0'], 'payjs_order_id': ['2018081321325600636471374'],
            'return_code': ['1'], 'time_end': ['2018-08-13 21:33:02'], 'total_fee': ['1'],
             'transaction_id': ['4200000149201808138100178561'], 'sign': ['3BB0F5C8843A16DEE422012A28CB3D47']
        }
        :return:
            APIException(500):     {'detail': ErrorDetail(string='signature not match!', code='invalid_signature')}
            ValidationError(400):  [ErrorDetail(string='signature not match!', code='invalid_signature')]
        """
        openid = request.POST.get('openid')
        total_fee = request.POST.get('total_fee')
        out_trade_no = request.POST.get('out_trade_no')
        payjs_order_id = request.POST.get('payjs_order_id')
        transaction_id = request.POST.get('transaction_id')
        attach = request.POST.get('attach')
        mchid = request.POST.get('mchid')
        sign = request.POST.get('sign')

        # 校验签名. 错误时返回: 400
        cal_sign = Payjs.get_sign(request.POST.dict())
        if sign != cal_sign:
            return Response(data='invalid_signature', status=400)

        # 根据out_trade_no检查数据库订单
        order = Orders.objects.filter(out_trade_no=out_trade_no, total_fee=total_fee).first()
        if not order:
            return Response(data='invalid_order', status=400)

        # TODO 增加使用时长
        order.status = 'paid'
        order.save()
        return Response('success')
