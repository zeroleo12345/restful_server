# Generated by Django 2.1.13 on 2021-01-19 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0012_auto_20210119_1925'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='platform',
            unique_together={('platform_id',), ('owner_user_id',), ('ssid',)},
        ),
    ]
