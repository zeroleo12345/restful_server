import pytest
# 第三方库
from django.conf import settings
# 项目库
from utils.wepay import WePay
from models.factories.user import UserFactory
from framework.unittest import UnitTestAPIClient
from framework.field import new_uuid


@pytest.mark.skip(reason="手动触发测试, 因为只有一个微信号")
def test_wepay_jsapi():
    client = UnitTestAPIClient()
    user, authorization = UserFactory.new_user_and_authorization(client)
    openid = user.weixin.openid
    total_fee = 1               # 单位分
    title = '用户支付提示'
    client_ip = '127.0.0.1'
    attach = None
    jsapi_params = WePay.create_jsapi_order(
        out_trade_no=new_uuid(),
        openid=openid, total_fee=total_fee, title=title, client_ip=client_ip, attach=attach, notify_url=settings.MP_PAY_NOTIFY_URL
    )
    assert 'appId' in jsapi_params
    assert 'nonceStr' in jsapi_params
    assert 'package' in jsapi_params
    assert 'paySign' in jsapi_params
    assert 'signType' in jsapi_params
    assert 'timeStamp' in jsapi_params
