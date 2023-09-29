# Generated by Django 3.0.7 on 2023-09-24 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0135_auto_20230916_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smtpsettings',
            name='email_use_ssl',
            field=models.BooleanField(db_column='EMAIL_USE_SSL', default=False),
        ),
        migrations.AlterField(
            model_name='smtpsettings',
            name='email_use_tls',
            field=models.BooleanField(db_column='EMAIL_USE_TLS', default=True),
        ),
    ]
