# Generated by Django 3.0.7 on 2021-10-21 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0167_treatmentduration'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='item_seq',
            field=models.IntegerField(db_column='item_seq', default=1, null=True),
        ),
    ]
