from django.http.response import HttpResponse
from trade.framework.authorization import get_http_token_name, UserPermission, JWTAuthentication


class CORSMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response.status_code = 204

            response['Access-Control-Max-Age'] = 600
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Origin, Authorization'

            return response

        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Origin, Authorization'
        return response


class TokenSetMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        _HTTP_AUTHORIZATION = get_http_token_name()
        token = request.META.get(_HTTP_AUTHORIZATION, '')
        if UserPermission.is_user(request.user) and not token:
            response['Authorization'] = JWTAuthentication.jwt_encode_handler(request.user)

        return response
