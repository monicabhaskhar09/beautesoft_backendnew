# Generated by Django 3.0.7 on 2021-06-03 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0116_appointmentstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointmentstatus',
            name='is_secstatus',
            field=models.BooleanField(db_column='Sec Status', default=False),
        ),
    ]
