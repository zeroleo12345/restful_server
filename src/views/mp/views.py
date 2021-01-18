import traceback
# 第三方库
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from wechatpy.utils import check_signature
from wechatpy.events import SubscribeScanEvent, ScanEvent, SubscribeEvent, ClickEvent
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply, ArticlesReply
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

        def get_reply_msg():
            # 被动回复 https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
            # 未关注用户扫描带参数二维码事件 - 订阅关注
            # 已关注用户扫描带参数二维码事件
            if isinstance(msg, SubscribeScanEvent) or isinstance(msg, ScanEvent):
                platform_id = int(msg.scene_id)
                platform = Platform.get(platform_id=platform_id)
                assert platform
                user = User.get(openid=from_user_openid)
                if not user:
                    # user 表记录, 不存在
                    User.create(openid=from_user_openid, bind_platform_id=platform.platform_id)
                else:
                    # user 表记录, 存在
                    if user.bind_platform_id != platform.platform_id:
                        log.w(f'platform_id change: {user.bind_platform_id} -> {platform.platform_id}, openid: {user.openid}')
                        user.update(bind_platform_id=platform.platform_id)
                r = ArticlesReply(source=appid, target=from_user_openid)
                r.add_article({
                    'title': f'点击进入',
                    'description': '查询WIFI密码 / WIFI续费',
                    'image': 'http://zlxpic.lynatgz.cn/zhuzaiyuan_mini.jpg',
                    'url': WeClient.ACCOUNT_VIEW_URI,
                })
                return r

            if isinstance(msg, ClickEvent):
                if msg.key == WeClient.ACCOUNT_VIEW_BTN_EVENT:
                    user = User.get(openid=from_user_openid)
                    if not user or user.bind_platform_id is None:
                        # 用户未经扫码, 进入公众号
                        return TextReply(source=appid, target=from_user_openid, content=f'请先扫描房东的WIFI二维码')
                    else:
                        r = ArticlesReply(source=appid, target=from_user_openid)
                        r.add_article({
                            'title': f'点击进入',
                            'description': '查询WIFI密码 / WIFI续费',
                            'image': 'http://zlxpic.lynatgz.cn/zhuzaiyuan_mini.jpg',
                            'url': WeClient.ACCOUNT_VIEW_URI,
                        })
                        return r
                elif msg.key == WeClient.CUSTOMER_SERVICE_BTN_EVENT:
                    return TextReply(source=appid, target=from_user_openid, content=settings.MP_DEFAULT_REPLY)

            elif isinstance(msg, SubscribeEvent):   # 关注公众号事件
                pass

            elif isinstance(msg, TextMessage):    # 文本消息
                if msg.content in ['help', '帮助', '命令']:
                    command = [
                        'openid',
                        '搜索 $name',
                        '二维码 $user_id'
                    ]
                    message = '命令:\n  ' + '\n  '.join(command)
                    return TextReply(source=appid, target=from_user_openid, content=message)

                elif msg.content == 'openid':
                    user = User.get(openid=from_user_openid)
                    messages = [
                        f'你的信息:',
                        f'openid: {user.openid}'
                        f'user_id: {user.user_id}'
                    ]
                    return TextReply(source=appid, target=from_user_openid, content='\n'.join(messages))

                elif msg.content.startswith('搜索') and from_user_openid == settings.MP_ADMIN_OPENID:
                    name = msg.content.split('搜索')[1].strip()
                    return TextReply(source=appid, target=from_user_openid, content=f'{settings.API_SERVER_URL}/search/user?name={name}')

                elif msg.content.startswith('二维码') and from_user_openid == settings.MP_ADMIN_OPENID:
                    user_id = msg.content.split('二维码')[1].strip()
                    user = User.get(user_id=user_id)
                    if not user:
                        return TextReply(source=appid, target=from_user_openid, content=f'用户不存在')
                    else:
                        platform = Platform.create(owner_user_id=user.user_id)
                        qrcode_info = WeClient.create_qrcode(scene_str=str(platform.platform_id), is_permanent=True)
                        log.d(f'qrcode_info: {qrcode_info}')
                        qrcode_content = qrcode_info['url']
                        log.i(f'create qrcode, platform_id: {platform.platform_id}, qrcode_content: {qrcode_content}')
                        platform.update(qrcode_content=qrcode_content)
                        return TextReply(source=appid, target=from_user_openid, content=f'user_id: {user.user_id}, qrcode_content: {platform.qrcode_content}')

                else:
                    return TextReply(source=appid, target=from_user_openid, content=settings.MP_DEFAULT_REPLY)
            return None
        #
        reply = get_reply_msg()
        if reply:
            xml = reply.render()
            return HttpResponse(content=xml, content_type='text/xml')
        else:
            return Response('success')
