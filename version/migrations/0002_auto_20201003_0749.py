# Generated by Django 3.1.1 on 2020-10-03 12:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('version', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='version',
            options={'verbose_name': 'Version', 'verbose_name_plural': 'Versions'},
        ),
        migrations.AddField(
            model_name='version',
            name='locked',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='version',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='version',
            name='private',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='version',
            name='status',
            field=models.CharField(choices=[('Master', 'Master'), ('Version', 'Version'), ('Conflicted', 'Conflicted'), ('History', 'History'), ('Reconciled', 'Reconciled'), ('Merged', 'Merged')], default='Master', max_length=12),
        ),
    ]