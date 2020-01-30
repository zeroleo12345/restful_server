import time
import hashlib
from urllib.parse import urlencode, unquote_plus, urlparse, parse_qsl, urlunparse
# 第三方库
from dynaconf import settings
import requests
# 自己的库
from trade.utils.myrandom import MyRandom

# 参考:   https://gist.github.com/motord/c0d6979d7685708b02950216290e255f

# PayJS
PAYJS_MERCHANT_ID = settings.get('PAYJS_MERCHANT_ID', default=None)     # payjs 商户号
PAYJS_MERCHANT_KEY = settings.get('PAYJS_MERCHANT_KEY', default=None)   # payjs API密钥


def url_join_param(host, params):
    """
    :param host: 域名
    :param params: url参数, 类型为字典
    :return: 以"?"连接参数后的url
    """
    url_parts = list(urlparse(host))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def ksort(d):
    return [
        (k, d[k]) for k in sorted(d.keys()) if d[k]
    ]


class Payjs(object):
    MERCHANT_ID = PAYJS_MERCHANT_ID      # 商户号
    MERCHANT_KEY = PAYJS_MERCHANT_KEY    # 密码
    CASHIER_URL = 'https://payjs.cn/api/cashier'  # 收银台URL

    @staticmethod
    def _get(url):
        return requests.get(url)

    @staticmethod
    def _post(url, data):
        return requests.post(url, data=data)

    @staticmethod
    def create_out_trade_no():
        return ''.join((
            str(int(time.time()*1000)),
            MyRandom.random_string(17, lowercase=True, uppercase=True)
        ))

    @staticmethod
    def get_sign(attributes):
        """
        PAYJS 签名算法与微信官方签名算法一致, 签名生成的通用步骤如下：
        第一步，设所有发送或者接收到的数据为集合M，将集合M内非空参数值的参数按照参数名ASCII码从小到大排序（字典序），
            使用URL键值对的格式（即key1=value1&key2=value2…）拼接成字符串stringA。
        第二步，在stringA最后拼接上 &key=密钥 得到stringSignTemp字符串，并对stringSignTemp进行MD5运算，
            再将得到的字符串所有字符转换为大写，得到sign值

        :param attributes: 属性字典
        :return:
        """
        attributes.pop('sign', None)
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
        # 清理空值, 计算签名
        data = {k: v for k, v in data.items() if v}
        data['sign'] = Payjs.get_sign(data)
        return Payjs._post(url, data)

    @staticmethod
    def cashier(total_fee, title, attach=None, notify_url=None, callback_url=None):
        """
        用户跳转到收银台支付. (Note: 并没有实际调用接口)
        :param total_fee: 支付金额, 单位分
        :param title: 订单标题
        :param attach: 用户自定义数据，在notify的时候会原样返回
        :param notify_url: 接收微信支付异步通知的回调地址。必须为可直接访问的URL，不能带参数、session验证、csrf验证。留空则不通知
        :param callback_url: 用户支付成功后，前端跳转地址。留空则支付后关闭webview
        :return:
            返回PayJS收银台URL, 由前端发起 GET请求 重定向到 PayJS收银台
        """
        param = dict()
        param['out_trade_no'] = Payjs.create_out_trade_no()     # 商户自定义交易号
        param['mchid'] = Payjs.MERCHANT_ID
        param['total_fee'] = total_fee
        param['body'] = title
        param['attach'] = attach
        param['notify_url'] = notify_url
        if callback_url:
            param['callback_url'] = callback_url
        # 清理空值
        param = {k: v for k, v in param.items() if v}
        param['sign'] = Payjs.get_sign(param)
        url = url_join_param(Payjs.CASHIER_URL, param)
        return url, param

    @staticmethod
    def query(payjs_order_id):
        # 查询订单状态
        url = 'https://payjs.cn/api/check'
        data = dict()
        data['payjs_order_id'] = payjs_order_id
        # 清理空值, 计算签名
        data = {k: v for k, v in data.items() if v}
        data['sign'] = Payjs.get_sign(data)
        return Payjs._post(url, data)
