import pytest
#
from service.wechat_enterprise.we_user import WeUser


def usage():
    print("""
测试方法:
    from service.wechat_enterprise.tests.test_user import *; a = Test()
    
    user_id = 'ZhouLiXin'
    a.test_send_template(user_id=user_id)
    """)


@pytest.mark.django_db
class Test(object):

    @pytest.mark.skip(reason='')
    def test_send_template(self, user_id: str):
        # {'errcode': 0, 'errmsg': 'ok', 'openid': 'oV4Up1vv8-PqS4uR6SsyAFJ-N9ds'}
        return WeUser.convert_to_openid(user_id=user_id)
