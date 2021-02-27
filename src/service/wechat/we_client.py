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
    ACCOUNT_VIEW_BTN_EVENT = 'ACCOUNT_VIEW_BTN_EVENT'       # 账户中心
    CUSTOMER_SERVICE_BTN_EVENT = 'CUSTOMER_SERVICE_BTN_EVENT'     # 联系客服
    ACCOUNT_VIEW_URI = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={settings.MP_APP_ID}' \
                       f'&redirect_uri={settings.MP_HOST}/&response_type=code&scope=snsapi_userinfo'
    PLATFORM_VIEW_URI = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={settings.MP_APP_ID}' \
                        f'&redirect_uri={settings.MP_HOST}/platform&response_type=code&scope=snsapi_userinfo'
    IOS_VIEW_URI = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={settings.MP_APP_ID}' \
                   f'&redirect_uri={settings.MP_HOST}/ios&response_type=code&scope=snsapi_userinfo'
    ANDROID_VIEW_URI = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={settings.MP_APP_ID}' \
                       f'&redirect_uri={settings.MP_HOST}/android&response_type=code&scope=snsapi_userinfo'

    @classmethod
    def create_mp_menu(cls):
        if not settings.ENV.is_production():
            return

        # 创建公众号-自定义菜单: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141013
        menu_data = {
            'button': [
                {
                    'type': 'click',
                    'name': 'WIFI账号中心',
                    'key': cls.ACCOUNT_VIEW_BTN_EVENT,
                },
                {
                    'type': 'click',
                    'name': '联系客服',
                    'key': cls.CUSTOMER_SERVICE_BTN_EVENT,
                },
                {
                    'name': '上网教程',
                    'sub_button': [
                        {
                            'type': 'view',
                            'name': '上网教程 (苹果手机)',
                            'url': cls.IOS_VIEW_URI,
                        },
                        {
                            'type': 'view',
                            'name': '上网教程 (安卓手机)',
                            'url': cls.ANDROID_VIEW_URI,
                        },
                    ]
                }
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
        :param is_permanent:
        :return: {"ticket":"gQH47joAAAAAAAAAASxod2G3sUw==","expire_seconds":60,"url":"http://weixin.qq.com/q/kZgfwMTm72WWPkovabbI"}
                    ticket:  获取的二维码ticket，凭借此ticket可以在有效时间内换取二维码。
                    expire_seconds:  该二维码有效时间，以秒为单位。 最大不超过2592000（即30天）。
                    url:  二维码图片解析后的地址，开发者可根据该地址自行生成需要的二维码图片
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
