# Generated by Django 3.0.7 on 2021-04-01 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0023_auto_20210331_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='treatmentusage',
            name='isactive',
            field=models.BooleanField(blank=True, db_column='IsActive', default=True, null=True),
        ),
    ]
