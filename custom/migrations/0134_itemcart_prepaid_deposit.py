# Generated by Django 3.0.7 on 2023-08-11 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0133_remove_itemcart_prepaid_useamt'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcart',
            name='prepaid_deposit',
            field=models.FloatField(default=0.0, null=True),
        ),
    ]
