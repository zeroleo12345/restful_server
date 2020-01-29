# 第三方库
from rest_framework.views import APIView
from django.http import HttpResponse
from django.conf import settings
from django.db import transaction
from wechatpy.exceptions import InvalidSignatureException
import sentry_sdk
# 自己的库
from trade.framework.restful import BihuResponse
from controls.auth import Authentication
from trade.settings import log
from trade.utils.django import get_client_ip
from trade.utils.wepay import WePay
from models import Orders, Tariff
from models import Resource, ResourceChange
from trade.framework.authorization import JWTAuthentication


class OrderView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = ()

    # /order    下单
    def post(self, request):
        # 获取参数
        auth = Authentication(request)
        tariff_name = request.data.get('tariff_name')
        #
        tariff = Tariff.get_object_or_404(tariff_name=tariff_name)
        attach = Tariff.tariff_to_attach(tariff=tariff)
        if auth.openid == settings.MP_ADMIN_OPENID:
            total_fee = 1 * tariff.duration  # 1分钱
        else:
            total_fee = tariff.price
        notify_url = f'{settings.API_SERVER_URL}/order/notify'      # 订单状态通知地址
        title = '用户支付提示'
        client_ip = get_client_ip(request)
        openid = auth.openid
        order_params, jsapi_params = WePay.cashier(
            openid=openid, total_fee=total_fee, title=title, client_ip=client_ip, attach=attach, notify_url=notify_url
        )
        out_trade_no = order_params['out_trade_no']
        attach = order_params['attach']
        # 订单入库
        Orders.objects.create(
            user_id=auth.user_id,
            openid=openid,
            out_trade_no=out_trade_no,
            attach=attach,
            total_fee=total_fee,
            appid=settings.MP_APP_ID,
            mch_id=settings.MP_MERCHANT_ID,
            status='unpaid',
        )
        return BihuResponse(jsapi_params)


# /order/notify
class OrderNotifyView(APIView):
    authentication_classes = ()
    permission_classes = ()

    @classmethod
    def response_success(cls):
        return HttpResponse(
            content="""<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>""",
            content_type='text/xml',
        )

    def post(self, request):
        # 1. 解析微信侧回调请求
        try:
            # data: OrderedDict([(u'appid', u'wx7f843ee17bc2a7b7'), (u'attach', u'{"btype": 0}'), (u'bank_type', u'CFT'), (u'cash_fee', 1), (u'fee_type', u'CNY'), (u'is_subscribe', u'Y'), (u'mch_id', u'1480215992'), (u'nonce_str', u'bZhA1HTmIqBFCluKpai32Yj97tvk4DzV'), (u'openid', u'ovj3E0l9vffwBuqz_PNu25yL_is4'), (u'out_trade_no', u'15021710481087kJMqd36CBz9OqFnK'), (u'result_code', u'SUCCESS'), (u'return_code', u'SUCCESS'), (u'time_end', u'20170808134526'), (u'total_fee', 1), (u'trade_type', u'JSAPI'), (u'transaction_id', u'4005762001201708085135613047'), (u'sign', u'F59843FFFAE5E70A9F1B67D755A372E0')])
            # SUCCESS 和 FAIL: out_trade_no, attach附加值
            xml = request.body
            # (Pdb) request.body
            # b'<xml><appid><![CDATA[wx54d296959ee50c0b]]></appid>\n<attach><![CDATA[{"tariff_name": "month1"}]]></attach>\n<bank_type><![CDATA[CFT]]></bank_type>\n<cash_fee><![CDATA[1]]></cash_fee>\n<fee_type><![CDATA[CNY]]></fee_type>\n<is_subscribe><![CDATA[Y]]></is_subscribe>\n<mch_id><![CDATA[1517154171]]></mch_id>\n<nonce_str><![CDATA[dJ1t73xXmCrOjn8z5DP6BKyNqgI0cwvS]]></nonce_str>\n<openid><![CDATA[o0FSR0Zh3rotbOog_b2lytxzKrYo]]></openid>\n<out_trade_no><![CDATA[1540483879395x3Oko4Ta9RWamsQCW]]></out_trade_no>\n<result_code><![CDATA[SUCCESS]]></result_code>\n<return_code><![CDATA[SUCCESS]]></return_code>\n<sign><![CDATA[22BE162C29D8558541F04475C379E18B]]></sign>\n<time_end><![CDATA[20181026001122]]></time_end>\n<total_fee>1</total_fee>\n<trade_type><![CDATA[JSAPI]]></trade_type>\n<transaction_id><![CDATA[4200000206201810263667544938]]></transaction_id>\n</xml>'
            data = WePay.WECHAT_PAY.parse_payment_result(xml)
        except (InvalidSignatureException, Exception) as exc:
            sentry_sdk.capture_exception(exc)
            return self.response_success()

        out_trade_no = data['out_trade_no']
        attach = data['attach']
        log.i(f'wepay order notify, out_trade_no: {out_trade_no}, attach: {attach}')

        return_code = data['return_code']
        if return_code != 'SUCCESS':
            return_msg = data.get('return_msg', '')
            log.e(f'wepay fail, return_msg: {return_msg}')
            return self.response_success()

        openid = data['openid']
        transaction_id = data['transaction_id']
        total_fee = data['total_fee']
        log.i(f'openid: {openid}, transaction_id: {transaction_id}, total_fee: {total_fee}')

        # 增加用户免费资源
        OrderNotifyView.increase_user_resource(total_fee, out_trade_no, transaction_id, attach)
        return self.response_success()

    @staticmethod
    def increase_user_resource(total_fee, out_trade_no, transaction_id, attach):
        # 根据out_trade_no检查数据库订单
        order = Orders.objects.filter(out_trade_no=out_trade_no, total_fee=total_fee).select_related('user').first()
        if not order:
            log.e(f'order not exist')
            return
        # 去重逻辑
        if order.is_paid():
            log.w(f'order notify duplicate')
            return

        # 计算时长叠加
        user = order.user
        resource = Resource.objects.get(user=user)
        tariff = Tariff.attach_to_tariff(attach)
        before = resource.expired_at
        after = tariff.increase_duration(before)

        with transaction.atomic():
            # 变更免费资源
            resource.expired_at = after
            resource.save()
            # 变更订单状态 和 微信订单号
            order.status = 'paid'
            order.transaction_id = transaction_id
            order.save()
            # 插入免费资源历史变更表
            ResourceChange.objects.create(user=user, orders=order, before=before, after=after)
