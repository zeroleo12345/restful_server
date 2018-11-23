# coding:utf-8
# 开发文档地址:    https://docs.sentry.io/error-reporting/quickstart/?platform=python

from decouple import config

import sentry_sdk

SENTRY_DSN = config('SENTRY_DSN')
sentry_sdk.init(SENTRY_DSN)

# 上报异常
try:
    a = 1 / 0
except Exception as e:
    # Alternatively the argument can be omitted
    sentry_sdk.capture_exception(e)

# 上报信息
sentry_sdk.capture_message('Sentry Hello World')
