# Generated by Django 3.0.7 on 2023-02-20 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0344_multistaff_deposit'),
    ]

    operations = [
        migrations.AddField(
            model_name='multistaff',
            name='gt1deposit',
            field=models.FloatField(db_column='GT1Deposit', null=True),
        ),
    ]
