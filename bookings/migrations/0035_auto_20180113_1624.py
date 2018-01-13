# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-13 22:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0034_auto_20180113_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='primary_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='bus',
            name='secondary_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='noressurvey',
            name='reason',
            field=models.CharField(blank=True, choices=[('quotes', "I'm just here to get a quote"), ('bus', 'I want more info on the bus'), ('prices too high', 'Party buses are too expensive'), ('prices not competitive', 'I found a lower price somewhere else'), ('service', "I'm not sure if you offer the service I'm looking for")], max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(blank=True, choices=[('completed', 'completed'), ('new', 'new'), ('pending', 'pending')], max_length=100, null=True),
        ),
    ]
