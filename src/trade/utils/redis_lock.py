import threading
import time
# 第三方库
import sentry_sdk
# 项目库
from trade.settings import log
from trade import settings
from trade.framework.database import get_redis
from trade.utils.signal import SigTerm


class RedisLock(object):
    worker_id = None
    pod_uid = settings.POD_UID
    thread = None
    is_process_exit = False
    is_released = False

    def __init__(self, max_worker_id: int, expire_time=30, process_name='worker1'):
        assert isinstance(max_worker_id, int)
        assert expire_time > 10
        #
        self.max_worker_id = max_worker_id
        self.expire_time = expire_time
        self.process_name = process_name
        #
        self.redis = get_redis()
        script = """
        if ARGV[1] == redis.call("get", KEYS[1]) then
            redis.call("expire", KEYS[1], ARGV[2])
            return 1
        end
        return 0
        """
        self.get_and_expire = self.redis.register_script(script)
        #
        script = """
        if ARGV[1] == redis.call("get", KEYS[1]) then
            redis.call("del", KEYS[1])
            return 1
        end
        return 0
        """
        self.get_and_delete = self.redis.register_script(script)

    def __del__(self):
        self.release_lock()

    @staticmethod
    def get_key(process_name: str, worker_id: int):
        return f'worker:{process_name}:{worker_id}'

    def refresh_lock(self):
        last = 0
        while 1:
            if SigTerm.is_term or self.is_process_exit:
                result = self.release_lock()
                log.d(f'release lock. result: {result}')
                raise SystemExit()
            now = int(time.time())
            if now - last < (self.expire_time / 2):
                continue
            else:
                last = now
            key = self.get_key(process_name=self.process_name, worker_id=self.worker_id)
            is_success = self.get_and_expire(keys=[key], args=[self.pod_uid, self.expire_time])
            if not is_success:
                sentry_sdk.capture_message(f'refresh lock fail. key: {key}, pod_uid: {self.pod_uid}')
            log.t(f'success refresh lock. key: {key}')
            time.sleep(1)

    def release_lock(self):
        if self.is_released:
            return
        self.is_released = True
        key = self.get_key(process_name=self.process_name, worker_id=self.worker_id)
        is_success = self.get_and_delete(keys=[key], args=[self.pod_uid])
        if not is_success:
            if not self.worker_id:
                log.d(f'no need release because not get lock, worker_id: {self.worker_id}')
                return -1
            sentry_sdk.capture_message(f'release lock fail. key: {key}')
        return is_success

    def acquire_lock(self) -> int:
        """
        :return: 0 - 未获取到锁
        """
        for worker_id in range(1, self.max_worker_id+1):
            key = self.get_key(process_name=self.process_name, worker_id=worker_id)
            is_set = self.redis.set(key, value=self.pod_uid, ex=self.expire_time, nx=True)
            if is_set:
                return int(worker_id)
        return 0

    def get_worker_id(self, blocking=True) -> int:
        if not self.worker_id:
            _id = self.acquire_lock()
            if _id == 0:
                if blocking:
                    if SigTerm.is_term:
                        raise SystemExit()
                    log.w(f'not acquire lock, sleep and reacquire')
                    time.sleep(self.expire_time)
                    return self.get_worker_id()
                else:
                    error = f'worker id is full! max_worker_id: {self.max_worker_id}'
                    sentry_sdk.capture_message(error)
                    raise Exception(error)
            self.worker_id = _id
        log.i(f'Success create worker id: {self.worker_id}')
        assert self.worker_id >= 1
        assert self.worker_id <= self.max_worker_id
        return self.worker_id

    def start(self):
        """ 开始 """
        self.get_worker_id(blocking=True)
        self.thread = threading.Thread(target=self.refresh_lock)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """ 停止 """
        if not self.thread:
            return
        self.is_process_exit = True
        self.thread.join(3)


if __name__ == '__main__':
    lock = RedisLock(max_worker_id=1, expire_time=30, process_name='timer_processor')
    try:
        lock.start()
    finally:
        lock.stop()
