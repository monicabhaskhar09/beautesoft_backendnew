# Generated by Django 3.0.7 on 2021-11-18 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0178_auto_20211118_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='appt_new',
            field=models.BooleanField(blank=True, db_column='Appt_New', null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='new',
            field=models.BooleanField(db_column='New', null=True),
        ),
    ]
