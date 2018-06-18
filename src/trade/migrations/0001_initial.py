# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-18 06:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('expired_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'resource',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'token',
            },
        ),
        migrations.CreateModel(
            name='TradeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=255)),
                ('out_trade_no', models.CharField(max_length=255, unique=True)),
                ('attach', models.CharField(max_length=255)),
                ('transaction_id', models.CharField(max_length=255)),
                ('total_fee', models.IntegerField()),
                ('appid', models.CharField(max_length=32)),
                ('mch_id', models.CharField(max_length=32)),
                ('status', models.CharField(choices=[('unpaid', '未支付'), ('paid', '已支付'), ('expired', '已过期')], default='unpaid', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'trade_history',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('openid', models.CharField(max_length=255, unique=True)),
                ('nickname', models.CharField(max_length=255)),
                ('headimgurl', models.URLField(max_length=512)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('username', models.CharField(max_length=255, null=True, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('is_enable', models.BooleanField(default=True)),
                ('role', models.CharField(choices=[('vip', 'VIP用户'), ('user', '用户'), ('guest', '访客')], default='user', max_length=32)),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.AddField(
            model_name='token',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', to='trade.User', verbose_name='User'),
        ),
        migrations.AddField(
            model_name='resource',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.User'),
        ),
    ]
