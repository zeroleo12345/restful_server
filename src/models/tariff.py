import json
# 第三方库
from django.utils import timezone
from rest_framework import exceptions
from django.http.response import Http404
from dateutil.relativedelta import relativedelta
# 自己的库


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
    def get_object_or_404(tariff_name):
        # 单位分
        objects = {
           'month1': Tariff.Instance(tariff_name='month1', price=50*100, duration=1, unit='month'),
           'month3': Tariff.Instance(tariff_name='month3', price=144*100, duration=3, unit='month'),  # 单位分, 9.6折
           'month6': Tariff.Instance(tariff_name='month6', price=276*100, duration=6, unit='month'),  # 单位分, 9.2折
        }
        # objects = {
        #     'month1': Tariff.Instance(tariff_name='month1', price=1, duration=1, unit='month'),
        #     'month3': Tariff.Instance(tariff_name='month3', price=3, duration=3, unit='month'),
        #     'month6': Tariff.Instance(tariff_name='month6', price=6, duration=6, unit='month'),
        # }

        if tariff_name not in objects:
            raise Http404('No Tariff matches the given query.')
        return objects[tariff_name]

    @staticmethod
    def tariff_to_attach(tariff):
        tariff_name = tariff.tariff_name
        attach = json.dumps({'tariff_name': tariff_name})
        return attach

    @staticmethod
    def attach_to_tariff(attach):
        tariff_name = json.loads(attach)['tariff_name']
        tariff = Tariff.get_object_or_404(tariff_name=tariff_name)
        return tariff
