# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-17 00:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_auto_20171215_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
