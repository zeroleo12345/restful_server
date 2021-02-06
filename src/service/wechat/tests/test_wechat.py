import pytest
#
from service.wechat.we_client import WeClient
from service.wechat.we_message import we_message


def usage():
    print("""
测试方法:
    from service.wechat.tests.test_wechat import *; a = Test()
    
    openid = 'o0FSR0Zh3rotbOog_b2lytxzKrYo'
    template_id = 'nJd-Uw5WlA9DBDqYPTSmpwhysbE269qMP5Adx-dbyyU'
    
    data = {'first': {'value': '您的宽带即将到期', 'color': '#173177'}, 'keyword1': {'value': '账号'}, 'keyword2': {'value': '到期时间 2020-01-01 08:00'}, 'remark': {'value': '如需继续使用, 请点击充值'}}
    a.test_send_template(openid, template_id, data, url=WeClient.ACCOUNT_VIEW_URI)
    """)


@pytest.mark.django_db
class Test(object):

    @pytest.mark.skip(reason='')
    def test_send_template(self, openid, template_id, data, url=None, mini_program=None):
        we_message.send_template(openid, template_id, data, url=url, mini_program=mini_program)
