# Generated by Django 3.0.10 on 2020-10-29 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_pharmacist_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pharmacist',
            name='Pharmaimage',
        ),
    ]