from rest_framework.views import APIView
# 项目库
from trade.settings import log
from framework.restful import BihuResponse


class DebugView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def detail(self, request):
        log.i(f'request.META: {request.META}')
        log.i(f'request.content_type: {request.content_type}')
        log.i(f'request.encoding: {request.encoding}')
        log.i(f'request.body: {request.body}')
        log.i(f'request.GET: {request.GET}')
        log.i(f'request.POST: {request.POST}')
        log.i(f'request.data: {request.data}')

    # /debug?abc=123 调试接口, 用于打印 HTTP body 和 HTTP 参数
    def get(self, request):
        log.i(f'GET method')
        self.detail(request)
        return BihuResponse()

    def post(self, request):
        log.i(f'POST method')
        self.detail(request)
        data = request.data
        return BihuResponse(data=data)
