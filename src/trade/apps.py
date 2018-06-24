from django.apps import AppConfig
from trade.utils.mp import MP


class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        # startup code here
        MP.create_mp_menu()
