# Generated by Django 3.0.7 on 2021-12-21 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0190_fmspw_flgtransacdisc'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='item_price_ceiling',
            field=models.FloatField(blank=True, db_column='Item_Price_Ceiling', null=True),
        ),
    ]
