import json
# 第三方库
from django.utils import timezone
from dateutil.relativedelta import relativedelta
# 项目库


# 资费
class Tariff(object):
    def __init__(self, price, speed, duration):
        self.tariff_name = f'{speed}M_{duration}month'      # 套餐ID
        # 价格
        self.price = price                  # 单位: 分
        self.price_desc = f'{price/100}元'
        self.price_red_desc = f'优惠!仅{price//duration}元/月'
        # 宽带速度
        self.speed = speed
        self.speed_desc = f'{speed}M'
        # 时长
        self.duration = duration
        self.duration_desc = f'充值{duration}个月'

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


class Tariffs(object):
    """
    1Byte = 8bit
    1M = 1000 Kbit/s -> 1000 / 8 KByte
    """
    tariffs = [
        # 4M
        [
            Tariff(speed=4, duration=1, price=50*100),
            Tariff(speed=4, duration=3, price=150*100),
            Tariff(speed=4, duration=6, price=300*100),
            Tariff(speed=4, duration=12, price=600*100),
        ],
        # 8M
        [
            Tariff(speed=8, duration=1, price=50*100),
            Tariff(speed=8, duration=3, price=150*100),
            Tariff(speed=8, duration=6, price=300*100),
            Tariff(speed=8, duration=12, price=600*100),
        ],
        # 20M
        [
            Tariff(speed=20, duration=1, price=50*100),
            Tariff(speed=20, duration=3, price=150*100),
            Tariff(speed=20, duration=6, price=300*100),
            Tariff(speed=20, duration=12, price=600*100),
        ],
        # 50M
        [
            Tariff(speed=50, duration=1, price=50*100),
            Tariff(speed=50, duration=3, price=150*100),
            Tariff(speed=50, duration=6, price=300*100),
            Tariff(speed=50, duration=12, price=600*100),
        ],
    ]

    @classmethod
    def get_tariff(cls, tariff_name: str) -> 'Tariff':
        for t in cls.tariffs:
            if t.tariff_name == tariff_name:
                return t
        return None
