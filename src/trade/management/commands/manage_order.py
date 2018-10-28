import os
import json
import datetime
import time
import pytz
import traceback
import signal
from django.core.management.base import BaseCommand
# 第三方类
# 自己的类
from trade.order.views import OrderNotifyView
from trade.order.models import Orders
from trade.utils.wepay import WePay
from mybase3.mylog3 import log

log.setLogHeader('order')
TZ = pytz.timezone('Asia/Shanghai')
INTERVAL = datetime.timedelta(minutes=10)  # 超时10分钟
TAG_FILE_PATH = 'time.tag'


class Command(BaseCommand):
    def handle(self, *args, **options):
        process = ServiceLoop()
        process.start()


class ServiceLoop(object):
    term = 0
    is_init = False
    start_time_dict = {"file": os.path.basename(__file__), "start_time": "2018-01-01 00:00:00"}

    def __init__(self):
        self.signal_register()

    def signal_register(self):
        """ 注册信号 """
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        if sig in [signal.SIGINT, signal.SIGTERM]:
            self.term = 1

    def cal_end_time(self):
        now_datetime = datetime.datetime.now(TZ)
        # 距离当前时间 INTERVAL 的时间点作为结束时间
        end_time = now_datetime - INTERVAL
        return end_time

    def start(self):
        start_time, end_time = self.init_start_time_end_time()
        try:
            # 消息循环
            while not self.term:
                end_time = self.cal_end_time()
                log.d(f'start_time: {start_time}, end_time: {end_time}')

                orders = Orders.objects.filter(created_at__gt=start_time, created_at__lte=end_time, status='unpaid')
                for order in orders:
                    self.handle_charge_status0(order)
                # 保存标签
                start_time = end_time
                self.save_start_time()
                # 睡眠X秒
                time.sleep(INTERVAL.total_seconds())
        except KeyboardInterrupt:
            log.d('KeyboardInterrupt, break')
        except Exception:
            log.e(traceback.format_exc())
        finally:
            log.i(f'exit, term: {self.term}')
            log.close()

    def handle_charge_status0(self, order):
        # 查询订单API文档: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_2
        # 关闭订单API文档: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_3
        # 下载对账单API文档: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_6

        out_trade_no = order.out_trade_no           # 商户订单号
        attach = order.attach
        total_fee = order.total_fee

        # 1. 查询订单API, 获取查询结果
        ret_json = WePay.WECHAT_PAY.order.query(None, out_trade_no)
        # OrderedDict([
        #  ('return_code', 'SUCCESS'), ('return_msg', 'OK'), ('appid', 'wx54d296959ee50c0b'), ('mch_id', '1517154171'),
        #  ('nonce_str', 'LQ36VyPkbS7tK7Nk'), ('sign', '5182234EB26EBFB718D5FDD1189E6056'), ('result_code', 'SUCCESS'),
        #  ('out_trade_no', '1540519817110XiX6jCKAmXb348V3e'), ('trade_state', 'NOTPAY'),
        #  ('trade_state_desc', '订单未支付')
        # ])
        log.d(f'order query from weixin: {ret_json}')

        if ret_json['return_code'] != 'SUCCESS':
            log.e('order query not success')
            return

        # 2. 检查签名
        if not WePay.WECHAT_PAY.check_signature(ret_json):
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
            OrderNotifyView.increase_user_resource(total_fee, out_trade_no, transaction_id, attach)
            Orders.objects.filter(out_trade_no=out_trade_no).update(status='paid', transaction_id=transaction_id)
            log.i(f"UPDATE orders SET status = 'paid', transaction_id = '{transaction_id}' WHERE out_trade_no = '{out_trade_no}'")

        elif trade_state in ['NOTPAY', 'CLOSED', 'PAYERROR']:

            # 超时还未支付或订单已经关闭, 需把charge记录状态从0改为-1
            Orders.objects.filter(out_trade_no=out_trade_no).update(status='expired')
            log.i(f"UPDATE orders SET status = 'expired' WHERE out_trade_no = '{out_trade_no}'")

    @property
    def start_time(self):
        return self.start_time_dict['start_time']

    @start_time.setter
    def start_time(self, yyyymmddHHMMSS):
        self.start_time_dict['start_time'] = yyyymmddHHMMSS

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
        if now_datetime - start_time < INTERVAL:
            time.sleep(INTERVAL.total_seconds())   # 睡眠X秒, 再处理

        # 距离当前时间 INTERVAL 的时间点作为结束时间
        end_time = now_datetime - INTERVAL

        log.i(f'init start_time: {start_time}, end_time: {end_time}')
        return start_time, end_time
