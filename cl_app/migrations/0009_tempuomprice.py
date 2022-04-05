# Generated by Django 3.0.7 on 2020-10-24 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0068_stock_favorites'),
        ('cl_app', '0008_auto_20201013_0749'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempUomPrice',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('item_code', models.CharField(blank=True, db_column='Item_Code', max_length=20, null=True)),
                ('cust_code', models.CharField(blank=True, db_column='Cust_Code', max_length=20, null=True)),
                ('cart_id', models.CharField(blank=True, max_length=20, null=True)),
                ('cart_date', models.DateField(blank=True, db_column='Cart_Date', null=True)),
                ('item_uom', models.CharField(blank=True, db_column='Item_UOM', max_length=20, null=True)),
                ('item_price', models.FloatField(blank=True, db_column='ITEM_PRICE', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('Cust_Codeid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Customer')),
                ('Item_Codeid', models.ForeignKey(blank=True, db_column='itemCodeid', null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Stock')),
                ('Item_UOMid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemUom')),
            ],
            options={
                'db_table': 'Temp_UomPrice',
            },
        ),
    ]
