# Generated by Django 3.0.7 on 2021-03-25 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0099_appointmentlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentlog',
            name='add_duration',
            field=models.TimeField(null=True),
        ),
    ]
