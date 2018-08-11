import time
import hashlib
from urllib.parse import urlencode, unquote_plus
# 第三方库
import requests
from django.conf import settings
# 自己的库
from trade.utils.myrandom import MyRandom

# 参考:   https://gist.github.com/motord/c0d6979d7685708b02950216290e255f


def ksort(d):
    return [(k, d[k]) for k in sorted(d.keys())]


class Payjs(object):
    MERCHANT_ID = settings.PAYJS_MERCHANT_ID      # 商户号
    MERCHANT_KEY = settings.PAYJS_MERCHANT_KEY    # 密码

    @staticmethod
    def _post(data, url):
        data['sign'] = Payjs.sign(data)
        return requests.post(url, data=data)

    @staticmethod
    def create_out_trade_no():
        return ''.join((
            str(int(time.time()*1000)),
            MyRandom.random_string(17)
        ))

    @staticmethod
    def sign(attributes):
        attributes = ksort(attributes)
        m = hashlib.md5()
        m.update((unquote_plus(urlencode(attributes)) + '&key=' + Payjs.MERCHANT_KEY).encode(encoding='utf-8'))
        sign = m.hexdigest()
        sign = sign.upper()
        return sign

    @staticmethod
    def QRPay(total_fee, body, notify_url):
        # 用户扫描二维码支付
        url = 'https://payjs.cn/api/native'
        data = dict()
        data['mchid'] = Payjs.MERCHANT_ID
        data['total_fee'] = total_fee
        data['body'] = body
        data['out_trade_no'] = Payjs.create_out_trade_no()
        data['notify_url'] = notify_url
        return Payjs._post(data, url)

    @staticmethod
    def JSPay(total_fee, body, callback_url=None):
        url = 'https://payjs.cn/api/jspay'
        data = dict()
        data['mchid'] = Payjs.MERCHANT_ID
        data['total_fee'] = total_fee
        data['body'] = body
        data['out_trade_no'] = Payjs.create_out_trade_no()
        if callback_url:
            data['callback_url'] = callback_url
        return Payjs._post(data, url)

    @staticmethod
    def Cashier(total_fee, body, callback_url=None):
        """
        用户跳转到收银台支付
        :param total_fee: 支付金额, 单位分
        :param body: 支付前台给用户的tips
        :param callback_url: 支付结果回调地址
        :return:
        """
        url = 'https://payjs.cn/api/cashier'
        data = dict()
        data['mchid'] = Payjs.MERCHANT_ID
        data['total_fee'] = total_fee
        data['body'] = body
        data['out_trade_no'] = Payjs.create_out_trade_no()     # 商户自定义交易号
        if callback_url:
            data['callback_url'] = callback_url
        return Payjs._post(data, url)

    @staticmethod
    def Query(payjs_order_id):
        # 查询订单状态
        url = 'https://payjs.cn/api/check'
        data = dict()
        data['payjs_order_id'] = payjs_order_id
        return Payjs._post(data, url)
