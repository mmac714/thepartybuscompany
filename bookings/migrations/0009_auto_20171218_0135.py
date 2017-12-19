# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-18 01:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0008_auto_20171218_0131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noressurvey',
            name='reason',
            field=models.CharField(choices=[('quotes', "I'm just here to get a quote"), ('service', "I'm not sure if you offer the service I'm looking for."), ('prices not competitive', 'I found a lower price somewhere else'), ('prices too high', 'Party buses are too expensive'), ('bus', 'I want more info on the bus')], max_length=2),
        ),
    ]