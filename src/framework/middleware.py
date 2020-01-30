import time
from django.http.response import HttpResponse


class CORSMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse(status=204)
            CORSMiddleware.set_cors_header(request.method, response)
            return response
        else:
            response = self.get_response(request)
            CORSMiddleware.set_cors_header(request.method, response)
            return response

    @staticmethod
    def set_cors_header(method, response):
        if method == 'OPTIONS':
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Origin, Authorization'
            response['Access-Control-Expose-Headers'] = 'Content-Type, Origin, Authorization'
            response['Access-Control-Max-Age'] = 1800
        else:
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Expose-Headers'] = 'Content-Type, Origin, Authorization'


class SystemTimeMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Time'] = int(time.time())
        return response


def get_client_ip(request):
    """
    nginx 透传客户端IP, 增加如下配置:
        proxy_set_header            Host $host;
        proxy_set_header            X-Real-IP $remote_addr;
        proxy_set_header            X-Forwarded-For $proxy_add_x_forwarded_for;
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip
