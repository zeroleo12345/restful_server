from django.apps import AppConfig
from trade.utils.mp import create_mp_menu


class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        # startup code here
        create_mp_menu()
