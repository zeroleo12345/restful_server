from trade import settings
# 第三方库
from django_redis import get_redis_connection
from wechatpy.session.redisstorage import RedisStorage
from wechatpy.enterprise import WeChatClient
from wechatpy.enterprise.client.api import WeChatUser
# 自己的库

redis_client = get_redis_connection(alias='default')
contact_client = WeChatClient(
    corp_id=settings.ENTERPRISE_CORP_ID, secret=settings.ENTERPRISE_CONTACT_SECRET, session=RedisStorage(redis_client, prefix='wechat_enterprise')
)


class WeUser(object):
    we_user = WeChatUser(client=contact_client)

    @classmethod
    def convert_to_openid(cls, user_id: str):
        return cls.we_user.convert_to_openid(user_id=user_id)