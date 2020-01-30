from rest_framework.test import APIClient
#
from framework.authorization import JWTAuthentication


class UnitTestAPIClient(APIClient):
    """
    workaround:
        https://github.com/encode/django-rest-framework/blob/master/tests/test_api_client.py
        https://www.django-rest-framework.org/api-guide/testing/

    Client 设置头部:
        client.defaults['HTTP_X_FORWARDED_FOR'] = '127.0.0.1'
    """

    def __init__(self, authorization=None):
        http_authorization = 'HTTP_AUTHORIZATION'
        authorization = str(authorization) if authorization else None

        super().__init__(**{
            http_authorization: authorization
        })
        self.user = JWTAuthentication.jwt_decode_handler(jwt_token=authorization)['user'] if authorization else {}

    def post(self, path, data=None, format='json', *args, **kwargs):
        # client.post(f'/debug', data='', format=None, content_type='application/xml')
        # client.post(f'/debug', data={}, format='json')
        # client.post(f'/debug', data=urlencode(data), format=None, content_type='application/x-www-form-urlencoded; charset=UTF-8')
        """
        :param path:
        :param data:
        :param format:
             json - request.data.get
             None - request.POST.get
        :return:
        """
        return super().post(path, data, format=format, *args, **kwargs)

    def put(self, path, data=None, format='json', *args, **kwargs):
        return super().put(path, data, format=format, *args, **kwargs)

    def patch(self, path, data=None, format='json', *args, **kwargs):
        return super().patch(path, data, format=format, *args, **kwargs)
