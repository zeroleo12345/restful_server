# coding:utf-8
# 开发文档地址:    https://docs.sentry.io/error-reporting/quickstart/?platform=python

from decouple import config

import sentry_sdk
from sentry_sdk import capture_exception

SENTRY_DSN = config('SENTRY_DSN')
sentry_sdk.init(SENTRY_DSN)

# 上报异常
try:
    a = 1 / 0
except Exception as e:
    # Alternatively the argument can be omitted
    capture_exception(e)

# 上报信息
from sentry_sdk import capture_message
capture_message('Sentry Hello World')
