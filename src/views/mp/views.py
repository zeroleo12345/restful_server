import traceback
# 第三方库
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from wechatpy.utils import check_signature
from wechatpy.events import SubscribeScanEvent, ScanEvent, SubscribeEvent
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply, ArticlesReply
from wechatpy import parse_message
# 项目库
from trade import settings
from trade.settings import log
from models import User, Platform, Weixin


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
        xml = request.body
        msg = parse_message(xml)
        log.i(f'wechat event: {msg}')
        appid = msg.target     # 例如: gh_9225266caeb1
        from_user_openid = msg.source

        # 未关注用户扫描带参数二维码事件 - 订阅关注
        # 已关注用户扫描带参数二维码事件
        if isinstance(msg, SubscribeScanEvent) or isinstance(msg, ScanEvent):
            response_text = '关注成功，后续会通过公众号给你推送自动接单和通知任务的结果。'
            platform_id = msg.scene_id
            platform = Platform.get(id=platform_id)
            assert platform
            weixin = Weixin.get(openid=from_user_openid)
            if weixin:
                # weixin 表记录, 存在
                weixin.update(platform_id=platform_id)
            else:
                # weixin 表记录, 不存在
                weixin.create(openid=from_user_openid, platform_id=platform_id)
            reply = TextReply()
            reply.source = appid
            reply.target = from_user_openid
            reply.content = response_text
            xml = reply.render()
            return HttpResponse(content=xml, content_type='text/xml')

        elif isinstance(msg, SubscribeEvent):   # 关注公众号事件
            reply = TextReply()
            reply.source = appid
            reply.target = from_user_openid
            reply.content = settings.MP_DEFAULT_REPLY
            xml = reply.render()
            return HttpResponse(xml, content_type='text/xml')

        elif isinstance(msg, TextMessage):    # 文本消息
            if msg.content in ['help', '帮助', '命令']:
                command = ['openid', '搜索']
                message = '命令: ' + ', '.join(command)
            elif msg.content == 'openid':
                message = f'你的openid: {from_user_openid}'
            elif msg.content.startswith('搜索'):
                word = msg.content.split('搜索')[1].strip()
                description, image = '', ''
                for user in User.search(nickname__contains=word):
                    description += f'昵称: "{user.nickname}"\n过期时间: {user.expired_at}'
                    image = user.headimgurl
                reply = ArticlesReply()
                reply.source = appid
                reply.target = from_user_openid
                reply.add_article({
                    'title': f'搜索词: "{word}"',
                    'description': description or '搜不到用户',
                    'image': image,
                    'url': f'{settings.API_SERVER_URL}/user/sync'
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

        return Response('success')
