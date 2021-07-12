# Generated by Django 3.0.10 on 2020-10-24 07:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20201024_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='alloted_time',
            field=models.TimeField(blank=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='meeting_link',
            field=models.URLField(blank=True),
        ),
        migrations.CreateModel(
            name='Medecine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('detail', models.CharField(blank=True, max_length=100, null=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Appointment')),
            ],
        ),
    ]