import datetime
# 第三方库
from django.utils import timezone
# 项目库
from . import MetaClass
from utils.decorators import promise_do_once
from trade.settings import log
from models import Account, User
from service.wechat.we_message import WePush


class ExpireUserJob(metaclass=MetaClass):
    next_time = timezone.localtime()

    @classmethod
    def start(cls):
        now = timezone.localtime()
        if now < cls.next_time:
            return
        if now.hour < 9:
            return
        # 隔天晚上9点
        cls.next_time = (now + datetime.timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
        cls.next_time = now + datetime.timedelta(minutes=1)
        #
        start_time = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = (now + datetime.timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        cls.doing(start_time=start_time, end_time=end_time)

    @classmethod
    @promise_do_once(file_name='expire_user', func_name='doing')
    def doing(cls, start_time, end_time):
        # 明天到期的用户
        log.d(f'select expire account where start_time > {start_time} and end_time <= {end_time}')
        #
        accounts = Account.objects.filter(
            expired_at__gt=start_time,
            expired_at__lte=end_time,
        )
        for account in accounts:
            user = User.get(user_id=account.user_id)
            log.i(f'send wechat template message, openid: {user.openid}, expired_at: {account.expired_at}')
            WePush.notify_account_expire(openid=user.openid, username=account.username, expired_at=account.expired_at)
