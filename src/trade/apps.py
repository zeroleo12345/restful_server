from django.apps import AppConfig
from django.db.models.signals import pre_migrate
from django.db.backends.signals import connection_created
from trade.utils.mp import MP

is_migration = False


def post_migration_callback(sender, **kwargs):
    print('111111111111: post_migration_callback')
    global is_migration
    is_migration = True


def init_my_app(sender, connection, **kwargs):
    print(f'22222222222222: init_my_app, is_migration: {is_migration}')
    if not is_migration:
        MP.create_mp_menu()


pre_migrate.connect(post_migration_callback, sender=None)

class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        # startup code here
        print('333333333333: ready')
        connection_created.connect(init_my_app, sender=None)
