# 第三方库
from rest_framework import status
import pytest
# 项目库
from framework.unittest import UnitTestAPIClient


@pytest.mark.django_db
class TestDebug:

    @pytest.fixture(autouse=True)
    def setup_stuff(self, db):
        pass

    def test_heartbeat_get(self):
        client = UnitTestAPIClient()
        response = client.get('/heartbeat')
        assert response.status_code == status.HTTP_200_OK

        res_dict = response.json()
        assert 'ok' == res_dict['code']
