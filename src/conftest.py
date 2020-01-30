import pytest
# from unittest import mock


# 全局mock
# @pytest.fixture(scope='session', autouse=True)
# def default_session_fixture(request):
#     patched1 = mock.patch('bihu.utils.kafka.producer.send_json')
#     patched1.__enter__()
#
#     def unpatch():
#         patched1.__exit__()
#     request.addfinalizer(unpatch)


# @pytest.fixture
@pytest.fixture(scope='module', autouse=True)
def db_no_rollback(request, django_db_setup, django_db_blocker):
    django_db_blocker.unblock()
    request.addfinalizer(django_db_blocker.restore)


# 全局clean_up
@pytest.fixture(scope='session', autouse=True)
def default_function_fixture(request):
    # before
    from django_redis import get_redis_connection
    get_redis_connection('default').flushall()
    #
    yield
    # after
    pass


# https://docs.pytest.org/en/latest/example/simple.html#detect-if-running-from-within-a-pytest-run
def pytest_configure(config):
    import sys
    sys._called_from_test = True


def pytest_unconfigure(config):
    import sys
    del sys._called_from_test
