# Generated by Django 3.0.7 on 2022-05-16 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0090_itemcart_is_prepaidused'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemcart',
            name='is_prepaidused',
        ),
    ]