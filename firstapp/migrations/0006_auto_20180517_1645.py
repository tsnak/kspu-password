# Generated by Django 2.0.5 on 2018-05-17 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firstapp', '0005_admin_right'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='right',
            field=models.TextField(),
        ),
    ]
