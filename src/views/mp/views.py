import traceback
# 第三方库
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from wechatpy.utils import check_signature
from wechatpy.events import SubscribeEvent
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply, ArticlesReply
from wechatpy import parse_message
import sentry_sdk
# 项目库
from utils.time import Datetime
from trade.settings import log

search_expired = 0


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
            # log.d(f'platform event notify: {msg}')
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
                    command = ['openid', 'search']
                    message = '命令: ' + ','.join(command)
                elif msg.content == 'openid':
                    message = f'你的openid: {from_user_openid}'
                elif msg.content == 'search':
                    message = '已进入搜索模式'
                    global search_expired
                    search_expired = Datetime.timestamp() + 300
                else:
                    global search_expired
                    if Datetime.timestamp() < search_expired:
                        reply = ArticlesReply()
                        reply.source = appid
                        reply.target = from_user_openid
                        reply.add_article({
                            'title': '用户信息',
                            'description': '用户详情',
                            'image': 'http://thirdwx.qlogo.cn/mmopen/vi_32/qfAic3BUiaj7Ynsdm8TgQayw0nibpC0Xll7LPehtJmadbdCLk8GPBKTG0szw2qfU0CAUf5x9mXTE0Eib0h3aXpzZxw/132',
                            'url': 'https://www.baidu.com'
                        })
                        xml = reply.render()
                        return HttpResponse(content=xml, content_type='text/xml')
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
            log.e(traceback.format_exc())
            sentry_sdk.capture_exception(exc)
            return Response('success')
