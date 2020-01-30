from rest_framework.fields import DateField


class NullDateField(DateField):
    def __init__(self, **kwargs):
        assert 'allow_null' not in kwargs, '`allow_null` is not a valid option.'
        kwargs['allow_null'] = True
        super(NullDateField, self).__init__(**kwargs)

    def to_internal_value(self, value):
        if value == '':
            return None
        return super(NullDateField, self).to_internal_value(value=value)
