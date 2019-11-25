import json
#
from django_redis import get_redis_connection


class WechatCode(object):
    @classmethod
    def key(cls, oauth_code: str):
        return f'wechat_code:{oauth_code}'

    @classmethod
    def set(cls, oauth_code, openid: str, nickname: str, avatar: str):
        redis = get_redis_connection()
        key = cls.key(oauth_code)
        value = json.dumps({
            'openid': openid,
            'nickname': nickname,
            'avatar': avatar,
        })
        redis.set(key, value, ex=86400)

    @classmethod
    def get(cls, oauth_code):
        redis = get_redis_connection()
        key = cls.key(oauth_code)
        value = redis.get(key)
        if not value:
            return None, None, None
        user_info = json.loads(value)
        openid = user_info['openid']
        nickname = user_info['nickname']
        avatar = user_info['avatar']
        return openid, nickname, avatar

