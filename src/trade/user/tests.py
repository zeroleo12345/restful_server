import pytest
from unittest.mock import MagicMock
from rest_framework import status
from trade.framework.tests import get_token_and_user, UnitTestAPIClient
from trade.utils import mp

mp.create_mp_menu = MagicMock()


@pytest.mark.django_db
def test_user():
    token, user = get_token_and_user()
    client = UnitTestAPIClient(token=token)
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
