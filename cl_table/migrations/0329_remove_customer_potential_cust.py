# Generated by Django 3.0.7 on 2023-01-20 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0328_auto_20230120_1647'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='potential_cust',
        ),
    ]
