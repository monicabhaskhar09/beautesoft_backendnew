# Generated by Django 3.0.7 on 2021-06-21 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0035_auto_20210621_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcart',
            name='prepaid_value',
            field=models.FloatField(blank=True, db_column='Prepaid_Value', null=True),
        ),
    ]
