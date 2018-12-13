import datetime
# 第三方类
from django.core.management.base import BaseCommand
# 自己的类
from trade.management.commands import Service
from trade.order.models import Orders
from mybase3.mylog3 import log

log.setLogHeader('statistics')


# 使用方法:  python manage.py statistics
class Command(BaseCommand):
    def handle(self, *args, **options):
        process = ServiceLoop()
        process.start()


class ServiceLoop(Service):
    interval = 600

    def run(self):
        pass
