# Generated by Django 3.0.7 on 2023-04-20 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0355_auto_20230420_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vouchercondition',
            name='isactive',
            field=models.BooleanField(db_column='IsActive', default=True),
        ),
    ]
