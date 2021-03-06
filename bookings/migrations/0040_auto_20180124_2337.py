# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-25 05:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0039_auto_20180120_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='prom_package_price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='noressurvey',
            name='reason',
            field=models.CharField(blank=True, choices=[('prices too high', 'Party buses are too expensive'), ('bus', 'I want more info on the bus'), ('quotes', "I'm just here to get a quote"), ('prices not competitive', 'I found a lower price somewhere else'), ('service', "I'm not sure if you offer the service I'm looking for")], max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(blank=True, choices=[('no deposit', 'no deposit'), ('paid deposit', 'paid deposit'), ('completed', 'completed')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(blank=True, choices=[('new', 'new'), ('pending', 'pending'), ('completed', 'completed')], max_length=100, null=True),
        ),
    ]
