# Generated by Django 3.0.7 on 2021-04-30 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0032_auto_20210419_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usagelevel',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('service_code', models.CharField(blank=True, db_column='Service_Code', max_length=20, null=True)),
                ('item_code', models.CharField(blank=True, db_column='Item_Code', max_length=20, null=True)),
                ('qty', models.CharField(blank=True, db_column='Qty', max_length=10, null=True)),
                ('uom', models.CharField(blank=True, db_column='UOM', max_length=20, null=True)),
                ('sequence', models.IntegerField(blank=True, db_column='Sequence', null=True)),
                ('service_desc', models.CharField(blank=True, db_column='Service_Desc', max_length=50, null=True)),
                ('item_desc', models.CharField(blank=True, db_column='Item_desc', max_length=50, null=True)),
                ('isactive', models.BooleanField(db_column='IsActive')),
            ],
            options={
                'db_table': 'UsageLevel',
                'managed': False,
            },
        ),
    ]
