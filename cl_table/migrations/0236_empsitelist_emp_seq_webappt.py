# Generated by Django 3.0.7 on 2022-05-30 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0235_paytable_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='empsitelist',
            name='emp_seq_webappt',
            field=models.IntegerField(blank=True, db_column='Emp_Seq_WebAppt', null=True),
        ),
    ]
