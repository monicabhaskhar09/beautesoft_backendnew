# Generated by Django 3.0.7 on 2023-11-20 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0397_fmspw_flgpoint'),
    ]

    operations = [
        migrations.CreateModel(
            name='apiUrls',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('url_description', models.CharField(blank=True, db_column='urlDescription', max_length=250, null=True)),
                ('url', models.CharField(blank=True, db_column='url', max_length=250, null=True)),
            ],
            options={
                'db_table': 'apiUrls',
            },
        ),
    ]
