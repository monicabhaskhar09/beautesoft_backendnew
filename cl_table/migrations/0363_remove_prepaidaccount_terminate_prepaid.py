# Generated by Django 3.0.7 on 2023-05-16 15:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0362_prepaidaccount_terminate_prepaid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prepaidaccount',
            name='terminate_prepaid',
        ),
    ]
