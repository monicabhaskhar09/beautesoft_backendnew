# Generated by Django 3.0.7 on 2021-06-04 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0117_auto_20210603_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='treatment_master',
            name='checktype',
            field=models.CharField(blank=True, choices=[('service', 'service'), ('package', 'package'), ('freetext', 'freetext')], db_column='Check Type', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='treatment_master',
            name='treat_parentcode',
            field=models.CharField(blank=True, db_column='Treat_ParentCode', max_length=20, null=True),
        ),
    ]
