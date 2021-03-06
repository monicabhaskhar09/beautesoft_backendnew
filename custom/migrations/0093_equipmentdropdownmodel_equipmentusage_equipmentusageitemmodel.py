# Generated by Django 3.0.7 on 2022-05-25 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0235_paytable_qr_code'),
        ('custom', '0092_itemcart_is_flexinewservice'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentDropdownModel',
            fields=[
                ('id', models.AutoField(db_column='Dropdown_ID', primary_key=True, serialize=False)),
                ('dropdown_item', models.CharField(blank=True, db_column='Dropdown_Item', default='', max_length=255, null=True)),
                ('dropdown_desc', models.CharField(blank=True, db_column='Dropdown_Desc', default='', max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'EquipmentDropdownModel',
            },
        ),
        migrations.CreateModel(
            name='EquipmentUsage',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('eq_number', models.CharField(blank=True, db_column='EQ_Number', default='', max_length=255, null=True)),
                ('title', models.CharField(blank=True, db_column='Project', default='', max_length=255, null=True)),
                ('company', models.CharField(blank=True, db_column='Company', default='', max_length=255, null=True)),
                ('contact_person', models.CharField(blank=True, db_column='ContactPerson', default='', max_length=255, null=True)),
                ('status', models.CharField(blank=True, db_column='Status', default='', max_length=255, null=True)),
                ('validity', models.CharField(blank=True, db_column='Validity', default='', max_length=255, null=True)),
                ('terms', models.CharField(blank=True, db_column='Terms', default='', max_length=255, null=True)),
                ('in_charge', models.CharField(blank=True, db_column='InCharge', default='', max_length=255, null=True)),
                ('remarks', models.CharField(blank=True, db_column='Remarks', default='', max_length=255, null=True)),
                ('footer', models.CharField(blank=True, db_column='Footer', default='', max_length=255, null=True)),
                ('active', models.CharField(blank=True, db_column='Active', default='active', max_length=255, null=True)),
                ('created_at', models.DateTimeField(db_column='Issue_Date', null=True)),
            ],
            options={
                'db_table': 'EquipmentUsage',
            },
        ),
        migrations.CreateModel(
            name='EquipmentUsageItemModel',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('quotation_quantity', models.CharField(blank=True, db_column='Item_Quantity', default='', max_length=255, null=True)),
                ('quotation_unitprice', models.CharField(blank=True, db_column='Item_UnitPrice', default='', max_length=255, null=True)),
                ('quotation_itemremarks', models.CharField(blank=True, db_column='Item_Remarks', default='', max_length=255, null=True)),
                ('quotation_itemcode', models.CharField(blank=True, db_column='Item_Code', default='', max_length=255, null=True)),
                ('quotation_itemdesc', models.CharField(blank=True, db_column='Item_Desc', default='', max_length=255, null=True)),
                ('item_uom', models.CharField(blank=True, db_column='Item_UOM', max_length=600, null=True)),
                ('active', models.CharField(blank=True, db_column='Active', default='active', max_length=255, null=True)),
                ('item_div', models.CharField(blank=True, db_column='Item_Div', max_length=20, null=True)),
                ('Item_Codeid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Stock')),
                ('fk_equipment', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.PROTECT, to='custom.EquipmentUsage')),
            ],
            options={
                'db_table': 'EquipmentUsage_Item',
            },
        ),
    ]
