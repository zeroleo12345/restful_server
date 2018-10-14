from django.apps import AppConfig
from django.conf import settings
from trade.utils.mp import MediaPlatform


class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        # startup code here
        if settings.DEBUG:
            # 本地调试环境
            pass
        else:
            MediaPlatform.create_mp_menu()
