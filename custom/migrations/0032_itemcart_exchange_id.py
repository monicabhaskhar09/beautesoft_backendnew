# Generated by Django 3.0.7 on 2021-05-24 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0115_auto_20210524_1452'),
        ('custom', '0031_remove_itemcart_exchange_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcart',
            name='exchange_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ExchangeDtl'),
        ),
    ]
