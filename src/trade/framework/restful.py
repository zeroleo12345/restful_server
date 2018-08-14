from collections import OrderedDict

from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.views import exception_handler


class MyJSONRenderer(JSONRenderer):
    def get_indent(self, accepted_media_type, renderer_context):
        return 2

    def render(self, response, *args, **kwargs):
        if not response:
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
        return Response(OrderedDict([
            ('total_count', self.page.paginator.count),
            ('results', results)
        ]))


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first, to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        if isinstance(exc, exceptions.ValidationError):
            detail = exc.detail[0]
            response.data = {
                'code': detail.code,
                'message': detail.__str__(),
            }
        elif isinstance(exc, exceptions.APIException):
            detail = response.data.pop('detail')
            response.data = {
                'code': detail.code,
                'message': detail.__str__(),
            }

    return response
