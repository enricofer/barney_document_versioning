# Generated by Django 2.0.13 on 2021-01-19 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('version', '0002_version_condiv'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='version',
            name='private',
        ),
    ]
