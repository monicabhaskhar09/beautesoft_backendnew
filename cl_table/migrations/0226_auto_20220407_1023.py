# Generated by Django 3.0.7 on 2022-04-07 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0225_auto_20220405_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='appt_status',
            field=models.CharField(blank=True, choices=[('Booking', 'Booking'), ('Waiting', 'Waiting List'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'), ('Arrived', 'Arrived'), ('Done', 'Done'), ('LastMinCancel', 'Cancelled Last Minute'), ('Late', 'Late'), ('No Show', 'No Show'), ('Block', 'Block')], db_column='Appt_Status', default='Booking', max_length=20, null=True),
        ),
    ]
