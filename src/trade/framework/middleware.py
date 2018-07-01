from django.http.response import HttpResponse
from trade.framework.authorization import UserPermission, JWTAuthentication


class CORSMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse(status=204)
            CORSMiddleware.set_cors_header(response)
            return response
        else:
            response = self.get_response(request)
            CORSMiddleware.set_cors_header(response)
            return response

    @staticmethod
    def set_cors_header(response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Max-Age'] = 1800    # 只对 OPTIONS 生效
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Origin, Authorization'
        response['Access-Control-Expose-Headers'] = 'Content-Type, Origin, Authorization'


class TokenSetMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        token = request.META.get('HTTP_AUTHORIZATION', '')
        if UserPermission.is_user(request.user) and not token:
            response['Authorization'] = JWTAuthentication.jwt_encode_handler(request.user)

        return response
