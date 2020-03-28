import os
import json
import datetime
import time
import pytz
# 第三方类
from django.core.management.base import BaseCommand
# 自己的类
from trade.management.commands import Service
from models import BroadBandOrder
from service.wechat.we_pay import WePay
from trade.settings import log
from controls.resource import increase_user_resource

log.set_header('order')
TZ = pytz.timezone('Asia/Shanghai')
TEN_MINUTE_DELTA = datetime.timedelta(minutes=10)  # 超时10分钟
TAG_FILE_PATH = 'time.tag'


# 使用方法:  python manage.py expire_order
class Command(BaseCommand):
    def handle(self, *args, **options):
        process = ServiceLoop()
        process.start()


class ServiceLoop(Service):
    start_time_dict = {"file": os.path.basename(__file__), "start_time": "2018-01-01 00:00:00"}

    def __init__(self):
        super(self.__class__, self).__init__()
        self.start_time, self.end_time = self.init_start_time_end_time()

    @staticmethod
    def calculate_end_time():
        now_datetime = datetime.datetime.now(TZ)
        # 距离当前时间 TEN_MINUTE_DELTA 的时间点作为结束时间
        end_time = now_datetime - TEN_MINUTE_DELTA
        return end_time

    def run(self):
        self.end_time = self.calculate_end_time()
        log.d(f'select unpaid order where start_time > {self.start_time} and end_time <= {self.end_time}')
        #
        orders = BroadBandOrder.objects.filter(
            created_at__gt=self.start_time,
            created_at__lte=self.end_time,
            status=BroadBandOrder.Status.UNPAID.value
        )
        for order in orders:
            self.handle_charge_status0(order)
        # 保存标签
        self.start_time = self.end_time
        self.save_start_time()

    def handle_charge_status0(self, order):
        # 查询订单API文档: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_2
        # 关闭订单API文档: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_3
        # 下载对账单API文档: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_6
        out_trade_no = order.out_trade_no           # 商户订单号
        attach = order.attach
        total_fee = order.total_fee

        # 1. 查询订单API, 获取查询结果
        ret_json = WePay.query_order(out_trade_no)
        # OrderedDict([
        #  ('return_code', 'SUCCESS'), ('return_msg', 'OK'), ('appid', 'wx54d296959ee50c0b'), ('mch_id', '1517154171'),
        #  ('nonce_str', 'LQ36VyPkbS7tK7Nk'), ('sign', '5182234EB26EBFB718D5FDD1189E6056'), ('result_code', 'SUCCESS'),
        #  ('out_trade_no', '1540519817110XiX6jCKAmXb348V3e'), ('trade_state', 'NOTPAY'),
        #  ('trade_state_desc', '订单未支付')
        # ])
        log.d(f'order query from weixin: {ret_json}')
        #
        if ret_json['return_code'] != 'SUCCESS':
            log.e('order query not success')
            return

        # 2. 检查签名
        if not WePay.is_right_sign(ret_json):
            log.e('sign illegal, sign:{}', ret_json['sign'])
            return

        if ret_json['result_code'] != 'SUCCESS':
            log.e('check signature not success')
            return

        # 3. 交易状态分支处理
        trade_state = ret_json['trade_state']

        if trade_state == 'SUCCESS':

            wx_total_fee = int(ret_json['total_fee'])
            transaction_id = ret_json['transaction_id']

            # 支付成功, 先检查total_fee是否一致, 然后把charge记录状态从0改为1, transaction_id更新为微信返回值
            if wx_total_fee != total_fee:
                log.e(f'total_fee: {wx_total_fee} != order.total_fee:{total_fee}')
                return

            # 增加用户免费资源
            increase_user_resource(total_fee, out_trade_no, transaction_id, attach)
            BroadBandOrder.objects.filter(out_trade_no=out_trade_no).update(status='paid', transaction_id=transaction_id)
            log.i(f"UPDATE broadband_order SET status = 'paid', transaction_id = '{transaction_id}' WHERE out_trade_no = '{out_trade_no}'")

        elif trade_state in ['NOTPAY', 'CLOSED', 'PAYERROR']:

            # 超时还未支付或订单已经关闭, 需把charge记录状态从0改为-1
            BroadBandOrder.objects.filter(out_trade_no=out_trade_no).update(status='expired')
            log.i(f"UPDATE broadband_order SET status = 'expired' WHERE out_trade_no = '{out_trade_no}'")

    def save_start_time(self):
        with open(TAG_FILE_PATH, 'w', encoding='utf8') as f:
            json.dump(self.start_time_dict, f)

    def init_start_time_end_time(self):
        if os.path.exists(TAG_FILE_PATH):
            with open(TAG_FILE_PATH, 'r') as f:
                self.start_time_dict = json.load(f)

        if self.start_time_dict['file'] != os.path.basename(__file__):
            raise Exception('tag file mismatch, file: {}', self.start_time_dict['file'])

        # 1. 标签存在, 以标签记录时间为开始时间; 2. 标签不存在, 以2018年1月1日为开始时间
        start_time = TZ.localize(datetime.datetime.strptime(self.start_time_dict['start_time'], "%Y-%m-%d %H:%M:%S"))

        now_datetime = datetime.datetime.now(TZ)
        if now_datetime - start_time < TEN_MINUTE_DELTA:
            time.sleep(TEN_MINUTE_DELTA.total_seconds())   # 睡眠X秒, 再处理

        # 距离当前时间 TEN_MINUTE_DELTA 的时间点作为结束时间
        end_time = now_datetime - TEN_MINUTE_DELTA

        log.i(f'init. start_time: {start_time}, end_time: {end_time}')
        return start_time, end_time
