import json
# 第三方库
from django.utils import timezone
from rest_framework import exceptions
from django.http.response import Http404
from dateutil.relativedelta import relativedelta
# 项目库


# 资费
class Tariff(object):
    class Instance(object):
        def __init__(self, tariff_name, price, duration, unit):
            self.tariff_name = tariff_name      # 套餐ID
            self.price = price                  # 单位: 分
            self.duration = duration
            self.unit = unit

        def increase_duration(self, start_datetime):
            # 如果有效期 < 当前时间, 则重置为当前时间再叠加有效期
            now = timezone.localtime()
            if start_datetime < now:
                start_datetime = now

            if self.unit == 'month':
                return start_datetime + relativedelta(months=self.duration)
            raise exceptions.ValidationError('时长单位错误', 'invalid_unit')

    @staticmethod
    def get_object_or_404(tariff_name: str):
        tariffs = [
           Tariff.Instance(tariff_name='month1', price=50*100, duration=1, unit='month'),     # 单位分
           Tariff.Instance(tariff_name='month3', price=150*100, duration=3, unit='month'),    # 单位分
           Tariff.Instance(tariff_name='month6', price=300*100, duration=6, unit='month'),    # 单位分
        ]
        for t in tariffs:
            if t.tariff_name == tariff_name:
                return t
        raise Http404('No Tariff matches the given query.')

    @staticmethod
    def tariff_to_attach(tariff):
        tariff_name = tariff.tariff_name
        attach = json.dumps({'tariff_name': tariff_name})
        return attach

    @staticmethod
    def convert_from_attach(attach: str):
        tariff_name = json.loads(attach)['tariff_name']
        tariff = Tariff.get_object_or_404(tariff_name=tariff_name)
        return tariff
