# Generated by Django 3.0.7 on 2023-02-03 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_ipad', '0020_tnc_detail_tnc_header'),
    ]

    operations = [
        migrations.AddField(
            model_name='webconsultation_hdr',
            name='signature',
            field=models.ImageField(blank=True, db_column='Signature', null=True, upload_to='img'),
        ),
    ]
