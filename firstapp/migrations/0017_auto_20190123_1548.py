# Generated by Django 2.0.5 on 2019-01-23 08:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('firstapp', '0016_auto_20190123_1543'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registrationdata',
            old_name='partonymic',
            new_name='patronymic',
        ),
        migrations.AlterField(
            model_name='passwordrecoverydata',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 23, 8, 44, 24, 492851, tzinfo=utc)),
        ),
    ]
