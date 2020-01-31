# 第三方库
from django.http.response import HttpResponse
from rest_framework import exceptions
# 项目库
from framework.database import get_redis
from framework.restful import MyJSONRenderer
from framework.exception import GlobalException

render = MyJSONRenderer()


def cache_response():
    """
    缓存应答
    :return:
    """
    def decorator(func):
        key = f'cache_response_{func.__module__}.{func.__name__}'

        def wrapper(_self, request, **kwargs):
            redis_client = get_redis()

            content, content_type = redis_client.hmget(key, 'content', 'content_type')
            if content:
                http_response = HttpResponse(content=content, content_type=content_type)
                return http_response

            # 调用原函数
            response = func(_self, request, **kwargs)
            # FIXME response.data
            http_response = HttpResponse(render.render(response.data), content_type=render.media_type)
            mapping = {
                'content': http_response.content,
                'content_type': http_response.get('Content-Type'),
            }
            redis_client.hmset(key, mapping)
            # 返回
            return http_response

        return wrapper

    return decorator


def check_user_input(param, data, status=200):
    """
    用于检查用户输入参数, 此时不应由DRF框架处理返回400, 应该是返回200, 让前端弹窗提示!
    :param param: 参数名
    :param data: HTTP应答json数据, 类型为字典
    :param status: HTTP应答状态码
    :return:
    """
    def decorator(func):
        def wrapper(_self, request, **kwargs):
            # 调用原函数
            try:
                response = func(_self, request, **kwargs)
            except exceptions.ValidationError as e:
                if isinstance(e.detail, dict) and param in e.detail:
                    return HttpResponse(render.render(data), content_type=render.media_type, status=status)
                else:
                    raise e
            # 返回
            http_response = HttpResponse(render.render(response.data), content_type=render.media_type)
            return http_response

        return wrapper

    return decorator


def check_sms_rate(expire_seconds: int, max_count: int, raise_exception: bool = False, toggle: bool = True):
    """
    限制重发短信间隔
    :return:
    """
    def decorator(func):
        def wrapper(mobile, **kwargs):
            assert mobile
            if toggle:
                redis = get_redis()
                send_key = f'{func.__name__}:{mobile}'
                with redis.pipeline(transaction=False) as pipe:
                    pipe.incr(name=send_key)
                    pipe.ttl(name=send_key)
                    current_count, wait_seconds = pipe.execute()
                if wait_seconds <= 0:
                    wait_seconds = expire_seconds
                    redis.expire(name=send_key, time=expire_seconds)
                if current_count > max_count:
                    if raise_exception:
                        raise GlobalException(data={'code': 'sms_forbidden', 'message': f'短信发送频繁, 请在{wait_seconds}秒后重试'}, status=200)
                    else:
                        # 什么也不做, 直接返回
                        return
            # 调用原函数
            return func(mobile, **kwargs)

        return wrapper

    return decorator
