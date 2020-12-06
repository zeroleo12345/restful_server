from trade import settings
from django_redis import get_redis_connection
#
from wechatpy import WeChatClient
from wechatpy.session.redisstorage import RedisStorage

redis_client = get_redis_connection(alias='default')


class WeClient(object):
    we_client = WeChatClient(
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
                    'name': '账号充值',
                    'url': cls.recharge_uri,
                },
                {
                    'type': 'view',
                    'name': '使用教程',
                    'url': f'{settings.TUTORIAL_URL}',
                },
            ]
        }
        cls.we_client.menu.create(menu_data)
        return

    @classmethod
    def create_qrcode(cls, scene_str: str, expire_seconds: int = 30, is_permanent=False):
        """
        https://developers.weixin.qq.com/doc/offiaccount/Account_Management/Generating_a_Parametric_QR_Code.html
        :param scene_str:
        :param expire_seconds:
        :return: {"ticket":"gQH47joAAAAAAAAAASxod2G3sUw==","expire_seconds":60,"url":"http://weixin.qq.com/q/kZgfwMTm72WWPkovabbI"}
        """
        assert isinstance(scene_str, str)
        data = {
            'expire_seconds': expire_seconds,
            'action_name': 'QR_LIMIT_STR_SCENE' if is_permanent else 'QR_STR_SCENE',
            'action_info': {
                'scene': {'scene_str': scene_str},
            }
        }
        return cls.we_client.qrcode.create(data)
