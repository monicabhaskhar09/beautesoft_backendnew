# Generated by Django 3.0.7 on 2023-08-20 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0383_auto_20230812_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepaidaccountcondition',
            name='topup_remain',
            field=models.FloatField(blank=True, db_column='Topup_Remain', null=True),
        ),
    ]