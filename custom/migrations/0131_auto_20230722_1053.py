# Generated by Django 3.0.7 on 2023-07-22 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0130_smtpsettings_isactive'),
    ]

    operations = [
        migrations.DeleteModel(
            name='City',
        ),
        migrations.DeleteModel(
            name='Country',
        ),
        migrations.DeleteModel(
            name='State',
        ),
    ]
