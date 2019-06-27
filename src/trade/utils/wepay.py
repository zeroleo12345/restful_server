import time
# 第三方库
from django.conf import settings
from wechatpy.pay import WeChatPay
# 自己的库
from trade.utils.myrandom import MyRandom


class WePay(object):
    WECHAT_PAY = WeChatPay(
        settings.MP_APP_ID, settings.MP_APP_KEY,
        settings.MP_MERCHANT_ID, settings.MP_SUB_MERCHANT_ID,
        settings.MP_MERCHANT_CERT, settings.MP_MERCHANT_KEY
    )

    @staticmethod
    def create_out_trade_no():
        # 商户订单号(32个字符内,只能是>数字、大小写字母_-|*@), 默认自动生成
        return ''.join((
            str(int(time.time()*1000)),
            MyRandom.random_string(17, lowercase=True, uppercase=True)
        ))

    @staticmethod
    def cashier(openid, total_fee, title, client_ip, attach=None, notify_url=None):
        """
        用户点击button跳转到收银台支付.
        :param openid: 缴费用户的openid. 当trade_type=JSAPI, 此参数必传
        :param total_fee: 支付金额, 单位分
        :param title: 订单标题
        :param client_ip: APP和网页支付提交用户端ip, Native支付填调用微信支付API的机器IP
        :param attach: 用户自定义数据，在notify的时候会原样返回
        :param notify_url: 接收微信支付异步通知的回调地址。必须为可直接访问的URL，不能带参数、session验证、csrf验证。留空则不通知
        :return:
            (order_params, jsapi_params)
        """
        # 统一下单. 微信官方参数地址:  https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
        order_params = {
            'trade_type': 'JSAPI',      # 交易类型 JSAPI--公众号支付, NATIVE--原生扫码支付, APP--app支付, 而MICROPAY--刷卡支付有单独的支付接口, 不能调用统一下单接口
            'body': title,              # 商品描述
            'total_fee': total_fee,     # 订单金额. (单位分)
            'notify_url': notify_url,   # 订单通知地址
            'attach': attach,
            'user_id': openid,          # 可选. 缴费用户的openid. 当trade_type=JSAPI, 此参数必传
            'client_ip': client_ip,     # 可选. APP和网页支付提交用户端ip, Native支付填调用微信支付API的机器IP
            'out_trade_no': WePay.create_out_trade_no(),
            'detail': None,             # 可选, 商品详情
            'fee_type': 'CNY',          # 可选, 符合ISO 4217标准的三位字母代码, 默认人民币: CNY
            'time_start': None,         # 可选, 订单生成时间, 默认为当前时间
            'time_expire': None,        # 可选, 订单失效时间, 默认为订单生成时间后两小时
            'goods_tag': None,          # 可选, 商品标记, 代金券或立减优惠功能的参数
            'product_id': None,         # 可选, 当trade_type=NATIVE, 此参数必传. 此id为二维码中包含的商品ID, 商户自行定义
            'device_info': None,        # 可选, 终端设备号(门店号或收银设备ID), 注意:PC网页或公众号内支付请传"WEB"
            'limit_pay': None,          # 可选, 指定支付方式, no_credit-指定不能使用信用卡支付
        }

        # 统一下单, 生成微信支付参数返回给微信浏览器
        ret_json = WePay.WECHAT_PAY.order.create(**order_params)
        # (Pdb) pprint(ret_json)
        # OrderedDict([('return_code', 'SUCCESS'),
        #              ('return_msg', 'OK'),
        #              ('appid', 'wx54d296959ee50c0b'),
        #              ('mch_id', '1517154171'),
        #              ('nonce_str', 'RDX6pxz2GTEdoQnE'),
        #              ('sign', '796CC22F8EDD664372BE9ACF7EB68ACD'),
        #              ('result_code', 'SUCCESS'),
        #              ('prepay_id', 'wx242238115691612efb08d4092661275602'),
        #              ('trade_type', 'JSAPI')])
        # 把微信服务端返回的参数转换为微信客户端JSAPI使用的参数
        prepay_id = ret_json['prepay_id'].__str__()
        jsapi_params = WePay.WECHAT_PAY.jsapi.get_jsapi_params(prepay_id)
        # (Pdb) pprint(params_dict)
        # {'appId': 'wx54d296959ee50c0b',
        #  'nonceStr': '603sd7IpN4M2OqCVvZazxrXY9bT5lBcR',
        #  'package': 'prepay_id=wx242238115691612efb08d4092661275602',
        #  'paySign': '6D2340AC7276C93852461E130A404E87',
        #  'signType': 'MD5',
        #  'timeStamp': '1540391991'}
        return order_params, jsapi_params

    @staticmethod
    def qrcode(total_fee, title, client_ip, attach=None, notify_url=None):
        """
        用户二维码支付.
        :param total_fee: 支付金额, 单位分
        :param title: 订单标题
        :param client_ip: APP和网页支付提交用户端ip, Native支付填调用微信支付API的机器IP
        :param attach: 用户自定义数据，在notify的时候会原样返回
        :param notify_url: 接收微信支付异步通知的回调地址。必须为可直接访问的URL，不能带参数、session验证、csrf验证。留空则不通知
        :return:
            (order_params, response)
        """
        # 统一下单. 微信官方参数地址:  https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
        order_params = {
            'trade_type': 'NATIVE',      # 交易类型 JSAPI--公众号支付, NATIVE--原生扫码支付, APP--app支付, 而MICROPAY--刷卡支付有单独的支付接口, 不能调用统一下单接口
            'body': title,              # 商品描述
            'total_fee': total_fee,     # 订单金额. (单位分)
            'notify_url': notify_url,   # 订单通知地址
            'attach': attach,
            'user_id': None,            # 可选. 缴费用户的openid. 当trade_type=JSAPI, 此参数必传
            'client_ip': client_ip,     # 可选. APP和网页支付提交用户端ip, Native支付填调用微信支付API的机器IP
            'out_trade_no': WePay.create_out_trade_no(),
            'detail': None,             # 可选, 商品详情
            'fee_type': 'CNY',          # 可选, 符合ISO 4217标准的三位字母代码, 默认人民币: CNY
            'time_start': None,         # 可选, 订单生成时间, 默认为当前时间
            'time_expire': None,        # 可选, 订单失效时间, 默认为订单生成时间后两小时
            'goods_tag': None,          # 可选, 商品标记, 代金券或立减优惠功能的参数
            'product_id': None,         # 可选, 当trade_type=NATIVE, 此参数必传. 此id为二维码中包含的商品ID, 商户自行定义
            'device_info': None,        # 可选, 终端设备号(门店号或收银设备ID), 注意:PC网页或公众号内支付请传"WEB"
            'limit_pay': None,          # 可选, 指定支付方式, no_credit-指定不能使用信用卡支付
        }

        # 统一下单, 生成微信支付参数返回给微信浏览器
        response = WePay.WECHAT_PAY.order.create(**order_params)
        # (Pdb) pprint(ret_json)
        # OrderedDict([('return_code', 'SUCCESS'),
        #              ('return_msg', 'OK'),
        #              ('appid', 'wx54d296959ee50c0b'),
        #              ('mch_id', '1517154171'),
        #              ('nonce_str', 'IvST3Mh4a5cQEUdN'),
        #              ('sign', 'BF402367D8C84BE53D0DCE942FA676AB'),
        #              ('result_code', 'SUCCESS'),
        #              ('prepay_id', 'wx27163152798783d24f7f81121395790900'),
        #              ('trade_type', 'NATIVE'),
        #              ('code_url', 'weixin://wxpay/bizpayurl?pr=LQjaKQI')])
        # (Pdb) pprint(params_dict)
        return order_params, response

    @staticmethod
    def query(payjs_order_id):
        # 查询订单状态
        pass
