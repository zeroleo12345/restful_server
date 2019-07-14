from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
# 自己的库
from mybase3.mylog3 import log


# /debug 调试接口, 用于打印 HTTP body 和 HTTP 参数
class DebugView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        log.i(f'GET method')
        log.i(f'GET: {request.GET}')
        log.i(f'POST: {request.POST}')
        log.i(f'data: {request.data}')
        return Response()

    def post(self, request):
        log.i(f'POST method')
        log.i(f'GET: {request.GET}')
        log.i(f'POST: {request.POST}')
        log.i(f'data: {request.data}')
        data = request.data
        return Response(data=data)
