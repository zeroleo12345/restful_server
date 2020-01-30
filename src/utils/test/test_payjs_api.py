import pytest
from urllib.parse import urljoin
# 第三方库
from django.conf import settings
from rest_framework import status
# 项目库
from utils.payjs import Payjs


@pytest.mark.skip(reason="手动触发测试, 因为需要消耗豆豆")
def test_payjs_post():
    callback_url = urljoin(settings.MP_WEB_URL, 'pay_success_callback')
    url, param = Payjs.cashier(total_fee=100, title='用户支付提示', callback_url=callback_url)
    response = Payjs._post(Payjs.CASHIER_URL, data=param)
    assert response.status_code == status.HTTP_200_OK
    assert "<!DOCTYPE html>\n<html>\n    <head>\n" in response.text
    assert "请在微信客户端打开链接" in response.text
    assert "</script>\n    </body>\n</html>\n" in response.text


@pytest.mark.skip(reason="手动触发测试, 因为需要消耗豆豆")
def test_payjs_get():
    callback_url = urljoin(settings.MP_WEB_URL, 'pay_success_callback')
    url, param = Payjs.cashier(total_fee=100, title='用户支付提示', callback_url=callback_url)
    response = Payjs._get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "<!DOCTYPE html>\n<html>\n    <head>\n" in response.text
    assert "请在微信客户端打开链接" in response.text
    assert "</script>\n    </body>\n</html>\n" in response.text
