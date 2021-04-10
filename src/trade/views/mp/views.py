import datetime
# 第三方库
import sentry_sdk
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from wechatpy.events import SubscribeScanEvent, ScanEvent, SubscribeEvent, ClickEvent
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply, ArticlesReply
# 项目库
from utils.myrandom import MyRandom
from utils.time import Datetime
import settings
from settings import log
from trade.models import Platform, User, Account
from trade.controls.platform import create_new_platform
from service.wechat.we_client import WeClient
from service.wechat.we_crypto import WeCrypto
from framework.database import get_redis


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
        if not WeCrypto.is_right_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            raise Exception('mp platform invalid signature')
        return Response(echostr)

    def post(self, request):
        """
        公众号平台事件通知. (PS: 使用平台自带的自定义菜单时, 平台不会下发消息)
        加密模式下 request.GET:
            {
                'signature': '3b6995754f8910fb784c1a060b17750f67b440a9',
                'timestamp': '1612607821',
                'nonce': '1404486768',
                'openid': 'o0FSR0Zh3rotbOog_b2lytxzKrYo',
                'encrypt_type': 'aes',
                'msg_signature': 'e36e86d1c88014e4dc1ced8323bff7ba006e0b0d'
            }
        明文模式下 request.GET:
            {
                'signature': '8d2e34ffd739d7ae39532f91ce41a48674ee323f',
                'timestamp': '1612608294',
                'nonce': '836218769',
                'openid': 'o0FSR0Zh3rotbOog_b2lytxzKrYo'
            }
        """
        xml = request.body
        msg_signature = request.GET.get('msg_signature', None)
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        msg = WeCrypto.decrypt_and_parse_message(xml=xml, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
        log.i(f'wechat event: {msg}, url params: {request.GET}')
        appid = msg.target     # 例如: gh_9225266caeb1
        from_user_openid = msg.source

        def get_reply_msg():
            # 被动回复 https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
            if isinstance(msg, SubscribeScanEvent) or isinstance(msg, ScanEvent):
                # 未关注用户扫描带参数二维码事件 - 订阅关注
                # 已关注用户扫描带参数二维码事件
                platform_id = int(msg.scene_id)
                platform = Platform.get(platform_id=platform_id)
                assert platform
                user = User.get(openid=from_user_openid)
                if not user:
                    # 创建 user
                    user = User.create(openid=from_user_openid, bind_platform_id=platform.platform_id)
                else:
                    # user 表记录, 存在
                    if user.bind_platform_id != platform.platform_id:
                        log.w(f'platform_id change: {user.bind_platform_id} -> {platform.platform_id}, openid: {user.openid}')
                        user.update(bind_platform_id=platform.platform_id)
                account = Account.get(user_id=user.user_id, platform_id=user.bind_platform_id)
                if not account:
                    # 创建 account
                    username = MyRandom.random_digit(length=8)
                    expired_at = Datetime.localtime() + datetime.timedelta(days=1)  # 新账户一天内免费
                    account = Account.create(
                        user_id=user.user_id,
                        platform_id=user.bind_platform_id,
                        username=username,
                        password=username,
                        radius_password=username,
                        role=Account.Role.PAY_USER.value,
                        expired_at=expired_at,
                    )
                sentry_sdk.capture_message(f'有用户扫描带参数二维码, platform_id: {platform.platform_id}, openid: {from_user_openid}')
                # 判断是否允许房东注册
                if platform.platform_id == settings.ADMIN_PLATFORM_ID:
                    redis = get_redis()
                    if redis.get('enable_platform_register'):
                        # 新创建平台
                        new_platform = create_new_platform(user_id=user.user_id)
                        platform_url = f'{settings.API_SERVER_URL}/platform/{new_platform.platform_id}'
                        sentry_sdk.capture_message(f'房东平台已建立, platform_url: {platform_url}')
                        redis.delete('enable_platform_register')
                # 应答
                return TextReply(source=appid, target=from_user_openid, content=f'账号: {account.username}\n密码: {account.password}\n状态: {account.status}')

            if isinstance(msg, ClickEvent):
                # 点击按钮 - 账号中心
                if msg.key == WeClient.ACCOUNT_VIEW_BTN_EVENT:
                    user = User.get(openid=from_user_openid)
                    if not user or user.bind_platform_id is None:
                        # 用户未经扫码, 进入公众号
                        return TextReply(source=appid, target=from_user_openid, content=f'请先扫描房东的WIFI二维码')
                    else:
                        platform = Platform.get(platform_id=user.bind_platform_id)
                        if platform.is_platform_owner(user_id=user.user_id) and not settings.is_admin(openid=from_user_openid):
                            # 房东不能打开充值页面, 但 admin 可以
                            return TextReply(source=appid, target=from_user_openid, content=f'房东不允许打开充值页面')
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
                        'id',
                        '搜索 $name',
                        'free',
                        '放通mac',
                        '房东注册',
                    ]
                    message = '命令:\n  ' + '\n  '.join(command)
                    return TextReply(source=appid, target=from_user_openid, content=message)

                elif msg.content == 'id':
                    # 查看用户ID
                    user = User.get(openid=from_user_openid)
                    messages = [
                        f'你的信息:',
                        f'openid: {user.openid}',
                        f'user_id: {user.user_id}',
                    ]
                    return TextReply(source=appid, target=from_user_openid, content='\n'.join(messages))

                # 以下命令需要 admin 权限
                elif msg.content.startswith('搜索') and settings.is_admin(openid=from_user_openid):
                    # 搜索用户信息
                    name = msg.content.split('搜索')[1].strip()
                    return TextReply(source=appid, target=from_user_openid, content=f'{settings.API_SERVER_URL}/search/user?name={name}')

                elif msg.content.startswith('放通mac') and settings.is_admin(openid=from_user_openid):
                    redis = get_redis()
                    ex = 60 * 5
                    redis.set('enable_mac_authentication', str(datetime.datetime.now()), ex=ex)
                    return TextReply(source=appid, target=from_user_openid, content=f'有效时间: {ex}秒')

                elif msg.content.startswith('房东注册') and settings.is_admin(openid=from_user_openid):
                    redis = get_redis()
                    ex = 60 * 5
                    redis.set('enable_platform_register', str(datetime.datetime.now()), ex=ex)
                    return TextReply(source=appid, target=from_user_openid, content=f'有效时间: {ex}秒')

                elif msg.content.startswith('free') and settings.is_admin(openid=from_user_openid):
                    expired_at = Datetime.localtime() + datetime.timedelta(minutes=30)
                    account = Account.get(user_id=0, platform_id=0)
                    if not account:
                        account = Account.create(
                            user_id=0,
                            platform_id=0,
                            username='free',
                            password='free',
                            radius_password='free',
                            role=Account.Role.FREE_USER.value,
                            expired_at=expired_at,
                        )
                    else:
                        account.update(expired_at=expired_at)
                    content = f'用户名: {account.username}, 密码: {account.password}, 失效时间: {Datetime.to_str(expired_at, fmt="%Y-%m-%d %H:%M:%S")}'
                    return TextReply(source=appid, target=from_user_openid, content=content)

                else:
                    return TextReply(source=appid, target=from_user_openid, content=settings.MP_DEFAULT_REPLY)
            return None
        #
        reply = get_reply_msg()
        if reply:
            xml = reply.render()
            xml = WeCrypto.encrypt_message(xml=xml, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
            return HttpResponse(content=xml, content_type='text/xml')
        else:
            return Response('success')
