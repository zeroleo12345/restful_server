"""
Django settings for trade project.

Generated by 'django-admin startproject' using Django 1.11.12.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import datetime
# 第三方库
from decouple import config
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
# 自己的库
from mybase3.mylog3 import log

LOG_HEADER = config('LOG_HEADER', default='restful')
LOG_DIR = config('LOG_DIR', default='../run/log')
LOG_LEVEL = config('LOG_LEVEL', default='debug')
log.init(header=LOG_HEADER, directory=LOG_DIR, level=LOG_LEVEL, max_buffer=0, max_line=100000)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['*']


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'trade',
]

MIDDLEWARE = [
    'trade.framework.middleware.CORSMiddleware',    # TODO 使用开源的: 'corsheaders.middleware.CorsMiddleware'
    'trade.framework.middleware.TokenSetMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

# if DEBUG:
#     MIDDLEWARE += [
#         'django.contrib.sessions.middleware.SessionMiddleware',
#         'django.middleware.csrf.CsrfViewMiddleware',
#         'django.contrib.auth.middleware.AuthenticationMiddleware',
#         'django.contrib.messages.middleware.MessageMiddleware',
#         'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     ]

ROOT_URLCONF = 'trade.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trade.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASE_ROUTERS = ['trade.framework.db_route.Router']
DATABASES = {
    'default': {
        **dj_database_url.parse(config("DATABASE_URI")),
        **{'TIME_ZONE': TIME_ZONE}
    },
}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config('REDIS_URI'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 'DEFAULT_AUTHENTICATION_CLASSES': (
#     'rest_framework.authentication.SessionAuthentication',
#     'rest_framework.authentication.BasicAuthentication'
# )
# # Use Django's standard `django.contrib.auth` permissions,
# # or allow read-only access for unauthenticated users.
# 'DEFAULT_PERMISSION_CLASSES': [
#     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
# ],
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'trade.framework.restful.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'trade.framework.authorization.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'trade.framework.authorization.UserPermission',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'trade.framework.restful.MyJSONRenderer',
    ),
    # 'DEFAULT_PAGINATION_CLASS': 'trade.framework.restful.MyPageNumberPagination',
}

JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=24),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,
}


# API服务器域名
API_SERVER_URL = config('API_SERVER_URL')   # 如: http://api.xxx.cn

# 微信公众平台配置
MP_WEB_URL = config('MP_WEB_URL')           # 如: http://www.xxx.cn
MP_APP_ID = config('MP_APP_ID')             # 开发者ID
MP_APP_SECRET = config('MP_APP_SECRET')     # 开发者密码
MP_TOKEN = config('MP_TOKEN')               # 令牌
MP_AES_KEY = config('MP_AES_KEY')           # 消息加解密密钥

# 微信商户平台配置
MP_MERCHANT_ID = config('MP_MERCHANT_ID')   # 商户号
MP_APP_KEY = config('MP_APP_KEY')           # API密钥
MP_MERCHANT_CERT = config('MP_MERCHANT_CERT', default=None)         # 可选. 商户证书路径 (平台上下载). 申请退款, 拉取订单评价数据, 下载资金账单 等个别接口需要证书
MP_MERCHANT_KEY = config('MP_MERCHANT_KEY', default=None)           # 可选. 商户证书私钥路径 (平台上下载).
MP_SUB_MERCHANT_ID = config('MP_SUB_MERCHANT_ID', default=None)     # 可选(一般不需填). 子商户号, 受理模式下需填

# # 公众号客服
# MP_KF_ACCOUNT = config('MP_KF_ACCOUNT')
# MP_KF_NICKNAME = config('MP_KF_NICKNAME')
# MP_KF_PASSWORD = config('MP_KF_PASSWORD')
MP_DEFAULT_REPLY = config('MP_DEFAULT_REPLY', default='宽带接入教程请点击按钮<使用教程>, 有问题可联系管理员')


class ENVIRONMENT(object):
    """
        production:
         - 创建公众号菜单
    """
    environment = config('ENVIRONMENT', default='production')

    @classmethod
    def is_production(cls):
        return cls.environment == 'production'

    @classmethod
    def is_unittest(cls):
        return cls.environment == 'unittest'

    @classmethod
    def is_development(cls):
        return cls.environment == 'development'


TUTORIAL_URL = config('TUTORIAL_URL', default='http://ca1145e4.wiz03.com/share/s/3a4knA3wo4e92gDVx03U7UoV0JuqNU0z3kT629VCU40BeXq6')
SILENCED_SYSTEM_CHECKS = ['urls.W002']

SENTRY_DSN = config('SENTRY_DSN', default='')
sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=ENVIRONMENT.environment,
    integrations=[DjangoIntegration()]
)
