from django.apps import AppConfig
from trade.utils import create_mp_menu


class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        # startup code here
        create_mp_menu()
