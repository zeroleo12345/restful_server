from trade import settings
#
from wechatpy.oauth import WeChatOAuth, WeChatOAuthException
import sentry_sdk


class WeOAuth(object):
    # snsapi_base-不需授权; snsapi_userinfo-需授权
    # state:  重定向后会带上此参数, 开发者可以填写a-zA-Z0-9的参数值，最多128字节
    _oauth_api = WeChatOAuth(
        app_id=settings.MP_APP_ID, secret=settings.MP_APP_SECRET, redirect_uri='', scope='snsapi_userinfo', state='1'
    )

    @classmethod
    def get_user_info(cls, code):
        """ 使用code通过微信OAUTH2接口, 获取openid.  # http://www.cnblogs.com/txw1958/p/weixin76-user-info.html
        {
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
            user_info['openid'] = oauth_code
            return user_info
        try:
            openid_access_token = cls._oauth_api.fetch_access_token(code)
        except WeChatOAuthException as e:
            sentry_sdk.capture_exception(e)
            return None, None, None
        # fetch_access_token 函数返回:
        # {
        #     'access_token': 'vX1lcBkeRY6WZUylVyZA9XPeoA92_15iBAXHHRtBD1dtbAtWe9e3i-DyHR9PBtP6L',
        #     'openid': 'ovj3E0l9vffwBuqz_PNu25yL_is4',
        #     'expires_in': 7200,
        #     'refresh_token': 'LSaCEeS8m-18_njiAN8Jm11V4QIeWxwOSsjEV9cM1ra5zkL',
        #     'scope': 'snsapi_userinfo'
        # }
        user_info = cls._oauth_api.get_user_info(openid=openid_access_token['openid'], access_token=openid_access_token['access_token'])
        openid = user_info['openid']
        nickname = user_info['nickname']
        avatar = user_info['headimgurl']
        return openid, nickname, avatar
