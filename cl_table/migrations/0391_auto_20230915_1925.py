# Generated by Django 3.0.7 on 2023-09-15 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0390_auto_20230915_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prepaidaccount',
            name='item_no',
            field=models.CharField(db_column='ITEM_NO', max_length=50, null=True),
        ),
    ]