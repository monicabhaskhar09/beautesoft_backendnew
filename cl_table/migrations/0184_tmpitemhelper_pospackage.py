# Generated by Django 3.0.7 on 2021-11-25 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0046_datechangelog'),
        ('cl_table', '0183_remove_appointment_new_appt'),
    ]

    operations = [
        migrations.AddField(
            model_name='tmpitemhelper',
            name='pospackage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='custom.PosPackagedeposit'),
        ),
    ]
