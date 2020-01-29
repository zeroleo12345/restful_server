from django.utils import timezone

import factory
from models.models import Orders


class OrdersFactory(factory.DjangoModelFactory):
    class Meta:
        model = Orders

    openid = factory.Sequence(lambda n: f'openid_{n}')
    out_trade_no = factory.Sequence(lambda n: f'out_trade_no_{n}')
    attach = factory.Sequence(lambda n: f'attach_{n}')
    transaction_id = factory.Sequence(lambda n: f'transaction_id_{n}')
    total_fee = 1
    appid = 'payjs'
    mch_id = 'mch_id'
    status = factory.Iterator([status[0] for status in Orders.STATUS])
    created_at = timezone.localtime()
    updated_at = timezone.localtime()
