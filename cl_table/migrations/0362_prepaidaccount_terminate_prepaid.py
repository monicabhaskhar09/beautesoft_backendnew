# Generated by Django 3.0.7 on 2023-05-16 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0361_auto_20230515_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepaidaccount',
            name='terminate_prepaid',
            field=models.BooleanField(default=False),
        ),
    ]
