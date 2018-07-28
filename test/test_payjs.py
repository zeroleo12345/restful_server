# *-* coding: UTF-8 *-*

import hashlib
import requests
from urllib.parse import urlencode, unquote_plus


def ksort(d):
    return [(k, d[k]) for k in sorted(d.keys())]


class Payjs(object):
    def __init__(self, merchant_id, merchant_key, notify_url, **kwargs):
        self.merchant_key = merchant_key  # 填写通信密钥
        self.merchant_id = merchant_id  # 特写商户号
        self.notify_url = notify_url

    def post(self, data, url):
        data['sign'] = self.sign(data)
        return requests.post(url, data=data)

    def sign(self, attributes):
        attributes = ksort(attributes)
        m = hashlib.md5()
        m.update((unquote_plus(urlencode(attributes)) + '&key=' + self.merchant_key).encode(encoding='utf-8'))
        sign = m.hexdigest()
        sign = sign.upper()
        return sign

    def QRPay(self, total_fee, body, out_trade_no):
        # 用户扫描二维码支付
        url = 'https://payjs.cn/api/native'
        data = {}
        data['mchid'] = self.merchant_id
        data['total_fee'] = total_fee
        data['body'] = body
        data['out_trade_no'] = out_trade_no
        data['notify_url'] = self.notify_url
        return self.post(data, url)

    def JSPay(self, total_fee, body, out_trade_no, callback_url=None):
        url = 'https://payjs.cn/api/jspay'
        data = {}
        data['mchid'] = self.merchant_id
        data['total_fee'] = total_fee
        data['body'] = body
        data['out_trade_no'] = out_trade_no
        # data['notify_url'] = self.notify_url
        if callback_url:
            data['callback_url'] = callback_url
        return self.post(data, url)

    def Cashier(self, total_fee, body, out_trade_no, callback_url=None):
        # 用户跳转到收银台支付
        url = 'https://payjs.cn/api/cashier'
        data = {}
        data['mchid'] = self.merchant_id
        data['total_fee'] = total_fee
        data['body'] = body
        data['out_trade_no'] = out_trade_no
        # data['notify_url'] = self.notify_url
        if callback_url:
            data['callback_url'] = callback_url
        return self.post(data, url)

    def Query(self, payjs_order_id):
        # 查询订单状态
        url = 'https://payjs.cn/api/check'
        data = {}
        data['payjs_order_id'] = payjs_order_id
        return self.post(data, url)

def Usage():
    payjs = Payjs(merchant_id='XXXX', merchant_key='xxxxxxxx', notify_url='http://xxx.com/callback');
    rst = payjs.QRPay(total_fee=100, body='TEST', out_trade_no='1001');
