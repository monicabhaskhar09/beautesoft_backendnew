# Generated by Django 3.0.7 on 2023-01-20 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0322_customerextended_cust_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='cust_birthday',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_birthmonth',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_birthyear',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_ccid',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_ctyid',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_expirydate',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_sex',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='exp_status',
        ),
    ]
