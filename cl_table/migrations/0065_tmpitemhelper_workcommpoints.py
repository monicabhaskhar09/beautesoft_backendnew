# Generated by Django 3.0.7 on 2020-10-16 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0064_auto_20201016_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='tmpitemhelper',
            name='workcommpoints',
            field=models.FloatField(blank=True, db_column='WorkCommPoints', default=0.0, null=True),
        ),
    ]
