import pytest
# 第三方库
from rest_framework import status
# 项目库
from framework.unittest import UnitTestAPIClient
from models.factories.user import UserFactory


@pytest.mark.skip(reason="手动触发测试")
def test_order_create():
    client = UnitTestAPIClient()
    user, authorization = UserFactory.new_user_and_authorization(client)
    client = UnitTestAPIClient(authorization=authorization)
    data = {
        'tariff_name': 'month1',
    }
    response = client.post('/order', data=data)
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response['code'] == 'ok'

    jsapi_params = json_response['data']
    assert 'appId' in jsapi_params
    assert 'nonceStr' in jsapi_params
    assert 'package' in jsapi_params
    assert 'paySign' in jsapi_params
    assert 'signType' in jsapi_params
    assert 'timeStamp' in jsapi_params
