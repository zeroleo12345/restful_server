from trade.framework.exception import GlobalException


class Authentication(object):
    def __init__(self, request):
        """
        {
            'weixin': {
                'id': 1,
                'openid': 'o0FSR0Zh3rotbOog_b2lytxzKrYo', 'nickname': 'nickname_0',
                'headimgurl': 'http://www.headimgurl.com/0', 'created_at': '2020-01-29T22:13:10.854786+08:00'
            },
            'username': 'username_0',
            'password': 'password_0',
            'is_enable': True,
            'role': 'vip'
        }
        """
        self.role = str(request.user.get('role', ''))
        self.is_enable = str(request.user.get('is_enable', ''))
        self.user_id = str(request.user.get('id', ''))
        if not self.user_id:
            raise GlobalException({'code': 'invalid_authorization', 'message': 'authorization缺失user_id'}, status=400)
