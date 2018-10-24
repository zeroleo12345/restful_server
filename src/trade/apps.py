from django.apps import AppConfig
from django.conf import settings
from trade.utils.mp import MediaPlatform


class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        # startup code here
        MediaPlatform.create_mp_menu()
