from django.apps import AppConfig
from trade.service.wechat.mp import WechatPlatform


class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        # startup code here
        WechatPlatform.create_mp_menu()
