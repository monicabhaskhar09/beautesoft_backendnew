# Generated by Django 3.0.7 on 2021-11-18 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0182_auto_20211118_1416'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='new_appt',
        ),
    ]
