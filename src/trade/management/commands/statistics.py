import datetime
# 第三方类
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
# 自己的类
from trade.management.commands import Service
from trade.order.models import Orders
from mybase3.mylog3 import log
from trade.utils.slack import send_slack_message

log.setLogHeader('statistics')


# 使用方法:  python manage.py statistics
class Command(BaseCommand):
    def handle(self, *args, **options):
        process = ServiceLoop()
        process.start()


class ServiceLoop(Service):
    interval = 600

    def run(self):
        # 累计昨天成交
        today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - datetime.timedelta(days=1)
        today_total = Orders.objects.filter(
            status='paid', updated_at__gt=yesterday, updated_at__lt=today
        ).aggregate(Sum('total_fee'))['total_fee']

        # 累计所有成交
        total = Orders.objects.filter(status='paid').aggregate(Sum('total_fee'))['total_fee']

        # 发送slack统计消息
        text = f'今天充值金额: {today_total/100}元, 历史累计充值金额: {total/100}元'
        send_slack_message(text=text)
        self.term = 1
