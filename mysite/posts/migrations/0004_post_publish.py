# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-19 20:11
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_draft'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='publish',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 19, 20, 11, 43, 1254, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
