# Generated by Django 3.0.7 on 2023-09-16 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0073_auto_20230914_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usagelevel',
            name='optional',
            field=models.BooleanField(db_column='Optional', null=True),
        ),
    ]