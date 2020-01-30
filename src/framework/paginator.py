from rest_framework import serializers


def validate_number(number, min_number=1, max_number=None):
    """Validate the given 1-based page number."""
    try:
        if isinstance(number, float) and not number.is_integer():
            raise ValueError
        number = int(number)
    except (TypeError, ValueError):
        raise serializers.ValidationError('That page number is not an integer', 'invalid_param')
    if number < min_number:
        raise serializers.ValidationError('That page number is too small', 'invalid_param')
    if max_number and number > max_number:
        raise serializers.ValidationError('That page number is too larger', 'invalid_param')
    return number


class PaginatorValidator(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    per_page = serializers.IntegerField(default=10)

    def validate(self, attrs):
        validate_number(attrs['page'])
        validate_number(attrs['per_page'], max_number=20)
        return attrs
