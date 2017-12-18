# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-18 19:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0012_auto_20171218_0400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noressurvey',
            name='reason',
            field=models.CharField(blank=True, choices=[('service', "I'm not sure if you offer the service I'm looking for"), ('prices too high', 'Party buses are too expensive'), ('prices not competitive', 'I found a lower price somewhere else'), ('quotes', "I'm just here to get a quote"), ('bus', 'I want more info on the bus')], max_length=150, null=True),
        ),
    ]
