# Generated by Django 3.0.7 on 2023-01-10 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0125_auto_20221209_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcart',
            name='batch_sno',
            field=models.CharField(blank=True, db_column='BATCH_SNO', max_length=30, null=True),
        ),
    ]
