# Generated by Django 3.0.7 on 2022-12-27 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0060_auto_20221208_1846'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemsitelist',
            name='showallsitebooking',
            field=models.BooleanField(db_column='showallsitebooking', default=False),
        ),
    ]