from django.conf import settings
from django_redis import get_redis_connection
from urllib.parse import urljoin

from wechatpy import WeChatClient
from wechatpy.oauth import WeChatOAuth
from wechatpy.session.redisstorage import RedisStorage

redis_client = get_redis_connection(alias='default')


class MediaPlatform(object):
    REDIRECT_URI = urljoin(settings.MP_WEB_URL, '')
    WECHAT_CLIENT = WeChatClient(
        appid=settings.MP_APP_ID, secret=settings.MP_APP_SECRET, session=RedisStorage(redis_client, prefix="_wechatpy")
    )

    WECHAT_OAUTH = WeChatOAuth(
        # snsapi_base-不需授权; snsapi_userinfo-需授权
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
                           f'&redirect_uri={MediaPlatform.REDIRECT_URI}&response_type=code&scope=snsapi_userinfo'
                },
                {
                    "name": '使用教程',
                    "type": 'view',
                    "url": 'https://www.baidu.com'
                },
            ]
        }
        MediaPlatform.WECHAT_CLIENT.menu.create(menu_data)

    @staticmethod
    def get_user_info_from_wechat(code):
        """ 使用code通过微信OAUTH2接口, 获取openid.  # http://www.cnblogs.com/txw1958/p/weixin76-user-info.html
        fetch_access_token()函数返回:
        {
            u'access_token': u'vX1lcBkeRY6WZUylVyZA9XPeoA92_15iBAXHHRtBD1dtbAtWe9e3i-DyHR9PBtP6L......',
            u'openid': u'ovj3E0l9vffwBuqz_PNu25yL_is4', u'expires_in': 7200,
            u'refresh_token': u'LSaCEeS8m-18_njiAN8Jm11V4QIeWxwOSsjEV9cM1ra5zkL......', u'scope': u'snsapi_userinfo'
        }
        """
        if not settings.ENVIRONMENT.is_production():
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
        MediaPlatform.WECHAT_OAUTH.fetch_access_token(code)
        user_info = MediaPlatform.WECHAT_OAUTH.get_user_info()
        return user_info
