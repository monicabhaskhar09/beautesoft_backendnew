# Generated by Django 3.0.7 on 2023-01-20 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0323_auto_20230120_1624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='cust_activeyn',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_blacklist',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_company',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_credit',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_defaultlist',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_membership',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_membershipfee',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_membershipused',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_ofsaddr1',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_ofsaddr2',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_ofsfax',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_pager',
        ),
    ]
