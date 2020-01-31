# 第三方库
from trade import settings
from wechatpy.pay import WeChatPay
from wechatpy.exceptions import WeChatPayException
from wechatpy.utils import check_signature
# 项目库
from framework.field import BaseEnum


class WePay(object):
    check_signature = check_signature
    _pay_api = WeChatPay(
        appid=settings.MP_APP_ID,
        api_key=settings.MP_APP_KEY,
        mch_id=settings.MP_MERCHANT_ID,
        sub_mch_id=None if not settings.MP_SUB_MERCHANT_ID else settings.MP_SUB_MERCHANT_ID,
        mch_cert=settings.MP_MERCHANT_CERT,
        mch_key=settings.MP_MERCHANT_KEY,
        timeout=10,
        sandbox=settings.MP_PAY_SANDBOX,
    )

    class TradeState(BaseEnum):
        PAID = 'SUCCESS'            # 支付成功
        REFUND = 'REFUND'           # 转入退款
        NOTPAY = 'NOTPAY'           # 未支付
        CLOSED = 'CLOSED'           # 已关闭
        REVOKED = 'REVOKED'         # 已撤销. (付款码支付)
        USERPAYING = 'USERPAYING'   # 用户支付中. (付款码支付)
        PAYERROR = 'PAYERROR'       # 支付失败. (其他原因，如银行返回失败)

    @classmethod
    def create_jsapi_order(cls, out_trade_no, total_fee, title, openid, client_ip, attach=None, notify_url=None):
        """
        用户点击button跳转到收银台支付.
        :param out_trade_no:
        :param total_fee: 支付金额, 单位分
        :param title: 订单标题
        :param openid: 缴费用户的openid. 当trade_type=JSAPI, 此参数必传, 且是授权给公众号的用户openid
        :param client_ip: APP和网页支付提交用户端ip, Native支付填调用微信支付API的机器IP
        :param attach: 用户自定义数据，在notify的时候会原样返回
        :param notify_url: 接收微信支付异步通知的回调地址。必须为可直接访问的URL，不能带参数、session验证、csrf验证。不能留空!
        """
        # 统一下单. 微信官方参数地址:  https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
        order_params = {
            'trade_type': 'JSAPI',      # 交易类型 JSAPI--公众号支付, NATIVE--原生扫码支付, APP--app支付, 而MICROPAY--刷卡支付有单独的支付接口, 不能调用统一下单接口
            'body': title,              # 商品描述
            'total_fee': total_fee,     # 订单金额. (单位分)
            'attach': attach,
            'user_id': openid,          # 可选. 缴费用户的openid. 当trade_type=JSAPI, 此参数必传
            'client_ip': client_ip,     # 可选. APP和网页支付提交用户端ip, Native支付填调用微信支付API的机器IP
            'out_trade_no': out_trade_no,
            'detail': None,             # 可选, 商品详情
            'fee_type': 'CNY',          # 可选, 符合ISO 4217标准的三位字母代码, 默认人民币: CNY
            'time_start': None,         # 可选, 订单生成时间, 默认为当前时间
            'time_expire': None,        # 可选, 订单失效时间, 默认为订单生成时间后两小时
            'goods_tag': None,          # 可选, 商品标记, 代金券或立减优惠功能的参数
            'product_id': None,         # 可选, 当trade_type=NATIVE, 此参数必传. 此id为二维码中包含的商品ID, 商户自行定义
            'device_info': None,        # 可选, 终端设备号(门店号或收银设备ID), 注意:PC网页或公众号内支付请传"WEB"
            'limit_pay': None,          # 可选, 指定支付方式, no_credit-指定不能使用信用卡支付
            'notify_url': notify_url,   # 订单通知地址
        }

        # 统一下单, 生成微信支付参数返回给微信浏览器
        response = cls._pay_api.order.create(**order_params)
        # OrderedDict([('return_code', 'SUCCESS'),
        #              ('return_msg', 'OK'),
        #              ('appid', 'wx14d296959ee50c0b'),
        #              ('mch_id', '1517154171'),
        #              ('nonce_str', 'RDX6pxz2GTEdoQnE'),
        #              ('sign', '796CC22F8EDD664372BE9ACF7EB68ACD'),
        #              ('result_code', 'SUCCESS'),
        #              ('prepay_id', 'wx242238115691612efb08d4092661275602'),
        #              ('trade_type', 'JSAPI')])
        return response

    @classmethod
    def create_native_order(cls, out_trade_no, total_fee, title, product_id, client_ip, attach=None, notify_url=None):
        """
        用户扫码支付.
        :param out_trade_no:
        :param total_fee: 支付金额, 单位分
        :param title: 订单标题
        :param product_id: 当trade_type=NATIVE, 此参数必传. 此id为二维码中包含的商品ID, 商户自行定义. (实测None也可以)
        :param client_ip: APP和网页支付提交用户端ip, Native支付填调用微信支付API的机器IP
        :param attach: 用户自定义数据，在notify的时候会原样返回
        :param notify_url: 接收微信支付异步通知的回调地址。必须为可直接访问的URL，不能带参数、session验证、csrf验证。不能留空!
        """
        # 统一下单. 微信官方参数地址:  https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=9_1
        order_params = {
            'trade_type': 'NATIVE',      # 交易类型 JSAPI--公众号支付, NATIVE--原生扫码支付, APP--app支付, 而MICROPAY--刷卡支付有单独的支付接口, 不能调用统一下单接口
            'body': title,              # 商品描述
            'total_fee': total_fee,     # 订单金额. (单位分)
            'attach': attach,
            'user_id': None,            # 可选. 缴费用户的openid. 当trade_type=JSAPI, 此参数必传
            'client_ip': client_ip,     # 可选. APP和网页支付提交用户端ip, Native支付填调用微信支付API的机器IP
            'out_trade_no': out_trade_no,
            'detail': None,             # 可选, 商品详情
            'fee_type': 'CNY',          # 可选, 符合ISO 4217标准的三位字母代码, 默认人民币: CNY
            'time_start': None,         # 可选, 订单生成时间, 默认为当前时间
            'time_expire': None,        # 可选, 订单失效时间, 默认为订单生成时间后两小时
            'goods_tag': None,          # 可选, 商品标记, 代金券或立减优惠功能的参数
            'product_id': product_id,   # 可选, 当trade_type=NATIVE, 此参数必传. 此id为二维码中包含的商品ID, 商户自行定义
            'device_info': None,        # 可选, 终端设备号(门店号或收银设备ID), 注意:PC网页或公众号内支付请传"WEB"
            'limit_pay': None,          # 可选, 指定支付方式, no_credit-指定不能使用信用卡支付
            'notify_url': notify_url,   # 订单通知地址
        }

        # 统一下单, 生成微信支付参数返回给微信浏览器
        response = cls._pay_api.order.create(**order_params)
        # OrderedDict([('return_code', 'SUCCESS'),
        #              ('return_msg', 'OK'),
        #              ('appid', 'wx54d296959ee50c01'),
        #              ('mch_id', '1517154171'),
        #              ('nonce_str', 'IvST3Mh4a5cQEUdN'),
        #              ('sign', 'BF402367D8C84BE53D0DCE942FA676AB'),
        #              ('result_code', 'SUCCESS'),
        #              ('prepay_id', 'wx27163152798783d24f7f81121395790900'),
        #              ('trade_type', 'NATIVE'),
        #              ('code_url', 'weixin://wxpay/bizpayurl?pr=LQjaKQI')])
        return response

    @classmethod
    def get_jsapi_params(cls, prepay_id: str):
        """
        :param prepay_id:
        :return:
        # {'appId': 'wx54d296959ee50c01',
        #  'nonceStr': '603sd7IpN4M2OqCVvZazxrXY9bT5lBcR',
        #  'package': 'prepay_id=wx242238115691612efb08d4092661275602',
        #  'paySign': '6D2340AC7276C93852461E130A404E87',
        #  'signType': 'MD5',
        #  'timeStamp': '1540391991'}
        """
        params = cls._pay_api.jsapi.get_jsapi_params(str(prepay_id))
        return params

    @classmethod
    def apply_refund(cls, out_trade_no, total_fee, out_refund_no, refund_fee, notify_url=None):
        """
        微信侧保证全额退款最多只会执行1次
        """
        refund_params = {
            'total_fee': total_fee,             # 订单总金额，单位为分
            'refund_fee': refund_fee,           # 退款总金额，单位为分
            'out_refund_no': out_refund_no,     # 商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔
            'out_trade_no': out_trade_no,       # 商户系统内部的订单号，transaction_id 二选一
            'fee_type': 'CNY',                  # 可选，货币类型，符合ISO 4217标准的三位字母代码，默认人民币：CNY
            'notify_url': notify_url,           # 可选，异步接收微信支付退款结果通知的回调地址
        }
        response = cls._pay_api.refund.apply(**refund_params)
        # >>> print(response)
        # OrderedDict([('return_code', 'SUCCESS'),
        #              ('return_msg', 'OK'),
        #              ('appid', 'wx54d296959ee50c01'),
        #              ('mch_id', '1517154171'),
        #              ('nonce_str', '9GgtDUrqZSiNXV7h'),
        #              ('sign', 'E84B63245169A008C8385567E2C49AD6'),
        #              ('result_code', 'SUCCESS'),
        #              ('transaction_id', '4200000297201907025906623815'),
        #              ('out_trade_no', '1562071838292kQBS1WdoVtkRGUqRW'),
        #              ('out_refund_no', '1562071838292kQBS1WdoVtkRGUqRW'),
        #              ('refund_id', '50000700772019070310374962187'),
        #              ('refund_channel', None),
        #              ('refund_fee', '1'),
        #              ('coupon_refund_fee', '0'),
        #              ('total_fee', '1'),
        #              ('cash_fee', '1'),
        #              ('coupon_refund_count', '0'),
        #              ('cash_refund_fee', '1')])
        return response

    @classmethod
    def query_order(cls, out_trade_no):
        """
        接口文档:     https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_2
        :param out_trade_no:
        :return:  字典类型
        <xml>
           <return_code><![CDATA[SUCCESS]]></return_code>
           <return_msg><![CDATA[OK]]></return_msg>
           <appid><![CDATA[wx2421b1c4370ec43b]]></appid>
           <mch_id><![CDATA[10000100]]></mch_id>
           <device_info><![CDATA[1000]]></device_info>
           <nonce_str><![CDATA[TN55wO9Pba5yENl8]]></nonce_str>
           <sign><![CDATA[BDF0099C15FF7BC6B1585FBB110AB635]]></sign>
           <result_code><![CDATA[SUCCESS]]></result_code>
           <openid><![CDATA[oUpF8uN95-Ptaags6E_roPHg7AG0]]></openid>
           <is_subscribe><![CDATA[Y]]></is_subscribe>
           <trade_type><![CDATA[MICROPAY]]></trade_type>
           <bank_type><![CDATA[CCB_DEBIT]]></bank_type>
           <total_fee>1</total_fee>
           <fee_type><![CDATA[CNY]]></fee_type>
           <transaction_id><![CDATA[1008450740201411110005820873]]></transaction_id>
           <out_trade_no><![CDATA[1415757673]]></out_trade_no>
           <attach><![CDATA[订单额外描述]]></attach>
           <time_end><![CDATA[20141111170043]]></time_end>
           <trade_state><![CDATA[SUCCESS]]></trade_state>
        </xml>
        """
        query_params = {
            'out_trade_no': out_trade_no,
        }
        try:
            response = cls._pay_api.order.query(**query_params)
            return response
        except WeChatPayException as e:
            if e.errcode == 'ORDERNOTEXIST':
                return None
            raise e

    @classmethod
    def close_order(cls, out_trade_no):
        query_params = {
            'out_trade_no': out_trade_no,
        }
        response = cls._pay_api.order.close(**query_params)
        return response

    @classmethod
    def parse_payment_result(cls, xml):
        return cls._pay_api.parse_payment_result(xml)

