from wechatpy.client.api import WeChatMessage
from datetime import datetime
#
from service.wechat.we_client import WeClient
from utils.time import Datetime
from trade import settings

we_message = WeChatMessage(client=WeClient.we_client)


class WePush(object):
    MP_ACCOUNT_EXPIRE_TEMPLATE_ID = settings.MP_ACCOUNT_EXPIRE_TEMPLATE_ID
    MP_ORDER_PAID_TEMPLATE_ID = settings.MP_ORDER_PAID_TEMPLATE_ID

    @classmethod
    def notify_account_expire(cls, openid: str, username: str, expired_at: datetime, mini_program=None):
        """
        您好，您的宽带即将到期       {{first.DATA}}
        帐号：123456789            帐号：{{keyword1.DATA}}
        类型：即将到期              类型：{{keyword2.DATA}}
        请尽快处理                  {{remark.DATA}}
        """
        data = {
            'first': {'value': '您的宽带即将到期'},
            'keyword1': {'value': username},
            'keyword2': {'value': f'到期时间 {Datetime.to_str(expired_at, fmt="%Y-%m-%d %H:%M")}'},
            'remark': {'value': '如需继续使用, 请点击充值'}
        }
        we_message.send_template(openid, cls.MP_ACCOUNT_EXPIRE_TEMPLATE_ID, data, url=WeClient.ACCOUNT_VIEW_URI, mini_program=mini_program)

    @classmethod
    def notify_owner_order_paid(cls, platform_id: int, openid: str, total_fee: int, nickname: str, paid_at: datetime, trade_no: str, mini_program=None):
        """
        您有一笔新订单，请及时处理。               {first.DATA}}
        商品：眼镜X1                             商品：{{keyword1.DATA}}
        金额：100元                              金额：{{keyword2.DATA}}
        购买人昵称：飘                            购买人昵称：{{keyword3.DATA}}
        交易时间：2014年7月21日 18:36             交易时间：{{keyword4.DATA}}
        交易流水号：2132132432432432             交易流水号：{{keyword5.DATA}}
        点击查看详情                             {{remark.DATA}}
        """
        data = {
            'first': {'value': f'房东-{platform_id}, 您有一笔收入'},
            'keyword1': {'value': '租户宽带充值'},
            'keyword2': {'value': f'{total_fee / 100}元'},
            'keyword3': {'value': nickname},
            'keyword4': {'value': f'{Datetime.to_str(paid_at, fmt="%Y-%m-%d %H:%M")}'},
            'keyword5': {'value': trade_no},
            'remark': {'value': ''}
        }
        we_message.send_template(openid, cls.MP_ORDER_PAID_TEMPLATE_ID, data, url=None, mini_program=mini_program)
        if platform_id != settings.ADMIN_PLATFORM_ID:
            data = {
                'first': {'value': f'您有一笔分成: 平台-{platform_id}'},
                'keyword1': {'value': '平台租户宽带充值'},
                'keyword2': {'value': f'{total_fee / 100}元'},
                'keyword3': {'value': nickname},
                'keyword4': {'value': f'{Datetime.to_str(paid_at, fmt="%Y-%m-%d %H:%M")}'},
                'keyword5': {'value': trade_no},
                'remark': {'value': ''}
            }
            we_message.send_template(settings.MP_ADMIN_OPENID, cls.MP_ORDER_PAID_TEMPLATE_ID, data, url=None, mini_program=mini_program)
