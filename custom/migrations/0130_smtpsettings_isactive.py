# Generated by Django 3.0.7 on 2023-05-26 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0129_remove_paymodechangelog_taudid'),
    ]

    operations = [
        migrations.AddField(
            model_name='smtpsettings',
            name='isactive',
            field=models.BooleanField(db_column='Isactive', default=True),
        ),
    ]
