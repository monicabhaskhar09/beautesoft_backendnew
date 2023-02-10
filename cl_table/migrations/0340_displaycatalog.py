# Generated by Django 3.0.7 on 2023-02-04 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0339_auto_20230127_1136'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisplayCatalog',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('menu_code', models.CharField(db_column='menuCode', max_length=80)),
                ('parent_code', models.CharField(blank=True, db_column='parentCode', max_length=80, null=True)),
                ('menu_description', models.CharField(blank=True, db_column='menuDescription', max_length=300, null=True)),
                ('bgcolor', models.CharField(blank=True, db_column='bgColor', max_length=80, null=True)),
                ('imagepath', models.ImageField(blank=True, db_column='imagePath', null=True, upload_to='img')),
                ('seqnumber', models.IntegerField(blank=True, db_column='seqNumber', null=True)),
                ('isactive', models.BooleanField(db_column='isActive', default=True)),
            ],
            options={
                'db_table': 'DisplayCatalog',
                'unique_together': {('menu_code',)},
            },
        ),
    ]
