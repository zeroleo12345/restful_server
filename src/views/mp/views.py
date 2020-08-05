# django 库
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
# 第三方库
from wechatpy.utils import check_signature
from wechatpy.events import SubscribeEvent
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply
from wechatpy import parse_message
import sentry_sdk
# 项目库


class EchoStrView(APIView):
    authentication_classes = ()
    permission_classes = ()
    renderer_classes = (StaticHTMLRenderer,)    # response的content-type方式, 会使用指定类序列化body

    # /mp/echostr
    def get(self, request):
        """
        URL样例:  {URL}/echostr?signature=40lenString&echostr=16809769573550014143&timestamp=1527776959&nonce=1011789502
        """
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        check_signature(settings.MP_TOKEN, signature, timestamp, nonce)
        return Response(echostr)

    def post(self, request):
        # 公众号平台事件通知. (note: 使用平台自带的自定义菜单时, 平台不会下发消息)
        try:
            xml = request.body
            msg = parse_message(xml)
            from trade.settings import log
            log.d(f'platform event notify: {msg}')
            appid = msg.target     # 例如: gh_9225266caeb1
            from_user_openid = msg.source
            if isinstance(msg, SubscribeEvent):   # 关注公众号事件
                reply = TextReply()
                reply.source = appid
                reply.target = from_user_openid
                reply.content = settings.MP_DEFAULT_REPLY
                xml = reply.render()
                return HttpResponse(xml, content_type='text/xml')
            elif isinstance(msg, TextMessage):    # 文本消息
                if msg.content in ['help', '帮助']:
                    command = ['openid']
                    message = '命令: ' + ','.join(command)
                elif msg.content == 'openid':
                    message = f'你的openid: {from_user_openid}'
                else:
                    message = settings.MP_DEFAULT_REPLY
                reply = TextReply()
                reply.source = appid
                reply.target = from_user_openid
                reply.content = message
                xml = reply.render()
                return HttpResponse(content=xml, content_type='text/xml')
            else:
                return Response('success')
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
            return Response('success')
