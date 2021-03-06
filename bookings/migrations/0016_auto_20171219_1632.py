# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-19 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0015_auto_20171219_0521'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='created',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='noressurvey',
            name='reason',
            field=models.CharField(blank=True, choices=[('quotes', "I'm just here to get a quote"), ('prices too high', 'Party buses are too expensive'), ('prices not competitive', 'I found a lower price somewhere else'), ('service', "I'm not sure if you offer the service I'm looking for"), ('bus', 'I want more info on the bus')], max_length=150, null=True),
        ),
    ]
