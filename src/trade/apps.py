from django.apps import AppConfig
from service.wechat.we_client import WeClient


class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        # startup code here
        WeClient.create_mp_menu()
