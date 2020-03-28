import time
import traceback
import pkgutil
# 第三方库
import sentry_sdk
# 项目库
from framework.database import close_old_connections
from utils.redis_lock import RedisLock
from trade.settings import log
from .jobs import MetaClass
from . import jobs
for importer, modname, ispkg in pkgutil.iter_modules(jobs.__path__, prefix=jobs.__loader__.name+'.'):
    __import__(modname)


class MainLoop(object):
    @staticmethod
    def add_arguments(parser):
        pass

    @staticmethod
    def handle(*args, **options):
        task = Task()
        task.start()


class Task(object):
    sleep_seconds = 60

    def start(self):
        # 需支持高可用, 多进程互斥, 只有1个进程在处理
        lock = RedisLock(max_worker_id=1, expire_time=30, process_name='timer_processor')
        try:
            lock.start()
            log.d(f'jobs: {MetaClass.jobs}')
            while True:
                # FIXME SigTerm, PidFile
                close_old_connections()     # workaround:   https://zhaojames0707.github.io/post/django_mysql_gone_away/
                for job_class in MetaClass.jobs:
                    job_class.start()
                time.sleep(self.sleep_seconds)
        except Exception as e:
            log.e(traceback.format_exc())
            if not isinstance(e, SystemExit):
                sentry_sdk.capture_exception(e)
        finally:
            lock.stop()
