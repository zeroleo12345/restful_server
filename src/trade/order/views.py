# 第三方库
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.db import transaction
from rest_framework.renderers import StaticHTMLRenderer
# 自己的库
from trade.utils.django import get_client_ip
from trade.utils.wepay import WePay
from trade.order.models import Orders, Tariff
from trade.resource.models import Resource, ResourceChange
from trade.framework.authorization import JWTAuthentication, UserPermission


class OrderView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = (UserPermission, )             # 默认配置

    def post(self, request):
        # 获取参数
        user = request.user
        tariff_name = request.data.get('tariff_name')
        #
        tariff = Tariff.get_object_or_404(tariff_name=tariff_name)
        attach = Tariff.tariff_to_attach(tariff=tariff)
        print(f'tariff_name: {tariff_name}, attach: {attach}')
        total_fee = tariff.price
        notify_url = f'{settings.API_SERVER_URL}/order/notify'      # 充值状态通知地址
        title = '用户支付提示'
        client_ip = get_client_ip(request)
        openid = user.weixin.openid
        data = WePay.Cashier(
            openid=openid, total_fee=total_fee, title=title, client_ip=client_ip, attach=attach, notify_url=notify_url
        )
        out_trade_no = '123'
        attach = '123'
        # 订单入库
        Orders.objects.create(
            user=user,
            openid=openid,
            out_trade_no=out_trade_no,
            attach=attach,
            total_fee=total_fee,
            appid=settings.MP_APP_ID,
            mch_id=settings.MP_MERCHANT_ID,
            status='unpaid',
        )
        return Response(data)


class OrderNotifyView(APIView):
    authentication_classes = ()
    permission_classes = ()
    renderer_classes = (StaticHTMLRenderer,)    # response的content-type方式, 会使用指定类序列化body

    def post(self, request):
        """
        :param request:
        request.path:  不包含域名 /order/notify
        url参数 request.GET: {}
        form参数 request.POST:
        {
             'attach': ['{"tariff_name": "month1"}'], 'mchid': ['1511573911'],
             'openid': ['o7LFAwUGHPZxyNahwjoNQtKh8EME'],
             'out_trade_no': ['1534167177710ovfltv6a8v7BsFAH0'], 'payjs_order_id': ['2018081321325600636471374'],
             'return_code': ['1'], 'time_end': ['2018-08-13 21:33:02'], 'total_fee': ['1'],
             'transaction_id': ['4200000149201808138100178561'], 'sign': ['3BB0F5C8843A16DEE422012A28CB3D47']
        }
        :return:
            因为是返回给PayJS服务器, 是text/html类型, 非application/json类型
            APIException(500):     {'detail': ErrorDetail(string='signature not match!', code='invalid_signature')}
            ValidationError(400):  [ErrorDetail(string='signature not match!', code='invalid_signature')]
        """
        # openid = request.POST.get('openid')
        total_fee = request.POST.get('total_fee')
        out_trade_no = request.POST.get('out_trade_no')
        # payjs_order_id = request.POST.get('payjs_order_id')
        # transaction_id = request.POST.get('transaction_id')
        attach = request.POST.get('attach')
        # mchid = request.POST.get('mchid')
        sign = request.POST.get('sign')

        # 校验签名. 错误时返回: 400
        cal_sign = WePay.get_sign(request.POST.dict())
        if sign != cal_sign:
            return Response(data='invalid_signature', status=400)

        # 根据out_trade_no检查数据库订单
        order = Orders.objects.filter(out_trade_no=out_trade_no, total_fee=total_fee).select_related('user').first()
        if not order:
            return Response(data='invalid_order', status=400)
        # 去重逻辑
        if order.is_paid():
            return Response('success')

        user = order.user
        resource, is_created = Resource.objects.get_or_create(user=user)
        tariff = Tariff.attach_to_tariff(attach)
        before = resource.expired_at
        after = tariff.increase_duration(before)

        with transaction.atomic():
            resource.expired_at = after
            resource.save()
            order.status = 'paid'
            order.save()
            ResourceChange.objects.create(user=user, orders=order, before=before, after=after)
        return Response('success')
