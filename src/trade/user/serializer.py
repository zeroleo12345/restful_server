from rest_framework import serializers

from trade.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('id', 'password')

    uuid = serializers.UUIDField(read_only=True, format='hex')
