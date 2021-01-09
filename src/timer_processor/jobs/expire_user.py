import datetime
# 第三方库
from django.utils import timezone
# 项目库
from . import MetaClass
from utils.decorators import promise_do_once
from trade.settings import log
from models import Account, Client
from service.wechat.we_client import WeClient
from service.wechat.we_message import we_message
from utils.time import Datetime
from trade import settings

MP_RECHARGE_TEMPLATE_ID = settings.MP_RECHARGE_TEMPLATE_ID


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
            user = Client.get(id=account.user_id)
            data = {
                'first': {'value': '您的宽带即将到期'},
                'keyword1': {'value': account.username},
                'keyword2': {'value': f'到期时间 {Datetime.to_str(account.expired_at, fmt="%Y-%m-%d %H:%M")}'},
                'remark': {'value': '如需继续使用, 请点击充值'}
            }
            log.i(f'send wechat template message, openid: {user.openid}, expired_at: {account.expired_at}')
            we_message.send_template(user.openid, MP_RECHARGE_TEMPLATE_ID, data, url=WeClient.recharge_uri, mini_program=None)
