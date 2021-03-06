# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-04 05:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_auto_20171204_0233'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='first_name',
            field=models.CharField(default='test', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='last_name',
            field=models.CharField(default='test', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='location_drop_off',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
