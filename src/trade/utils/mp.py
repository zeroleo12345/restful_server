import time
from django.conf import settings
from django_redis import get_redis_connection
from urllib.parse import urljoin

from wechatpy import WeChatClient
from wechatpy.oauth import WeChatOAuth
from wechatpy.session.redisstorage import RedisStorage
from payjs import PayJS

from trade.utils.myrandom import MyRandom

redis_client = get_redis_connection(alias='default')


class MediaPlatform(object):
    redirect_uri = urljoin(settings.HTML_URL, '')
    wechat_client = WeChatClient(appid=settings.APPID, secret=settings.APPSECRET,
                                   session=RedisStorage(redis_client, prefix="_wechatpy"))
    # snsapi_base-不需授权; snsapi_userinfo-需授权
    wechat_oauth = WeChatOAuth(app_id=settings.APPID, secret=settings.APPSECRET, redirect_uri=redirect_uri,
                                 scope='snsapi_userinfo', state='1')

    @staticmethod
    def create_mp_menu():
        if settings.ENVIORMENT.is_unittest():
            return

        # TODO: 防止多次创建菜单
        # 创建公众号-自定义菜单: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141013
        menu_data = {"button": [
            {
                "name": '个人中心',
                "type": 'view',
                "url": f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={settings.APPID}'
                       f'&redirect_uri={MediaPlatform.redirect_uri}&response_type=code&scope=snsapi_userinfo'
            },
        ]}
        print(menu_data)
        MediaPlatform.wechat_client.menu.create(menu_data)

    @staticmethod
    def get_user_info_from_wechat(code):
        """ 使用code通过微信OAUTH2接口, 获取openid.
        返回数据请参考: http://www.cnblogs.com/txw1958/p/weixin76-user-info.html
        fetch_access_token:
        {
            u'access_token': u'vX1lcBkeRY6WZUylVyZA9XPeoA92_15iBAXHHRtBD1dtbAtWe9e3i-DyHR9PBtP6L......',
            u'openid': u'ovj3E0l9vffwBuqz_PNu25yL_is4', u'expires_in': 7200,
            u'refresh_token': u'LSaCEeS8m-18_njiAN8Jm11V4QIeWxwOSsjEV9cM1ra5zkL......', u'scope': u'snsapi_userinfo'
        }
        """
        if settings.DEBUG:
            user_info = {
                u'province': u'\u5e7f\u4e1c', u'openid': u'ovj3E0l9vffwBuqz_PNu25yL_is4',
                u'headimgurl': u'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7AianZsHE6LefhQuSmwibx4KZ9LYkRmIibrFKmSbAVjlpBg/0',
                u'language': u'zh_CN', u'city': u'\u5e7f\u5dde', u'country': u'\u4e2d\u56fd', u'sex': 1,
                u'privilege': [], u'nickname': u'\u5468\u793c\u6b23'
            }
            pass
            user_info['openid'] = code
            return user_info

        # TODO: token 针对每个用户2小时内有效, 不需要每次都通过code获取新的token!!!
        # https://wohugb.gitbooks.io/wechat/content/qrconnent/refresh_token.html
        MediaPlatform.wechat_oauth.fetch_access_token(code)
        user_info = MediaPlatform.wechat_oauth.get_user_info()
        return user_info


class WeixinPay(object):
    # pay_js = PayJS(settings.MCHID, settings.APPKEY, FORCE_SSL=False)
    pay_js = PayJS(settings.MCHID, settings.APPKEY)

    @staticmethod
    def create_out_trade_no():
        return ''.join((
            str(int(time.time()*1000)),
            MyRandom.random_string(17)
        ))

    @staticmethod
    def cashier(total_fee, title=None, attach=None, notify_url=None, callback_url=None):
        """
        发起收银台支付

        注：目前此接口在参数传递错误时并不会有提示，依然会返回一个跳转后的网址
        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param title: （可选）订单标题，0 - 32 字符
        :param attach: （可选）用户自定义数据，在notify的时候会原样返回
        :param notify_url: （可选）回调地址，留空使用默认，传入空字符串代表无需回调
        :param callback_url: （可选）（暂无效）支付成功后前端跳转地址
        :return: PayJSResult: {
            'REDIRECT': 'http://shifenkuai.popfeng.com/micropay/getopenid?token=order:token:sSxjpV0siRYb5lWr',
            'STATUS_CODE': 302,
            'json': None,
            'redirect': 'http://shifenkuai.popfeng.com/micropay/getopenid?token=order:token:sSxjpV0siRYb5lWr',
            'url': 'https://payjs.cn/api/cashier'
        }
        """
        # 收银台支付
        # 可选. 商户订单号(32个字符内,只能是数字、大小写字母_-|*@), 默认自动生成
        out_trade_no = WeixinPay.create_out_trade_no()
        return WeixinPay.pay_js.cashier(out_trade_no=out_trade_no, total_fee=total_fee, body=title, attach=attach, notify_url=notify_url, callback_url=callback_url)

    @staticmethod
    def qrpay(total_fee, title=None, attach=None, notify_url=None):
        """
        发起扫码支付
        :param total_fee: 支付金额，单位为分，介于 1 - 1000000 之间
        :param title: （可选）订单标题，0 - 32 字符
        :param attach: （可选）用户自定义数据，在notify的时候会原样返回
        :param notify_url: （可选）回调地址，留空使用默认，传入空字符串代表无需回调
        :return:
        """
        out_trade_no = WeixinPay.create_out_trade_no()
        return WeixinPay.pay_js.native(out_trade_no=out_trade_no, total_fee=total_fee, body=title, attach=attach)
        # if r:
        #     print(r.code_url)         # 二维码地址（weixin:// 开头，请使用此地址构建二维码）
        #     print(r.qrcode)           # 二维码地址（https:// 开头，为二维码图片的地址）
        #     print(r.payjs_order_id)   # 订单号（PAYJS 的）
        # else:
        #     print(r.STATUS_CODE)      # HTTP 请求状态码
        #     print(r.ERROR_NO)         # 错误码
        #     print(r.error_msg)        # 错误信息
        #     print(r)
