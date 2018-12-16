import signal
import time
from abc import ABC, abstractmethod
# 第三方类
import sentry_sdk
# 自己的类
from mybase3.mylog3 import log


class Service(ABC):
    interval = 20   # 单位秒
    term = 0

    def __init__(self):
        self.signal_register()

    @abstractmethod
    def run(self):
        pass

    def signal_register(self):
        """ 注册信号 """
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        if sig in [signal.SIGINT, signal.SIGTERM]:
            self.term = 1

    def start(self):
        try:
            # 消息循环
            while not self.term:
                self.run()
                time.sleep(self.interval)    # 睡眠 X 秒
        except KeyboardInterrupt:
            log.d('KeyboardInterrupt, break')
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
        finally:
            log.i(f'exit, term: {self.term}')
            log.close()
