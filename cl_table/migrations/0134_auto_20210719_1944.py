# Generated by Django 3.0.7 on 2021-07-19 19:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0133_auto_20210719_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='cardno1',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cardno2',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cardno3',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cardno4',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cardno5',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='emergencycontact',
        ),
    ]
