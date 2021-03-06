# Generated by Django 2.1.13 on 2021-01-18 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0006_order_platform_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='platform_id',
            field=models.BigIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='resourcechange',
            name='out_trade_no',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.BigIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='user_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='user_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='platform',
            name='owner_user_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='resourcechange',
            name='user_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('user_id',), ('openid',)},
        ),
    ]
