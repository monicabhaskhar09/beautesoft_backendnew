# Generated by Django 3.0.7 on 2023-03-06 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_ipad', '0026_auto_20230228_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='webconsultation_dtl',
            name='image',
            field=models.ImageField(blank=True, db_column='image', null=True, upload_to='img'),
        ),
        migrations.AddField(
            model_name='webconsultation_dtl',
            name='pic_data1',
            field=models.TextField(blank=True, null=True),
        ),
    ]
