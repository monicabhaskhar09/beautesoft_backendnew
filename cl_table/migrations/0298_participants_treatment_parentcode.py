# Generated by Django 3.0.7 on 2022-10-25 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0297_auto_20221020_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='participants',
            name='treatment_parentcode',
            field=models.CharField(blank=True, db_column='Treatment_ParentCode', max_length=20, null=True),
        ),
    ]
