# Generated by Django 3.0.7 on 2021-10-29 14:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0173_auto_20211021_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prepaidaccountcondition',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccountcondition',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
    ]
