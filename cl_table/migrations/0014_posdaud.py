# Generated by Django 3.0.7 on 2020-10-09 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0013_auto_20201009_0824'),
    ]

    operations = [
        migrations.CreateModel(
            name='PosDaud',
            fields=[
                ('dt_no', models.AutoField(primary_key=True, serialize=False)),
                ('mac_code', models.CharField(blank=True, max_length=15, null=True)),
                ('sa_date', models.DateTimeField(blank=True, null=True)),
                ('sa_time', models.DateTimeField(blank=True, null=True)),
                ('cas_logno', models.CharField(max_length=20)),
                ('sa_transacno', models.CharField(max_length=20)),
                ('dt_status', models.CharField(blank=True, max_length=5, null=True)),
                ('dt_itemno', models.CharField(blank=True, max_length=20, null=True)),
                ('dt_itemdesc', models.CharField(max_length=200)),
                ('dt_price', models.FloatField(blank=True, null=True)),
                ('dt_promoprice', models.FloatField(blank=True, db_column='dt_PromoPrice', null=True)),
                ('dt_amt', models.FloatField(blank=True, null=True)),
                ('dt_qty', models.IntegerField(blank=True, null=True)),
                ('dt_discamt', models.FloatField(blank=True, db_column='dt_discAmt', null=True)),
                ('dt_discpercent', models.FloatField(blank=True, db_column='dt_discPercent', null=True)),
                ('dt_discdesc', models.CharField(blank=True, db_column='dt_discDesc', max_length=20, null=True)),
                ('dt_discno', models.CharField(blank=True, max_length=10, null=True)),
                ('dt_remark', models.CharField(blank=True, max_length=60, null=True)),
                ('dt_staffno', models.CharField(blank=True, db_column='dt_Staffno', max_length=100, null=True)),
                ('dt_staffname', models.CharField(blank=True, db_column='dt_StaffName', max_length=600, null=True)),
                ('dt_reason', models.IntegerField(blank=True, db_column='dt_Reason', null=True)),
                ('dt_discuser', models.CharField(blank=True, db_column='dt_DiscUser', max_length=50, null=True)),
                ('dt_combocode', models.CharField(blank=True, db_column='dt_ComboCode', max_length=20, null=True)),
                ('itemsite_code', models.CharField(db_column='ItemSite_Code', max_length=10)),
                ('dt_lineno', models.IntegerField(db_column='dt_LineNo')),
                ('dt_stockupdate', models.CharField(blank=True, db_column='dt_StockUpdate', max_length=20, null=True)),
                ('dt_stockremark', models.CharField(blank=True, db_column='dt_StockRemark', max_length=200, null=True)),
                ('dt_uom', models.CharField(blank=True, db_column='dt_UOM', max_length=20, null=True)),
                ('isfoc', models.BooleanField(db_column='IsFoc')),
                ('item_remarks', models.CharField(blank=True, db_column='Item_Remarks', max_length=500, null=True)),
                ('next_payment', models.CharField(blank=True, db_column='Next_Payment', max_length=20, null=True)),
                ('next_appt', models.CharField(blank=True, db_column='Next_Appt', max_length=20, null=True)),
                ('dt_transacamt', models.FloatField(blank=True, db_column='dt_TransacAmt', null=True)),
                ('dt_deposit', models.FloatField(blank=True, null=True)),
                ('appt_time', models.CharField(blank=True, db_column='Appt_Time', max_length=10, null=True)),
                ('hold_item_out', models.BooleanField(db_column='Hold_Item_Out')),
                ('issue_date', models.DateTimeField(blank=True, db_column='Issue_Date', null=True)),
                ('hold_item', models.BooleanField(db_column='Hold_Item')),
                ('holditemqty', models.IntegerField(blank=True, db_column='HoldItemQty', null=True)),
                ('st_ref_treatmentcode', models.CharField(db_column='ST_Ref_TreatmentCode', max_length=20)),
                ('item_status_code', models.CharField(blank=True, db_column='Item_Status_Code', max_length=50, null=True)),
                ('first_trmt_done', models.BooleanField(db_column='First_Trmt_Done')),
                ('first_trmt_done_staff_code', models.CharField(blank=True, db_column='First_Trmt_Done_Staff_Code', max_length=200, null=True)),
                ('first_trmt_done_staff_name', models.CharField(blank=True, db_column='First_Trmt_Done_Staff_Name', max_length=200, null=True)),
                ('record_detail_type', models.CharField(blank=True, db_column='Record_Detail_Type', max_length=50, null=True)),
                ('trmt_done_staff_code', models.CharField(blank=True, db_column='Trmt_Done_Staff_Code', max_length=200, null=True)),
                ('trmt_done_staff_name', models.CharField(blank=True, db_column='Trmt_Done_Staff_Name', max_length=200, null=True)),
                ('trmt_done_id', models.CharField(blank=True, db_column='Trmt_Done_ID', max_length=50, null=True)),
                ('trmt_done_type', models.CharField(blank=True, db_column='Trmt_Done_Type', max_length=50, null=True)),
                ('topup_service_trmt_code', models.CharField(blank=True, db_column='TopUp_Service_Trmt_Code', max_length=50, null=True)),
                ('topup_product_treat_code', models.CharField(blank=True, db_column='TopUp_Product_Treat_Code', max_length=50, null=True)),
                ('topup_prepaid_trans_code', models.CharField(blank=True, db_column='TopUp_Prepaid_Trans_Code', max_length=50, null=True)),
                ('topup_prepaid_type_code', models.CharField(blank=True, db_column='TopUp_Prepaid_Type_Code', max_length=50, null=True)),
                ('voucher_link_cust', models.BooleanField(db_column='Voucher_Link_Cust')),
                ('voucher_no', models.CharField(blank=True, db_column='Voucher_No', max_length=50, null=True)),
                ('update_prepaid_bonus', models.BooleanField(db_column='Update_Prepaid_Bonus')),
                ('deduct_commission', models.BooleanField(db_column='Deduct_Commission')),
                ('deduct_comm_refline', models.IntegerField(blank=True, db_column='Deduct_comm_refLine', null=True)),
                ('gst_amt_collect', models.FloatField(blank=True, db_column='GST_Amt_Collect', null=True)),
                ('topup_prepaid_pos_trans_lineno', models.IntegerField(blank=True, db_column='TopUp_Prepaid_POS_Trans_LineNo', null=True)),
                ('open_pp_uid_ref', models.CharField(blank=True, db_column='OPEN_PP_UID_REF', max_length=50, null=True)),
                ('compound_code', models.CharField(blank=True, db_column='COMPOUND_CODE', max_length=50, null=True)),
                ('topup_outstanding', models.FloatField(blank=True, db_column='TopUp_Outstanding', null=True)),
                ('t1_tax_code', models.CharField(blank=True, db_column='T1_Tax_Code', max_length=20, null=True)),
                ('t1_tax_amt', models.FloatField(blank=True, db_column='T1_Tax_Amt', null=True)),
                ('t2_tax_code', models.CharField(blank=True, db_column='T2_Tax_Code', max_length=20, null=True)),
                ('t2_tax_amt', models.FloatField(blank=True, db_column='T2_Tax_Amt', null=True)),
                ('dt_grossamt', models.CharField(blank=True, db_column='dt_GrossAmt', max_length=20, null=True)),
            ],
            options={
                'db_table': 'pos_daud',
            },
        ),
    ]
