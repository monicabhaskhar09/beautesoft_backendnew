# Generated by Django 3.0.7 on 2023-01-26 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0337_auto_20230126_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='posdaud',
            name='holditemqty',
            field=models.IntegerField(blank=True, db_column='HoldItemQty', null=True),
        ),
    ]
