# Generated by Django 3.0.7 on 2022-05-24 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0091_remove_itemcart_is_prepaidused'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcart',
            name='is_flexinewservice',
            field=models.BooleanField(default=False),
        ),
    ]
