# Generated by Django 3.0.7 on 2021-07-19 16:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0131_auto_20210719_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='Cust_titleid',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_consultant_id',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_therapist_id',
        ),
        migrations.RemoveField(
            model_name='schedulehour',
            name='shortdesc',
        ),
        migrations.AlterUniqueTogether(
            name='diagnosis',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='diagnosis',
            name='cust_no',
        ),
    ]
