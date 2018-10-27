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
from trade.order.models import Orders
from trade.utils.wepay import WePay
from mybase3.mylog3 import log

TZ = pytz.timezone('Asia/Shanghai')
INTERVAL = datetime.timedelta(minutes=10)  # 超时10分钟
TAG_FILE_PATH = 'start_time.tag'


class Command(BaseCommand):
    def handle(self, *args, **options):
        process = ServiceLoop()
        process.start()


class ServiceLoop(object):
    term = 0
    is_init = False
    start_time_dict = {"file": os.path.basename(__file__), "start_time": "2018-01-01 00:00:00"}

    def __init__(self):
        self.start_time, self.end_time = self.init_start_time_end_time()
        self.signal_register()

    def signal_register(self):
        """ 注册信号 """
        signal.signal(signal.SIGINT, self._sig_handler)
        signal.signal(signal.SIGTERM, self._sig_handler)

    def signal_handler(self, sig, frame):
        if sig in [signal.SIGINT, signal.SIGTERM]:
            self.term = 1

    def cal_end_time(self):
        now_datetime = datetime.datetime.now(TZ)
        # 距离当前时间 INTERVAL 的时间点作为结束时间
        end_time = (now_datetime - INTERVAL).strftime('%Y-%m-%d %H:%M:%S')
        return end_time

    def start(self):
        try:
            # 消息循环
            while not self.term:
                self.end_time = self.cal_end_time()
                log.d('start_time: {self.start_time}, end_time: {self.end_time}')

                orders = Orders.objects.filter(created_at__gt=self.start_time, created_at__lte=self.end_time, status='unpaid')
                for order in orders:
                    self.handle_charge_status0(order)
                # 保存标签
                self.start_time = self.end_time
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

        transaction_id = order.transaction_id       # 微信订单号
        out_trade_no = order.out_trade_no           # 商户订单号

        # 1. 查询订单API, 获取查询结果
        ret_json = WePay.WECHAT_PAY.order.query(transaction_id, out_trade_no)
        log.i("order query from weixin:{}".format(ret_json))

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

            # 支付成功, 先检查total_fee是否一致, 然后把charge记录状态从0改为1, transaction_id更新为微信返回值
            wx_total_fee = int(ret_json['total_fee'])
            if wx_total_fee != order.total_fee:
                log.e(f'wx total_fee: {wx_total_fee} != db total_fee:{order.total_fee}')
                return

            # 更新表状态: 未支付 改为 已支付 和 微信订单号
            transaction_id = ret_json['transaction_id']
            Orders.objects.get(out_trade_no=out_trade_no).update(status='paid', transaction_id=transaction_id)

        elif trade_state in ['NOTPAY', 'CLOSED', 'PAYERROR']:

            # 超时还未支付或订单已经关闭, 需把charge记录状态从0改为-1
            log.w(f'update orders status to expired, out_trade_no:{out_trade_no}')
            Orders.objects.get(out_trade_no=out_trade_no).update(status='expired')

    @property
    def start_time(self):
        return self.start_time_dict['start_time']

    @start_time.setter
    def start_time(self, yyyymmddHHMMSS):
        self.start_time_dict['start_time'] = yyyymmddHHMMSS

    def save_start_time(self):
        with open(TAG_FILE_PATH, 'wb') as f:
            json.dump(self.start_time_dict, f)

    def init_start_time_end_time(self):
        if os.path.exists(TAG_FILE_PATH):
            with open(TAG_FILE_PATH, 'r') as f:
                self.start_time_dict = json.load(f)

        if self.start_time_dict['file'] != os.path.basename(__file__):
            raise Exception('tag file mismatch, file: {}', self.start_time_dict['file'])

        # 1. 标签存在, 以标签记录时间为开始时间; 2. 标签不存在, 以2018年1月1日为开始时间
        start_time = self.start_time_dict['start_time']

        now_datetime = datetime.datetime.now(TZ)
        if now_datetime - TZ.localize(datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")) < INTERVAL:
            time.sleep(INTERVAL.total_seconds())   # 睡眠X秒, 再处理

        # 距离当前时间 INTERVAL 的时间点作为结束时间
        end_time = (now_datetime - INTERVAL).strftime('%Y-%m-%d %H:%M:%S')

        return start_time, end_time
