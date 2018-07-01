from django.http.response import HttpResponse
from trade.framework.authorization import UserPermission, JWTAuthentication


class CORSMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # request.method = OPTIONS 为什么会不同?
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Origin, Authorization'
        response['Access-Control-Expose-Headers'] = 'Content-Type, Origin, Authorization'
        return response


class TokenSetMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        token = request.META.get('HTTP_AUTHORIZATION', '')
        if UserPermission.is_user(request.user) and not token:
            response['Authorization'] = JWTAuthentication.jwt_encode_handler(request.user)

        return response
