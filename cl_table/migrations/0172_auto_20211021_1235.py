# Generated by Django 3.0.7 on 2021-10-21 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0171_stock_item_seq'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='item_seq',
            field=models.IntegerField(default=1, null=True),
        ),
    ]
