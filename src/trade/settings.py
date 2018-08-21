#!/usr/bin/env python
# coding:utf-8
"""
Django settings for trade project.

Generated by 'django-admin startproject' using Django 1.11.12.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

import dj_database_url
import datetime
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-4r%#j%!suu2$8!)8!tvjkvyoska9swt#b8&=9pdo%ux-%we%)'

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
if DEBUG:
    MIDDLEWARE += [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

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

# API服务器域名, 如: 'http://api.xxx.cn'
API_SERVER_URL = config('API_SERVER_URL')

# 微信公众平台, 如: 'http://www.xxx.cn'
MP_WEB_URL = config('MP_WEB_URL')
MP_APP_ID = config('MP_APP_ID')             # 开发者ID
MP_APP_SECRET = config('MP_APP_SECRET')     # 开发者密码
MP_TOKEN = config('MP_TOKEN')               # 令牌
MP_AES_KEY = config('MP_AES_KEY')           # 消息加解密密钥
"""
# # 微信商户平台
MP_MERCHANT_ID = config('MP_MERCHANT_ID')   # 商户号
MP_APP_KEY = config('MP_APP_KEY')           # API密钥
MP_MERCHANT_CERT = config('MP_MERCHANT_CERT', default=None)         # 商户证书路径
MP_MERCHANT_KEY = config('MP_MERCHANT_KEY', default=None)           # 商户证书私钥路径
# # 未确定哪里获取
MP_SUB_MERCHANT_ID = config('MP_SUB_MERCHANT_ID', default=None)     # 可选. 子商户号, 受理模式下必填
# # 公众号客服
# MP_KF_ACCOUNT = config('MP_KF_ACCOUNT')
# MP_KF_NICKNAME = config('MP_KF_NICKNAME')
# MP_KF_PASSWORD = config('MP_KF_PASSWORD')
"""

# PayJS
PAYJS_MERCHANT_ID = config('PAYJS_MERCHANT_ID')     # payjs 商户号
PAYJS_MERCHANT_KEY = config('PAYJS_MERCHANT_KEY')   # payjs API密钥


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


SILENCED_SYSTEM_CHECKS = ['urls.W002']
