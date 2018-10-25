import pytest
from urllib.parse import urljoin
# 第三方库
from django.conf import settings
from rest_framework import status
# 自己的库
from trade.utils.wepay import WePay
from trade.framework.unittest import get_user_and_token


@pytest.mark.skip(reason="手动触发测试, 因为只有一个微信号")
def test_wepay_cashier():
    user, jwt_token = get_user_and_token()
    openid = user.weixin.openid
    total_fee = 1               # 单位分
    title = '用户支付提示'
    client_ip = '127.0.0.1'
    attach = None
    notify_url = urljoin(settings.MP_WEB_URL, 'pay_success_callback')
    order_params, wepay_params = WePay.Cashier(
        openid=openid, total_fee=total_fee, title=title, client_ip=client_ip, attach=attach, notify_url=notify_url
    )
    assert 'appId' in wepay_params
    assert 'nonceStr' in wepay_params
    assert 'package' in wepay_params
    assert 'paySign' in wepay_params
    assert 'signType' in wepay_params
    assert 'timeStamp' in wepay_params
