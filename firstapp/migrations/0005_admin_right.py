# Generated by Django 2.0.5 on 2018-05-17 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firstapp', '0004_auto_20180517_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='right',
            field=models.TextField(default='no'),
        ),
    ]
