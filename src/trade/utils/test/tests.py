from urllib.parse import urljoin
# 第三方库
from django.conf import settings
from rest_framework import status
# 自己的库
from trade.utils.payjs import Payjs


def test_payjs():
    callback_url = urljoin(settings.MP_WEB_URL, 'pay_success_callback')
    response = Payjs.Cashier(total_fee=100, body='用户支付提示', callback_url=callback_url)
    assert response.status_code == status.HTTP_200_OK
    assert "<!DOCTYPE html>\n<html>\n    <head>\n" in response.text
    assert "请在微信客户端打开链接" in response.text
    assert "</script>\n    </body>\n</html>\n" in response.text
