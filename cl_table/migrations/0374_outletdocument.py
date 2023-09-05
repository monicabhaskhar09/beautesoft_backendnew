# Generated by Django 3.0.7 on 2023-07-24 13:11

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0072_remove_tmpitemhelpersession_treatmentpackage'),
        ('cl_table', '0373_staffdocument'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutletDocument',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('filename', models.CharField(blank=True, db_column='filename', max_length=500, null=True)),
                ('document_name', models.CharField(blank=True, db_column='document_name', max_length=500, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('file', models.FileField(upload_to='img')),
                ('site', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_app.ItemSitelist')),
            ],
            options={
                'db_table': 'OutletDocument',
            },
        ),
    ]