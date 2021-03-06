# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-11 00:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0029_auto_20180110_1817'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bus',
            name='primary_image',
        ),
        migrations.RemoveField(
            model_name='bus',
            name='secondary_image',
        ),
        migrations.AlterField(
            model_name='noressurvey',
            name='reason',
            field=models.CharField(blank=True, choices=[('prices too high', 'Party buses are too expensive'), ('quotes', "I'm just here to get a quote"), ('bus', 'I want more info on the bus'), ('service', "I'm not sure if you offer the service I'm looking for"), ('prices not competitive', 'I found a lower price somewhere else')], max_length=150, null=True),
        ),
    ]
