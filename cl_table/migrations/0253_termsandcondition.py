# Generated by Django 3.0.7 on 2022-07-12 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0252_auditlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='termsandcondition',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('template_name', models.CharField(blank=True, db_column='template_name', max_length=500, null=True)),
                ('template_text', models.TextField(blank=True, db_column='template_text', null=True)),
                ('isactive', models.BooleanField(db_column='isactive', default=True)),
            ],
            options={
                'db_table': 'termsandcondition',
            },
        ),
    ]
