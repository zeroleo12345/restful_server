import datetime
# 第三方类
from django.utils import timezone
from django.db.models import Sum
# 自己的类
from . import MetaClass
from trade.models import Order
from utils.feishu import Feishu
from utils.decorators import promise_do_once


class StatisticsJob(metaclass=MetaClass):
    next_time = timezone.localtime()

    @classmethod
    def start(cls):
        now = timezone.localtime()
        if now < cls.next_time:
            return
        # 隔天早上7点
        tomorrow = (now + datetime.timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        cls.next_time = tomorrow
        #
        start_time = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time - datetime.timedelta(days=1)
        cls.doing(start_time=start_time, end_time=end_time)

    @classmethod
    @promise_do_once(file_name='statistics', func_name='doing')
    def doing(cls, start_time, end_time):
        # 累计昨天成交
        status = Order.Status.PAID.value
        today_sum = Order.objects.filter(
            status=status, updated_at__gt=end_time, updated_at__lt=start_time
        ).aggregate(sum=Sum('total_fee'))['sum']
        if not today_sum:
            today_sum = 0

        # 累计所有成交
        total_sum = Order.objects.filter(status=status).aggregate(sum=Sum('total_fee'))['sum']
        if not total_sum:
            total_sum = 0

        # 发送slack统计消息
        text = f'昨天充值金额: {today_sum/100} 元, 历史累计充值金额: {total_sum/100} 元'
        Feishu.send_groud_msg(receiver_id=Feishu.FEISHU_NOTIFY_GROUP, text=text)
