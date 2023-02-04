# Generated by Django 3.0.7 on 2023-01-23 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0333_auto_20230123_1458'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerextended',
            name='or_key',
        ),
        migrations.AddField(
            model_name='customer',
            name='or_key',
            field=models.CharField(blank=True, db_column='OR_KEY', max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='masterdatastock',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('item_name', models.CharField(blank=True, db_column='Item_Name', max_length=60, null=True)),
                ('item_div', models.CharField(blank=True, db_column='Item_Div', max_length=20, null=True)),
                ('item_type', models.CharField(blank=True, db_column='Item_Type', max_length=20, null=True)),
                ('Stock_PIC', models.ImageField(null=True, upload_to='img')),
                ('item_code', models.CharField(blank=True, max_length=20, null=True)),
                ('item_price', models.DecimalField(blank=True, db_column='Item_Price', decimal_places=4, max_digits=19, null=True)),
                ('prepaid_value', models.FloatField(blank=True, db_column='Prepaid_Value', null=True)),
                ('redeempoints', models.FloatField(blank=True, db_column='redeempoints', null=True)),
                ('item_seq', models.IntegerField(default=1, null=True)),
                ('item_isactive', models.BooleanField(default=True)),
                ('Item_Classid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemClass')),
                ('Item_Deptid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemDept')),
                ('Item_Divid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemDiv')),
                ('Item_Rangeid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemRange')),
                ('Item_Typeid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemType')),
            ],
            options={
                'db_table': 'masterdatastock',
            },
        ),
    ]
