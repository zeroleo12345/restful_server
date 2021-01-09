import traceback
# 第三方库
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from wechatpy.utils import check_signature
from wechatpy.events import SubscribeScanEvent, ScanEvent, SubscribeEvent
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply
from wechatpy import parse_message
# 项目库
from trade import settings
from trade.settings import log
from models import Platform, User
from service.wechat.we_client import WeClient


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
        #
        reply = None
        # 未关注用户扫描带参数二维码事件 - 订阅关注
        # 已关注用户扫描带参数二维码事件
        if isinstance(msg, SubscribeScanEvent) or isinstance(msg, ScanEvent):
            response_text = '关注成功，后续会通过公众号给你推送自动接单和通知任务的结果。'
            platform_id = int(msg.scene_id)
            platform = Platform.get(id=platform_id)
            assert platform
            user = User.get(openid=from_user_openid)
            if user:
                # user 表记录, 存在
                if user.bind_platform_id != platform.id:
                    log.i(f'platform_id change: {user.bind_platform_id} -> {platform.id}, openid: {user.openid}')
                    user.update(platform_id=platform.id)
            else:
                # user 表记录, 不存在
                user.create(openid=from_user_openid, platform_id=platform.id)
            reply = TextReply(source=appid, target=from_user_openid, content=response_text)

        elif isinstance(msg, SubscribeEvent):   # 关注公众号事件
            reply = TextReply(source=appid, target=from_user_openid, content=settings.MP_DEFAULT_REPLY)

        elif isinstance(msg, TextMessage):    # 文本消息
            if msg.content in ['help', '帮助', '命令']:
                command = [
                    'openid',
                    '搜索 $name',
                    '二维码 $user_id'
                ]
                message = '命令:\n  ' + '\n  '.join(command)
                reply = TextReply(source=appid, target=from_user_openid, content=message)

            elif msg.content == 'openid':
                user = User.get(openid=from_user_openid)
                messages = [
                    f'你的信息:',
                    f'openid: {user.openid}'
                    f'user_id: {user.id}'
                ]
                reply = TextReply(source=appid, target=from_user_openid, content='\n'.join(messages))

            elif msg.content.startswith('搜索') and from_user_openid == settings.MP_ADMIN_OPENID:
                name = msg.content.split('搜索')[1].strip()
                reply = TextReply(source=appid, target=from_user_openid, content=f'{settings.API_SERVER_URL}/search?name={name}')
                # reply = ArticlesReply(source=appid, target=from_user_openid)
                # reply.add_article({
                #     'title': f'搜索词: "{name}"',
                #     'description': '搜不到用户',
                #     'image': image_url,
                #     'url': f'{settings.API_SERVER_URL}/search?name=name'
                # })

            elif msg.content.startswith('二维码') and from_user_openid == settings.MP_ADMIN_OPENID:
                user_id = msg.content.split('二维码')[1].strip()
                user = User.get(id=user_id)
                if not user:
                    reply = TextReply(source=appid, target=from_user_openid, content=f'用户不存在')
                else:
                    platform = Platform.create(owner_user_id=user.id)
                    log.i(f'create qrcode, platform_id: {platform.id}')
                    qrcode_info = WeClient.create_qrcode(scene_str=platform.id, is_permanent=True)
                    qrcode_url = qrcode_info['url']
                    platform.update(qrcode_url=qrcode_url)
                    reply = TextReply(source=appid, target=from_user_openid, content=f'user_id: {user.id}, qrcode_url: {platform.qrcode_url}')

            else:
                reply = TextReply(source=appid, target=from_user_openid, content=settings.MP_DEFAULT_REPLY)
        if reply:
            xml = reply.render()
            return HttpResponse(content=xml, content_type='text/xml')
        else:
            return Response('success')
