# 第三方库
from django.utils import timezone
import factory
# 自己的库
from trade.user.factories import UserFactory
from trade.resource.models import Resource


class ResourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Resource

    user = factory.SubFactory(UserFactory)
    expired_at = timezone.localtime()
    updated_at = timezone.localtime()