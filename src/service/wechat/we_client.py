from trade import settings
from django_redis import get_redis_connection
#
from wechatpy import WeChatClient
from wechatpy.session.redisstorage import RedisStorage

redis_client = get_redis_connection(alias='default')


class WeClient(object):
    client_api = WeChatClient(
        appid=settings.MP_APP_ID, secret=settings.MP_APP_SECRET, session=RedisStorage(redis_client, prefix='wechat')
    )
    recharge_uri = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={settings.MP_APP_ID}' \
                   f'&redirect_uri={settings.MP_REDIRECT_URI}&response_type=code&scope=snsapi_userinfo'

    @classmethod
    def create_mp_menu(cls):
        if not settings.ENV.is_production():
            return

        # TODO: 防止多次创建菜单
        # 创建公众号-自定义菜单: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141013
        menu_data = {
            'button': [
                {
                    'type': 'view',
                    'name': '充值',
                    'url': cls.recharge_uri,
                },
                {
                    'type': 'view',
                    'name': '使用教程',
                    'url': f'{settings.TUTORIAL_URL}',
                },
            ]
        }
        cls.client_api.menu.create(menu_data)
