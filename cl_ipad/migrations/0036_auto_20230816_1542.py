# Generated by Django 3.0.7 on 2023-08-16 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_ipad', '0035_auto_20230814_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='webconsultation_analysisresult',
            name='image1',
            field=models.ImageField(blank=True, db_column='image1', max_length=255, null=True, upload_to='img'),
        ),
        migrations.AddField(
            model_name='webconsultation_analysisresult',
            name='pic_data2',
            field=models.TextField(blank=True, null=True),
        ),
    ]
