# Generated by Django 3.0.7 on 2021-08-02 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0044_merge_20210717_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemsitelist',
            name='is_automember',
            field=models.BooleanField(db_column='IsAutoMember', default=False),
        ),
    ]
