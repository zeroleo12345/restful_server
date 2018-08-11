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
    return [
        (k, d[k]) for k in sorted(d.keys()) if d[k]
    ]


class Payjs(object):
    MERCHANT_ID = settings.PAYJS_MERCHANT_ID      # 商户号
    MERCHANT_KEY = settings.PAYJS_MERCHANT_KEY    # 密码
    # CASHIER_URL = 'https://payjs.cn/api/cashier'    # 收银台地址

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
        """
        PAYJS 签名算法与微信官方签名算法一致, 签名生成的通用步骤如下：
        第一步，设所有发送或者接收到的数据为集合M，将集合M内非空参数值的参数按照参数名ASCII码从小到大排序（字典序），
            使用URL键值对的格式（即key1=value1&key2=value2…）拼接成字符串stringA。
        第二步，在stringA最后拼接上 &key=密钥 得到stringSignTemp字符串，并对stringSignTemp进行MD5运算，
            再将得到的字符串所有字符转换为大写，得到sign值
        :param attributes:
        :return:
        """
        attributes = ksort(attributes)
        m = hashlib.md5()
        m.update((unquote_plus(urlencode(attributes)) + '&key=' + Payjs.MERCHANT_KEY).encode(encoding='utf-8'))
        sign = m.hexdigest()
        sign = sign.upper()
        return sign

    @staticmethod
    def QRPay(total_fee, title, attach=None, notify_url=None):
        """
        用户扫描二维码支付
        :param total_fee: 支付金额, 单位分
        :param title: 订单标题
        :param attach: 用户自定义数据，在notify的时候会原样返回
        :param notify_url: 接收微信支付异步通知的回调地址。必须为可直接访问的URL，不能带参数、session验证、csrf验证。留空则不通知
        :return:
        """
        url = 'https://payjs.cn/api/native'
        data = dict()
        data['out_trade_no'] = Payjs.create_out_trade_no()
        data['mchid'] = Payjs.MERCHANT_ID
        data['total_fee'] = total_fee
        data['body'] = title
        data['notify_url'] = notify_url
        return Payjs._post(data, url)

    @staticmethod
    def Cashier(total_fee, title, attach=None, notify_url=None, callback_url=None):
        """
        用户跳转到收银台支付
        :param total_fee: 支付金额, 单位分
        :param title: 订单标题
        :param attach: 用户自定义数据，在notify的时候会原样返回
        :param notify_url: 接收微信支付异步通知的回调地址。必须为可直接访问的URL，不能带参数、session验证、csrf验证。留空则不通知
        :param callback_url: 用户支付成功后，前端跳转地址。留空则支付后关闭webview
        :return:
            返回字典, 由前端发起 GET请求 到 PayJS收银台
        """
        data = dict()
        data['url'] = "https://payjs.cn/api/cashier"
        data['out_trade_no'] = Payjs.create_out_trade_no()     # 商户自定义交易号
        data['mchid'] = Payjs.MERCHANT_ID
        data['total_fee'] = total_fee
        data['body'] = title
        data['attach'] = attach
        data['notify_url'] = notify_url
        if callback_url:
            data['callback_url'] = callback_url
        return data

    @staticmethod
    def Query(payjs_order_id):
        # 查询订单状态
        url = 'https://payjs.cn/api/check'
        data = dict()
        data['payjs_order_id'] = payjs_order_id
        return Payjs._post(data, url)
