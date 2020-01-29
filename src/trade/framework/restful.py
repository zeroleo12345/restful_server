import sys
import traceback
from collections import OrderedDict
# 第三方库
from django.http import JsonResponse
from django.http.response import Http404
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from rest_framework import exceptions
import sentry_sdk
# 项目库
from trade.framework.exception import GlobalException
from trade.settings import log


class BihuResponse(JsonResponse):
    def __init__(self, data=None, safe=True, **kwargs):
        if data is None:
            data = {'code': 'ok'}
        elif 'code' not in data:
            data = {
                'code': 'ok',
                'data': data,
            }
        super(self.__class__, self).__init__(data, safe=safe, **kwargs)


class MyJSONRenderer(JSONRenderer):
    def get_indent(self, accepted_media_type, renderer_context):
        return 2

    def render(self, response, *args, **kwargs):
        if response is None:
            response = {'code': 'ok'}
            return super().render(response, *args, **kwargs)

        if 'code' not in response:
            response = {
                'code': 'ok',
                'data': response,
            }

        return super().render(response, *args, **kwargs)


class MyPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'

    def get_paginated_response(self, results):
        return BihuResponse(OrderedDict([
            ('total_count', self.page.paginator.count),
            ('results', results)
        ]))


def exc_detail_to_message(exc_detail, field_name=''):
    if exc_detail and isinstance(exc_detail, list):
        for detail in exc_detail:
            if not detail:
                continue
            return exc_detail_to_message(detail, field_name)

    elif isinstance(exc_detail, dict):
        if 'message' in exc_detail:
            code = exc_detail['code']
            message = exc_detail['message']

            if field_name:
                code = f"{code}_{field_name}"
                # message = f"{exc_detail['message']}"

            return code, message

        if 'non_field_errors' not in exc_detail:
            field_name, *_ = exc_detail.keys()

        for key, detail in exc_detail.items():
            return exc_detail_to_message(detail, field_name)

    return 'unknown_error', '系统错误'


def custom_exception_handler(e, context):
    if isinstance(e, GlobalException):
        return BihuResponse(e.data, status=e.status)

    if isinstance(e, exceptions.APIException):      # 包含 exceptions.ValidationError
        exc_details = e.get_full_details()
        if 'code' in exc_details and 'message' in exc_details:
            data = exc_details
        else:
            code, message = exc_detail_to_message(exc_details)
            data = {'code': code, 'message': message}
        return BihuResponse(data, status=e.status_code)

    if isinstance(e, Http404):
        data = {'code': 'not_found', 'message': str(e)}
        return BihuResponse(data, status=404)

    if hasattr(sys, '_called_from_test'):
        log.e(str(e))
        return None
    #
    log.e(traceback.format_exc())
    sentry_sdk.capture_exception(e)
    return BihuResponse({'code': 'unknown_error', 'message': '系统错误'}, status=500)
