# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-20 22:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0038_auto_20180120_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noressurvey',
            name='reason',
            field=models.CharField(blank=True, choices=[('quotes', "I'm just here to get a quote"), ('bus', 'I want more info on the bus'), ('prices not competitive', 'I found a lower price somewhere else'), ('service', "I'm not sure if you offer the service I'm looking for"), ('prices too high', 'Party buses are too expensive')], max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='start_time',
            field=models.TimeField(blank=True, default='16:00', null=True),
        ),
    ]