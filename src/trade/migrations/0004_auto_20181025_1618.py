# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-10-25 16:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0003_auto_20181014_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcechange',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.User'),
        ),
    ]
