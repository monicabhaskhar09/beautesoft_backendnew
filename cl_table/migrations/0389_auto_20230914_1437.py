# Generated by Django 3.0.7 on 2023-09-14 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0388_auto_20230914_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fmspw',
            name='flgservicelimit',
            field=models.BooleanField(db_column='flgservicelimit', default=False, null=True),
        ),
    ]
