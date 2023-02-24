# Generated by Django 3.0.7 on 2023-02-24 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0347_treatment_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerextended',
            name='dob_status',
        ),
        migrations.AddField(
            model_name='customer',
            name='dob_status',
            field=models.BooleanField(db_column='DOB_status', null=True),
        ),
    ]
