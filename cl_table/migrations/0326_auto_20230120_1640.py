# Generated by Django 3.0.7 on 2023-01-20 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0325_auto_20230120_1637'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='age_range0',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='age_range1',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='age_range2',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='age_range3',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='age_range4',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='allergy',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_address4',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_age',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_password',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_servicetype',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_type',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='mcust_code',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='voucher_no',
        ),
    ]