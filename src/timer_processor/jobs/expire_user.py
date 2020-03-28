import datetime
# 第三方库
from django.utils import timezone
# 项目库
from . import MetaClass
from models import User
from trade.settings import log
from utils.decorators import promise_do_once


class ExpireUserJob(metaclass=MetaClass):
    next_time = timezone.localtime()

    @classmethod
    def start(cls):
        now = timezone.localtime()
        if now < cls.next_time:
            return
        # 隔天晚上9点
        tomorrow = (now + datetime.timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
        cls.next_time = tomorrow
        cls.doing()

    @classmethod
    @promise_do_once(class_name='ExpireUserJob')
    def doing(cls):
        # 明天到期的用户
        now = timezone.localtime()
        start_time = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = (now + datetime.timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        log.d(f'select expire user where start_time > {cls.start_time} and end_time <= {cls.end_time}')
        #
        orders = User.objects.filter(
            expired_at__gt=cls.start_time,
            expired_at__lte=cls.end_time,
            status=User.Status.UNPAID.value
        )
        for order in orders:
            cls.handle_order_unpaid(order)
        # 保存标签
        cls.start_time = cls.end_time
        cls.save_start_time(start_time=cls.start_time)
