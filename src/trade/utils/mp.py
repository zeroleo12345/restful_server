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

redirect_uri = urljoin(settings.HTML_URL, 'oauth2')
print(redirect_uri)
g_wechat_oauth = WeChatOAuth(app_id=settings.APPID,
                             secret=settings.APPSECRET,
                             redirect_uri=redirect_uri,
                             # snsapi_base-不需授权; snsapi_userinfo-需授权
                             scope='snsapi_userinfo',
                             state='1')


def create_mp_menu():
    # 创建公众号-自定义菜单: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141013
    menu_data = {"button": [
        {
            "name": '个人中心',
            "type": 'view',
            "url": f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={settings.APPID}'
                   f'&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo'
        },
    ]}
    g_wechat_client.menu.create(menu_data)
