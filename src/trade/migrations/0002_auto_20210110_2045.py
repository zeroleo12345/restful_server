# Generated by Django 2.1.13 on 2021-01-10 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='platform',
            name='qrcode_url',
            field=models.URLField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='platform',
            name='ssid',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
