# Generated by Django 3.0.7 on 2021-06-01 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0032_itemcart_exchange_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcart',
            name='is_total',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
