import datetime
# 第三方类
from django.utils import timezone
from django.db import connection
# 自己的类
from . import MetaClass
from framework.database import dict_fetchall
from utils.slack import send_slack_message
from utils.decorators import promise_do_once
from trade.settings import log
from pprint import pprint


class IllegalDot1xUserJob(metaclass=MetaClass):
    next_time = timezone.localtime()

    @classmethod
    def start(cls, force=False):
        now = timezone.localtime()
        if not force and now < cls.next_time:
            return
        # 隔天早上7点
        tomorrow = (now + datetime.timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        cls.next_time = tomorrow
        #
        start_time = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time - datetime.timedelta(days=1)
        cls.doing(start_time=start_time, end_time=end_time)

    @classmethod
    @promise_do_once(file_name='illegal_dot1x_user', func_name='doing')
    def doing(cls, start_time, end_time):
        # 所有public的AP
        public_ap = set()
        ap_owner = dict()
        sql = f"""
        SELECT * FROM ap_owner WHERE is_public = 1;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            for row in dict_fetchall(cursor):
                username = row['username']
                ap_mac = row['ap_mac']
                is_public = row['is_public']
                if is_public:
                    public_ap.add(ap_mac)
                if ap_mac not in ap_owner:
                    ap_owner[ap_mac] = set()
                ap_owner[ap_mac].add(username)

        # 按username统计连接最多的AP, 作为用户绑定的常用AP. 需排除is_public的AP
        username_ap = dict()
        # TODO 加上时间筛选, 30天内
        sql = f"""
        SELECT username, ap_mac, count(*) AS accept_count FROM stat_user GROUP BY username, ap_mac ORDER BY accept_count DESC;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            for row in dict_fetchall(cursor):
                username = row['username']
                ap_mac = row['ap_mac']
                accept_count = row['accept_count']
                if ap_mac in public_ap:
                    continue
                if ap_mac in ap_owner:
                    # 跳过已绑定用户的AP
                    continue
                if username in username_ap:
                    # 绑定关系已处理
                    continue
                else:
                    username_ap[username] = f'{ap_mac}:{accept_count}'

        # 按 username, user_mac 统计, 告警: 不等于该ap_owner的username
        username_usermac_ap = dict()
        sql = f"""
        SELECT username, user_mac, ap_mac, count(*) AS accept_count FROM stat_user GROUP BY username, user_mac, ap_mac ORDER BY accept_count DESC;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            for row in dict_fetchall(cursor):
                username = row['username']
                user_mac = row['user_mac']
                ap_mac = row['ap_mac']
                accept_count = row['accept_count']
                #
                if ap_mac in ap_owner:
                    # 跳过已绑定用户的AP
                    continue
                if ap_mac in public_ap:
                    # 公用AP跳过
                    continue
                if f'{username}:{user_mac}' in username_usermac_ap:
                    # 绑定关系已处理
                    continue
                else:
                    username_usermac_ap[f'{username}:{user_mac}'] = ap_mac

        pprint(f'username_ap: {username_ap}')
        pprint(f'username_usermac_ap: {username_usermac_ap}')
        for key, value in username_usermac_ap.items():
            username, user_mac = key.split(':')
            ap_mac = value
            correct_ap_mac, correct_accept_count = username_ap[username].split(':')
            if ap_mac == correct_ap_mac:
                continue
            log.e(f'username: {username}, user_mac: {user_mac} 应绑定AP: {correct_ap_mac}, 次数: {correct_accept_count}. 但现连接: {ap_mac}')
            # 发送slack统计消息
            # text = f'昨天充值金额: {today_sum/100} 元, 历史累计充值金额: {total_sum/100} 元'
            # send_slack_message(text=text)
