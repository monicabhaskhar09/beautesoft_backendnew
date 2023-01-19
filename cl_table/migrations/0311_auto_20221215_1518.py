# Generated by Django 3.0.7 on 2022-12-15 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0310_auto_20221214_1359'),
    ]

    operations = [
        migrations.CreateModel(
            name='Treatmentids',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('treatment_parentcode', models.CharField(blank=True, db_column='Treatment_ParentCode', max_length=20, null=True)),
                ('treatment_int', models.IntegerField(blank=True, db_column='treatment_int', null=True)),
            ],
            options={
                'db_table': 'Treatmentids',
            },
        ),
        migrations.AddIndex(
            model_name='treatmentids',
            index=models.Index(fields=['treatment_parentcode'], name='Treatmentid_Treatme_daa149_idx'),
        ),
        migrations.AddIndex(
            model_name='treatmentids',
            index=models.Index(fields=['treatment_int'], name='Treatmentid_treatme_1a34ad_idx'),
        ),
    ]