from django.conf import settings
from django_redis import get_redis_connection
from urllib.parse import urljoin

from wechatpy import WeChatClient
from wechatpy.oauth import WeChatOAuth
from wechatpy.session.redisstorage import RedisStorage

redis_client = get_redis_connection(alias='default')


class WechatPlatform(object):
    REDIRECT_URI = urljoin(settings.MP_WEB_URL, '')
    CLIENT = WeChatClient(
        appid=settings.MP_APP_ID, secret=settings.MP_APP_SECRET, session=RedisStorage(redis_client, prefix="_wechatpy")
    )

    # snsapi_base-不需授权; snsapi_userinfo-需授权
    WECHAT_OAUTH = WeChatOAuth(
        app_id=settings.MP_APP_ID, secret=settings.MP_APP_SECRET, redirect_uri=REDIRECT_URI, scope='snsapi_userinfo',
        state='1'
    )

    @staticmethod
    def create_mp_menu():
        if not settings.ENVIRONMENT.is_production():
            return

        # TODO: 防止多次创建菜单
        # 创建公众号-自定义菜单: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141013
        menu_data = {
            "button": [
                {
                    "name": '账号中心',
                    "type": 'view',
                    "url": f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={settings.MP_APP_ID}'
                           f'&redirect_uri={WechatPlatform.REDIRECT_URI}&response_type=code&scope=snsapi_userinfo',
                },
                {
                    "name": '使用教程',
                    "type": 'view',
                    "url": f'{settings.TUTORIAL_URL}',
                },
            ]
        }
        WechatPlatform.CLIENT.menu.create(menu_data)

    @staticmethod
    def get_user_info_from_wechat(code):
        """ 使用code通过微信OAUTH2接口, 获取openid.  # http://www.cnblogs.com/txw1958/p/weixin76-user-info.html
        fetch_access_token()函数返回:
        {
            'access_token': 'vX1lcBkeRY6WZUylVyZA9XPeoA92_15iBAXHHRtBD1dtbAtWe9e3i-DyHR9PBtP6L......',
            'openid': 'ovj3E0l9vffwBuqz_PNu25yL_is4', 'expires_in': 7200,
            'refresh_token': 'LSaCEeS8m-18_njiAN8Jm11V4QIeWxwOSsjEV9cM1ra5zkL......', 'scope': 'snsapi_userinfo'
        }
        """
        if not settings.ENVIRONMENT.is_production():
            # 返回例子
            user_info = {
                'province': '广东',
                'openid': 'ovj3E0l9vffwBuqz_PNu25yL_is4',
                'headimgurl': 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7AianZsHE6LefhQuSmwibx4KZ9LYkRmIibrFKmSbAVjlpBg/0',
                'language': 'zh_CN',
                'city': '广州',
                'country': '中国',
                'sex': 1,
                'privilege': [],
                'nickname': '测试账号'
            }
            pass
            user_info['openid'] = code
            return user_info

        # TODO: access_token 针对每个用户2小时内有效. 服务端需主动获取用户信息时, 可重用access_token!
        # https://wohugb.gitbooks.io/wechat/content/qrconnent/refresh_token.html
        WechatPlatform.WECHAT_OAUTH.fetch_access_token(code)
        user_info = WechatPlatform.WECHAT_OAUTH.get_user_info()
        return user_info
