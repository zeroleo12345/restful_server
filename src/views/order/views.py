# 第三方库
from rest_framework.views import APIView
from django.http import HttpResponse
from wechatpy.exceptions import InvalidSignatureException
import sentry_sdk
# 项目库
from trade import settings
from trade.settings import log
from utils.mydjango import get_client_ip
from service.wechat.we_pay import WePay
from models import Order, Tariff, User
from framework.restful import BihuResponse
from framework.authorization import JWTAuthentication
from framework.field import new_uuid
from controls.auth import Authentication
from controls.resource import increase_user_resource


class OrderView(APIView):
    authentication_classes = (JWTAuthentication, )      # 默认配置
    permission_classes = ()

    # /order    下单
    def post(self, request):
        # 获取参数
        auth = Authentication(request)
        tariff_name = request.data.get('tariff_name')
        #
        user = User.get(user_id=auth.user_id)
        tariff = Tariff.get_object_or_404(tariff_name=tariff_name)
        attach = Tariff.tariff_to_attach(tariff=tariff)
        if settings.is_admin(openid=user.openid):
            total_fee = 1 * tariff.duration  # 1分钱
        else:
            total_fee = tariff.price
        title = '用户支付提示'
        client_ip = get_client_ip(request)
        openid = user.openid
        out_trade_no = new_uuid()
        response = WePay.create_jsapi_order(
            out_trade_no=out_trade_no,
            openid=openid, total_fee=total_fee, title=title, client_ip=client_ip, attach=attach, notify_url=settings.MP_PAY_NOTIFY_URL
        )
        prepay_id = response['prepay_id']
        # 订单入库
        order = Order.create(
            user_id=user.user_id,
            platform_id=user.bind_platform_id,
            openid=openid,
            out_trade_no=out_trade_no,
            attach=attach,
            total_fee=total_fee,
            appid=settings.MP_APP_ID,
            mch_id=settings.MP_MERCHANT_ID,
            status=Order.Status.UNPAID.value,
        )
        data = {
            'order': order.to_dict(),
            'param': WePay.get_jsapi_params(prepay_id=prepay_id),
        }
        return BihuResponse(data=data)


class OrderNotifyView(APIView):
    authentication_classes = ()
    permission_classes = ()
    SUCCESS_RESPONSE = HttpResponse(
        content=r'<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>',
        content_type='text/xml',
    )

    # /order/notify     付款结果通知
    def post(self, request):
        log.d(f'we_pay notify. data: {request.body}')
        try:
            # request.data: OrderedDict([(u'appid', u'wx7f843ee17bc2a7b7'), (u'attach', u'{"btype": 0}'), (u'bank_type', u'CFT'), (u'cash_fee', 1), (u'fee_type', u'CNY'), (u'is_subscribe', u'Y'), (u'mch_id', u'1480215992'), (u'nonce_str', u'bZhA1HTmIqBFCluKpai32Yj97tvk4DzV'), (u'openid', u'ovj3E0l9vffwBuqz_PNu25yL_is4'), (u'out_trade_no', u'15021710481087kJMqd36CBz9OqFnK'), (u'result_code', u'SUCCESS'), (u'return_code', u'SUCCESS'), (u'time_end', u'20170808134526'), (u'total_fee', 1), (u'trade_type', u'JSAPI'), (u'transaction_id', u'4005762001201708085135613047'), (u'sign', u'F59843FFFAE5E70A9F1B67D755A372E0')])
            # (Pdb) request.body
            # b'<xml><appid><![CDATA[wx54d296959ee50c0b]]></appid>\n<attach><![CDATA[{"tariff_name": "month1"}]]></attach>\n<bank_type><![CDATA[CFT]]></bank_type>\n<cash_fee><![CDATA[1]]></cash_fee>\n<fee_type><![CDATA[CNY]]></fee_type>\n<is_subscribe><![CDATA[Y]]></is_subscribe>\n<mch_id><![CDATA[1517154171]]></mch_id>\n<nonce_str><![CDATA[dJ1t73xXmCrOjn8z5DP6BKyNqgI0cwvS]]></nonce_str>\n<openid><![CDATA[o0FSR0Zh3rotbOog_b2lytxzKrYo]]></openid>\n<out_trade_no><![CDATA[1540483879395x3Oko4Ta9RWamsQCW]]></out_trade_no>\n<result_code><![CDATA[SUCCESS]]></result_code>\n<return_code><![CDATA[SUCCESS]]></return_code>\n<sign><![CDATA[22BE162C29D8558541F04475C379E18B]]></sign>\n<time_end><![CDATA[20181026001122]]></time_end>\n<total_fee>1</total_fee>\n<trade_type><![CDATA[JSAPI]]></trade_type>\n<transaction_id><![CDATA[4200000206201810263667544938]]></transaction_id>\n</xml>'
            data = WePay.parse_payment_result(request.body)
            out_trade_no = data['out_trade_no']
            attach = data['attach']
            return_code = data['return_code']
            assert return_code == 'SUCCESS'
            transaction_id = data['transaction_id']
            total_fee = data['total_fee']
            # 增加用户免费资源
            increase_user_resource(total_fee, out_trade_no, transaction_id, attach)
            return self.SUCCESS_RESPONSE
        except (InvalidSignatureException, Exception) as e:
            log.e(f'we_pay notify error, body: {request.body}')
            sentry_sdk.capture_exception(e)
            return self.SUCCESS_RESPONSE
