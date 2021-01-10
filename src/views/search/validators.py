# 第三方库
from rest_framework import serializers


class SearchValidator(serializers.Serializer):
    name = serializers.CharField()
