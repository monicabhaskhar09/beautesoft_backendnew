# Generated by Django 3.0.7 on 2023-05-29 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0365_auto_20230516_1545'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='customerextended',
            unique_together={('cust_code', 'cust_name')},
        ),
    ]