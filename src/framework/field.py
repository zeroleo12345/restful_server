import uuid
from enum import Enum
# 第三方库
from django.db import models
#
# from utils.redis_lock import RedisLock
# from utils.mysignal import SigTerm


# lock = RedisLock(max_worker_id=250)
# lock.start()
# SigTerm.add_term_handler(lock.stop)

# id_iterator = generator(worker_id=lock.get_worker_id(), data_center_id=1)


def new_uuid() -> str:
    """
    :return: 32位随机字符串
    """
    return uuid.uuid4().hex


class Char32Field(models.Field):
    def db_type(self, connection):
        return 'char(32)'


class ModelEnum(Enum):
    @classmethod
    def choices(cls):
        return [(e.value, e.name) for e in cls]

    @classmethod
    def values(cls):
        for x in cls:
            yield x.value
