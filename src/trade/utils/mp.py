from django.conf import settings
from django_redis import get_redis_connection
from urllib.parse import urljoin

from wechatpy import WeChatClient
from wechatpy.oauth import WeChatOAuth
from wechatpy.session.redisstorage import RedisStorage

redis_client = get_redis_connection()

g_wechat_client = WeChatClient(appid=settings.APPID,
                               secret=settings.APPSECRET,
                               session=RedisStorage(redis_client, prefix="_wechatpy"))

redirect_uri = urljoin(settings.HTML_URL, '')
g_wechat_oauth = WeChatOAuth(app_id=settings.APPID,
                             secret=settings.APPSECRET,
                             redirect_uri=redirect_uri,
                             # snsapi_base-不需授权; snsapi_userinfo-需授权
                             scope='snsapi_userinfo',
                             state='1')


class MediaPlatform(object):
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
                       f'&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo'
            },
        ]}
        print(menu_data)
        g_wechat_client.menu.create(menu_data)

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
            return {
                u'province': u'\u5e7f\u4e1c', u'openid': u'ovj3E0l9vffwBuqz_PNu25yL_is4',
                u'headimgurl': u'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7AianZsHE6LefhQuSmwibx4KZ9LYkRmIibrFKmSbAVjlpBg/0',
                u'language': u'zh_CN', u'city': u'\u5e7f\u5dde', u'country': u'\u4e2d\u56fd', u'sex': 1,
                u'privilege': [], u'nickname': u'\u5468\u793c\u6b23'
            }

        # TODO: token 针对每个用户2小时内有效, 不需要每次都通过code获取新的token!!!
        # https://wohugb.gitbooks.io/wechat/content/qrconnent/refresh_token.html
        g_wechat_oauth.fetch_access_token(code)
        user_info = g_wechat_oauth.get_user_info()
        return user_info
