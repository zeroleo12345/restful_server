from rest_framework.views import APIView
from rest_framework.response import Response
# 自己的库
from mybase3.mylog3 import log


# /debug 调试接口, 用于打印 HTTP body 和 HTTP 参数
class DebugView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def detail(self, request):
        log.i(f'request.content_type: {request.content_type}')
        log.i(f'request.encoding: {request.encoding}')
        log.i(f'request.body: {request.body}')
        log.i(f'request.GET: {request.GET}')
        log.i(f'request.POST: {request.POST}')
        log.i(f'request.data: {request.data}')

    def get(self, request):
        log.i(f'GET method')
        self.detail(request)
        return Response()

    def post(self, request):
        log.i(f'POST method')
        self.detail(request)
        data = request.data
        return Response(data=data)
