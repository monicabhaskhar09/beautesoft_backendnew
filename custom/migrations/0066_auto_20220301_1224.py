# Generated by Django 3.0.7 on 2022-03-01 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0065_auto_20220301_1030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podetailmodel',
            name='BrandCode',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='BrandName',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='ITEMSITE_CODE',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='IsApproved',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='LineNumber',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_AMT',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_APPQTY',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_CANCELQTY',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_DATE',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_DISCAMT',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_DISCPER',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_FOCQTY',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_ID',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_ITEMCODE',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_ITEMDESC',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_ITEMPRICE',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_OUTQTY',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_PRICE',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_QTY',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_RECQTY',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_TIME',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='POD_TTLQTY',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='PO_ID',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='PO_No',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='PersonApproved',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='PostStatus',
        ),
        migrations.RemoveField(
            model_name='podetailmodel',
            name='STATUS',
        ),
        migrations.AddField(
            model_name='podetailmodel',
            name='active',
            field=models.CharField(blank=True, db_column='Active', default='active', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='podetailmodel',
            name='fk_po',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.PROTECT, to='custom.POModel'),
        ),
        migrations.AddField(
            model_name='podetailmodel',
            name='id',
            field=models.AutoField(db_column='PO_Detail_ID', default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='podetailmodel',
            name='po_discount',
            field=models.CharField(blank=True, db_column='PO_Discount', default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='podetailmodel',
            name='po_shipcost',
            field=models.CharField(blank=True, db_column='PO_ShipCost', default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='podetailmodel',
            name='po_taxes',
            field=models.CharField(blank=True, db_column='PO_Taxes', default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='podetailmodel',
            name='po_total',
            field=models.CharField(blank=True, db_column='PO_Total', default='', max_length=255, null=True),
        ),
        migrations.AlterModelTable(
            name='podetailmodel',
            table='PurchaseOrder_Detail',
        ),
    ]
