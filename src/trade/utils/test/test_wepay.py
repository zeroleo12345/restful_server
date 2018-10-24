import pytest
from urllib.parse import urljoin
# 第三方库
from django.conf import settings
from rest_framework import status
# 自己的库
from trade.utils.wepay import WePay


def test_wepay_cashier():
    openid = 'o0FSR0Zh3rotbOog_b2lytxzKrYo'     # zeroleo12345 在畅玩竹仔园下的openid
    total_fee = 1               # 单位分
    title = '用户支付提示'
    client_ip = '127.0.0.1'
    attach = None
    notify_url = urljoin(settings.MP_WEB_URL, 'pay_success_callback')
    response = WePay.Cashier(
        openid=openid, total_fee=total_fee, title=title, client_ip=client_ip, attach=attach, notify_url=notify_url
    )
    assert 'appId' in response
    assert 'nonceStr' in response
    assert 'package' in response
    assert 'paySign' in response
    assert 'signType' in response
    assert 'timeStamp' in response

