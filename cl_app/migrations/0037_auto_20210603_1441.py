# Generated by Django 3.0.7 on 2021-06-03 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0036_usagelevel_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemsitelist',
            name='service_sel',
            field=models.BooleanField(db_column='Service Selection', default=False, null=True),
        ),
        migrations.AddField(
            model_name='itemsitelist',
            name='service_text',
            field=models.BooleanField(db_column='Service Text', default=False, null=True),
        ),
    ]
