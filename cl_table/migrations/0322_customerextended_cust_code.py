# Generated by Django 3.0.7 on 2023-01-20 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0321_auto_20230119_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerextended',
            name='cust_code',
            field=models.CharField(db_column='Cust_code', max_length=255, null=True),
        ),
    ]