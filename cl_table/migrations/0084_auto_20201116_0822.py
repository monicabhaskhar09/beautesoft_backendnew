# Generated by Django 3.0.7 on 2020-11-16 08:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0083_auto_20201116_0819'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poshaud',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='poshaud',
            name='updated_at',
        ),
    ]
