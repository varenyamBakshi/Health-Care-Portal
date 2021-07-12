# Generated by Django 3.0.10 on 2020-10-24 07:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20201024_1247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='timeslot',
        ),
        migrations.AddField(
            model_name='doctor',
            name='close_time',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctor',
            name='open_time',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]