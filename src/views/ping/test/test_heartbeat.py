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

    def test_ping_get(self):
        client = UnitTestAPIClient()
        response = client.get('/ping')
        assert response.status_code == status.HTTP_200_OK
