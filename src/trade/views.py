# django 库
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
# 第三方库
from wechatpy.utils import check_signature


class EchoStrView(APIView):
    authentication_classes = ()
    permission_classes = ()
    renderer_classes = (StaticHTMLRenderer,)

    def get(self, request):
        # {URL}/echostr?signature=40lenString&echostr=16809769573550014143&timestamp=1527776959&nonce=1011789502
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        check_signature(settings.TOKEN, signature, timestamp, nonce)
        return Response(echostr)
