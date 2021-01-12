import pytest
#
from service.wechat.we_client import WeClient
from service.wechat.we_message import we_message


def usage():
    print("""
测试方法:
    from service.wechat.tests.test_wechat import *; a = Test()
    
    openid = 'o0FSR0Zh3rotbOog_b2lytxzKrYo'
    template_id = 'SUx74ExnoOoiESmA-K-pDrHa6qhYce99upCTKGX2Lgk'
    
    data = {'first': {'value': '您的宽带即将到期', 'color': '#173177'}, 'keyword1': {'value': '账号'}, 'keyword2': {'value': '2020-01-01 08:00'}, 'remark': {'value': '如需继续使用, 请点击充值'}}
    a.test_send_template(openid, template_id, data, url=WeClient.recharge_uri)
    """)


@pytest.mark.django_db
class Test(object):

    @pytest.mark.skip(reason='公众号推送模板')
    def test_send_template(self, openid, template_id, data, url=None, mini_program=None):
        we_message.send_template(openid, template_id, data, url=url, mini_program=mini_program)
