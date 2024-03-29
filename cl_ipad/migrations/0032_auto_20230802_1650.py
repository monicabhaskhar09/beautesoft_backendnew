# Generated by Django 3.0.7 on 2023-08-02 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_ipad', '0031_webconsultation_analysismaster'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webconsultation_analysismaster',
            name='body_part',
        ),
        migrations.RemoveField(
            model_name='webconsultation_analysismaster',
            name='footer_part',
        ),
        migrations.RemoveField(
            model_name='webconsultation_analysismaster',
            name='header_part',
        ),
        migrations.AddField(
            model_name='webconsultation_analysismaster',
            name='body',
            field=models.BooleanField(db_column='body', default=False),
        ),
        migrations.AddField(
            model_name='webconsultation_analysismaster',
            name='footer',
            field=models.BooleanField(db_column='footer', default=False),
        ),
        migrations.AddField(
            model_name='webconsultation_analysismaster',
            name='header',
            field=models.BooleanField(db_column='header', default=False),
        ),
    ]
