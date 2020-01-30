# 第三方库
from rest_framework import status
import pytest
# 自己的库
from trade.framework.unittest import UnitTestAPIClient


@pytest.mark.django_db
class TestDebug:

    @pytest.fixture(autouse=True)
    def setup_stuff(self, db):
        pass

    def test_debug_get(self):
        client = UnitTestAPIClient()
        response = client.get('/debug')
        assert response.status_code == status.HTTP_200_OK

        res_dict = response.json()
        assert 'ok' == res_dict['code']

    def test_debug_post(self):
        client = UnitTestAPIClient()
        response = client.post('/debug')
        assert response.status_code == status.HTTP_200_OK

        res_dict = response.json()
        assert 'ok' == res_dict['code']
