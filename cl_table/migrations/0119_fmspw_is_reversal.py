# Generated by Django 3.0.7 on 2021-06-08 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0118_auto_20210604_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='fmspw',
            name='is_reversal',
            field=models.BooleanField(db_column='Reversal', default=False),
        ),
    ]
