# Generated by Django 3.0.7 on 2021-06-08 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0038_auto_20210603_1443'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemsitelist',
            name='is_nric',
            field=models.BooleanField(db_column='Nric', default=False),
        ),
    ]
