# Generated by Django 3.0.7 on 2023-04-24 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0358_auto_20230424_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepaidopencondition',
            name='itembrand_id',
            field=models.IntegerField(blank=True, db_column='itembrand_id', null=True),
        ),
        migrations.AddField(
            model_name='prepaidopencondition',
            name='itemdept_id',
            field=models.IntegerField(blank=True, db_column='itemdept_id', null=True),
        ),
    ]
