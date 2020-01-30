# 第三方库
from django.utils import timezone
import factory
# 项目库
from models.factories.user import UserFactory
from models import Resource


class ResourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Resource

    user = factory.SubFactory(UserFactory)
    expired_at = timezone.localtime()
    updated_at = timezone.localtime()
