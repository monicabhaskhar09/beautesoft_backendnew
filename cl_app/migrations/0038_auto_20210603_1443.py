# Generated by Django 3.0.7 on 2021-06-03 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0037_auto_20210603_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemsitelist',
            name='service_sel',
            field=models.BooleanField(db_column='Service Selection', default=False),
        ),
        migrations.AlterField(
            model_name='itemsitelist',
            name='service_text',
            field=models.BooleanField(db_column='Service Text', default=False),
        ),
    ]
