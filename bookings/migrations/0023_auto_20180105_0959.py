# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-05 15:59
from __future__ import unicode_literals

import bookings.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0022_auto_20180102_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='primary_image',
            field=models.ImageField(blank=True, null=True, upload_to=bookings.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='noressurvey',
            name='reason',
            field=models.CharField(blank=True, choices=[('prices too high', 'Party buses are too expensive'), ('bus', 'I want more info on the bus'), ('quotes', "I'm just here to get a quote"), ('service', "I'm not sure if you offer the service I'm looking for"), ('prices not competitive', 'I found a lower price somewhere else')], max_length=150, null=True),
        ),
    ]
