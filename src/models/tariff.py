import json
# 第三方库
from django.utils import timezone
from dateutil.relativedelta import relativedelta
# 项目库


# 资费
class Tariff(object):
    def __init__(self, per_month_price, speed, month):
        self.tariff_name = f'{speed}M_{month}month'      # 套餐ID
        # 价格
        self.price = per_month_price * month                  # 单位: 分
        self.price_desc = f'{"{:g}".format(self.price/100)}元'
        self.price_red_desc = f'平均{per_month_price//100}元/月'
        # 宽带速度
        self.speed = speed
        self.speed_desc = f'{speed}M'
        # 时长
        self.duration = month
        self.duration_desc = f'充值{month}个月'

    def increase_duration(self, start_datetime):
        # 如果有效期 < 当前时间, 则重置为当前时间再叠加有效期
        now = timezone.localtime()
        if start_datetime < now:
            start_datetime = now

        return start_datetime + relativedelta(months=self.duration)

    def convert_to_attach(self) -> str:
        attach = json.dumps({'tariff_name': self.tariff_name})
        return attach

    @staticmethod
    def convert_from_attach(attach: str) -> 'Tariff':
        tariff_name = json.loads(attach)['tariff_name']
        return Tariffs.get_tariff(tariff_name=tariff_name)

    def to_dict(self):
        return {
            'tariff_name': self.tariff_name,
            'price': self.price,
            'price_desc': self.price_desc,
            'price_red_desc': self.price_red_desc,
            'speed': self.speed,
            'speed_desc': self.speed_desc,
            'duration': self.duration,
            'duration_desc': self.duration_desc,
        }


class Tariffs(object):
    """
    1Byte = 8bit
    电信宽带1M = 1000 Kbit/s = 1000 / 8 KByte/s = 125KB/s = 125*8 kbps = 125*8*1000 bit/s
    """
    all = [
        # 4M
        Tariff(speed=4, month=6, per_month_price=50*100),
        Tariff(speed=4, month=3, per_month_price=60*100),
        # 8M
        Tariff(speed=8, month=6, per_month_price=60*100),
        Tariff(speed=8, month=3, per_month_price=75*100),
        # 12M
        Tariff(speed=12, month=6, per_month_price=70*100),
        Tariff(speed=12, month=3, per_month_price=90*100),
        # 50M
        Tariff(speed=50, month=6, per_month_price=90*100),
        Tariff(speed=50, month=3, per_month_price=120*100),
    ]

    @classmethod
    def get_tariff(cls, tariff_name: str) -> 'Tariff':
        for t in cls.all:
            if t.tariff_name == tariff_name:
                return t
        return None
