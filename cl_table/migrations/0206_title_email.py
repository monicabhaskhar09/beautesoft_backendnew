# Generated by Django 3.0.7 on 2022-03-14 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0205_auto_20220314_0631'),
    ]

    operations = [
        migrations.AddField(
            model_name='title',
            name='email',
            field=models.EmailField(blank=True, db_column='email', max_length=100, null=True),
        ),
    ]
