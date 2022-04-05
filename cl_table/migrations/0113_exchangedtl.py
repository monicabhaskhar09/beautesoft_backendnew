# Generated by Django 3.0.7 on 2021-05-24 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0112_auto_20210520_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeDtl',
            fields=[
                ('id', models.BigAutoField(db_column='ID', primary_key=True, serialize=False)),
                ('exchange_no', models.CharField(blank=True, db_column='Exchange_No', max_length=20, null=True)),
                ('staff_code', models.CharField(blank=True, db_column='Staff_Code', max_length=50, null=True)),
                ('staff_name', models.CharField(blank=True, db_column='Staff_Name', max_length=50, null=True)),
                ('original_item_code', models.CharField(blank=True, db_column='Original_Item_Code', max_length=50, null=True)),
                ('original_item_name', models.CharField(blank=True, db_column='Original_Item_Name', max_length=250, null=True)),
                ('exchange_item_code', models.CharField(blank=True, db_column='Exchange_Item_Code', max_length=50, null=True)),
                ('exchange_item_name', models.CharField(blank=True, db_column='Exchange_Item_Name', max_length=250, null=True)),
                ('trmt_code', models.CharField(blank=True, db_column='Trmt_Code', max_length=50, null=True)),
                ('trmt_full_code', models.CharField(blank=True, db_column='Trmt_Full_Code', max_length=50, null=True)),
                ('treatment_time', models.CharField(blank=True, db_column='Treatment_Time', max_length=50, null=True)),
                ('sa_transacno', models.CharField(blank=True, db_column='Sa_TransacNo', max_length=50, null=True)),
                ('sa_date', models.DateTimeField(blank=True, db_column='Sa_Date', null=True)),
                ('exchange_date', models.DateTimeField(blank=True, db_column='Exchange_Date', null=True)),
                ('status', models.BooleanField(blank=True, db_column='Status', null=True)),
                ('reverse_date', models.DateTimeField(blank=True, db_column='Reverse_Date', null=True)),
                ('site_code', models.CharField(blank=True, db_column='Site_Code', max_length=50, null=True)),
                ('cust_code', models.CharField(blank=True, db_column='Cust_Code', max_length=50, null=True)),
                ('cust_name', models.CharField(blank=True, db_column='Cust_Name', max_length=50, null=True)),
                ('fe_transacno', models.CharField(blank=True, db_column='FE_TransacNo', max_length=50, null=True)),
            ],
            options={
                'db_table': 'Exchange_Dtl',
            },
        ),
    ]
