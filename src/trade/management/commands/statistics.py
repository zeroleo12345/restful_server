import datetime
# 第三方类
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
# 自己的类
from trade.management.commands import Service
from models import Orders
from trade.settings import log
from utils.slack import send_slack_message

log.set_header('statistics')


# 使用方法:  python manage.py statistics
class Command(BaseCommand):
    def handle(self, *args, **options):
        process = ServiceLoop()
        process.start()


class ServiceLoop(Service):
    interval = 0

    def run(self):
        # 累计昨天成交
        today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - datetime.timedelta(days=1)
        today_sum = Orders.objects.filter(
            status='paid', updated_at__gt=yesterday, updated_at__lt=today
        ).aggregate(sum=Sum('total_fee'))['sum']
        if not today_sum:
            today_sum = 0

        # 累计所有成交
        total_sum = Orders.objects.filter(status='paid').aggregate(sum=Sum('total_fee'))['sum']
        if not total_sum:
            total_sum = 0

        # 发送slack统计消息
        text = f'昨天充值金额: {today_sum/100} 元, 历史累计充值金额: {total_sum/100} 元'
        send_slack_message(text=text)
        self.term = 1
