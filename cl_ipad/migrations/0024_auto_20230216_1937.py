# Generated by Django 3.0.7 on 2023-02-16 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_ipad', '0023_auto_20230210_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webconsultation_questionsub_questions',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='webconsultation_questionsub_questions',
            name='answer_text',
        ),
        migrations.AddField(
            model_name='webconsultation_dtl',
            name='subquestion_number',
            field=models.CharField(blank=True, db_column='subquestionNumber', max_length=10, null=True),
        ),
    ]
