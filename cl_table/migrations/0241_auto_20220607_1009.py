# Generated by Django 3.0.7 on 2022-06-07 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0240_auto_20220607_1006'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='customer',
            unique_together={('cust_code', 'cust_email', 'cust_phone1')},
        ),
    ]