from collections import OrderedDict

from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import exceptions


class MyJSONRenderer(JSONRenderer):
    def get_indent(self, accepted_media_type, renderer_context):
        return 2

    def render(self, data, *args, **kwargs):
        if data is None:
            data = {'code': 'ok'}

        if 'code' not in data:
            data = {
                'code': 'ok',
                'data': data,
            }

        return super().render(data, *args, **kwargs)


class MyPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total_count', self.page.paginator.count),
            ('results', data)
        ]))


def get_authorization_header(request):
    key = request.META.get('HTTP_88_TOKEN')
    if not key:
        raise exceptions.NotAuthenticated()
    return key
