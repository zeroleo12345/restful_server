# 参考:  https://docs.djangoproject.com/en/1.9/howto/custom-model-fields/#custom-database-types
import random
from decimal import Decimal
import datetime
# 第三方库
from django.db import models, connections
from django_redis import get_redis_connection
from django.utils.dateparse import parse_datetime
from gevent.queue import LifoQueue
from redis.connection import Connection, BlockingConnectionPool
from redis import Redis
# 项目库
from trade import settings
from utils.time import Datetime


def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def to_dict(self, fields=None, exclude=None):
    data = {}
    for f in self._meta.concrete_fields:
        value = f.value_from_object(self)

        if fields and f.name not in fields:
            continue

        if exclude and f.name in exclude:
            continue

        if isinstance(f, models.DateTimeField):
            value = Datetime.convert_timezone(value).isoformat() if value else ''
        elif isinstance(f, models.DateField):
            value = value.strftime('%Y-%m-%d') if value else ''
        elif isinstance(f, models.DecimalField):
            value = None if value is None else float(value)

        data[f.name] = value

    return data


def to_model(model, dct, fields=None, exclude=None):
    data = {}
    for f in model._meta.concrete_fields:
        value = dct[f.name]

        if fields and f.name not in fields:
            continue

        if exclude and f.name in exclude:
            continue

        if isinstance(f, models.DateTimeField):
            if value:
                value = parse_datetime(value)
            else:
                value = None
        elif isinstance(f, models.DateField):
            if value:
                value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
            else:
                value = None
        elif isinstance(f, models.DecimalField):
            value = Decimal(value)

        data[f.name] = value

    return model(**data)


def get_redis() -> Redis:
    return get_redis_connection()


def get_increase_id(key: str, max_increment=100) -> str:
    redis = get_redis()
    key = f'mysql:{key}:id'
    return str(redis.incrby(key, random.randint(1, max_increment)))


class MyBlockingConnectionPool(BlockingConnectionPool):
    def __init__(self, max_connections=50, timeout=20, connection_class=Connection, queue_class=LifoQueue, **connection_kwargs):
        # workaround:   https://github.com/andymccurdy/redis-py/blob/master/redis/connection.py
        super(self.__class__, self).__init__(
            max_connections=max_connections,
            timeout=timeout,
            connection_class=connection_class,
            queue_class=queue_class,
            **connection_kwargs,
        )


class DatabaseAppsRouter(object):
    DATABASE_MAPPING = settings.DATABASE_APPS_MAPPING
    """
    A router to control all database operations on models for different
    databases.

    In case an app is not set in settings.DATABASE_APPS_MAPPING, the router
    will fallback to the `default` database.

    DATABASE_APPS_MAPPING = {'app1': 'db1', 'app2': 'db2'}
    """

    def db_for_read(self, model, **hints):
        """"Point all read operations to the specific database."""
        if model._meta.app_label in self.DATABASE_MAPPING:
            return self.DATABASE_MAPPING[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        """Point all write operations to the specific database."""
        if model._meta.app_label in self.DATABASE_MAPPING:
            return self.DATABASE_MAPPING[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between apps that use the same database."""
        db_obj1 = self.DATABASE_MAPPING.get(obj1._meta.app_label)
        db_obj2 = self.DATABASE_MAPPING.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        return None

    # Django > 1.7
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db in self.DATABASE_MAPPING.values():
            return self.DATABASE_MAPPING.get(app_label) == db
        elif app_label in self.DATABASE_MAPPING:
            return False
        return None
