# Generated by Django 2.0.5 on 2018-05-17 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firstapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=256)),
            ],
        ),
        migrations.RemoveField(
            model_name='person',
            name='email',
        ),
    ]
