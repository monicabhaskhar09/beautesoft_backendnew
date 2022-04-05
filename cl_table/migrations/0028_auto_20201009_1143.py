# Generated by Django 3.0.7 on 2020-10-09 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cl_app', '0002_auto_20201009_0613'),
        ('custom', '0002_auto_20201009_0626'),
        ('cl_table', '0027_auto_20201009_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance2',
            name='Attn_Emp_codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Employee'),
        ),
        migrations.AddField(
            model_name='attendance2',
            name='Attn_Site_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_app.ItemSitelist'),
        ),
        migrations.AddField(
            model_name='attendance2',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance2',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='controlno',
            name='Site_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_app.ItemSitelist'),
        ),
        migrations.AddField(
            model_name='controlno',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='controlno',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='empsitelist',
            name='Emp_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Employee'),
        ),
        migrations.AddField(
            model_name='empsitelist',
            name='Site_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_app.ItemSitelist'),
        ),
        migrations.AddField(
            model_name='empsitelist',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='empsitelist',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='itemclass',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='itemclass',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='itemdept',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='itemdept',
            name='deptpic',
            field=models.ImageField(null=True, upload_to='img'),
        ),
        migrations.AddField(
            model_name='itemdept',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='itemdiv',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='itemdiv',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='itemhelper',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='itemhelper',
            name='td_type_code',
            field=models.CharField(blank=True, db_column='TD_Type_CODE', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='itemhelper',
            name='td_type_short_desc',
            field=models.CharField(blank=True, db_column='TD_Type_Short_Desc', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='itemhelper',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='itemrange',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='itemrange',
            name='itm_Deptid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemDept'),
        ),
        migrations.AddField(
            model_name='itemrange',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='multistaff',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='multistaff',
            name='level_group_code',
            field=models.CharField(blank=True, db_column='Level_group_code', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='multistaff',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='paygroup',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='paygroup',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='paytable',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='paytable',
            name='pay_groupid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.PayGroup'),
        ),
        migrations.AddField(
            model_name='paytable',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='posdisc',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='posdisc',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='schedulehour',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='schedulehour',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='schedulemonth',
            name='Emp_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Employee'),
        ),
        migrations.AddField(
            model_name='schedulemonth',
            name='Site_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_app.ItemSitelist'),
        ),
        migrations.AddField(
            model_name='schedulemonth',
            name='User_Nameid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Fmspw'),
        ),
        migrations.AddField(
            model_name='schedulemonth',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='schedulemonth',
            name='itm_Typeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ScheduleHour'),
        ),
        migrations.AddField(
            model_name='schedulemonth',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='Room_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='custom.Room'),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='add_duration',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='appt_fr_time',
            field=models.TimeField(db_column='Appt_Fr_time', null=True),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='appt_to_time',
            field=models.TimeField(db_column='Appt_To_time', null=True),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='helper_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Employee'),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='itemcart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='custom.ItemCart'),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='new_remark',
            field=models.CharField(db_column='New_Remark', max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='td_type_code',
            field=models.CharField(blank=True, db_column='TD_Type_CODE', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='td_type_short_desc',
            field=models.CharField(blank=True, db_column='TD_Type_Short_Desc', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendance2',
            name='attn_date',
            field=models.DateTimeField(auto_now_add=True, db_column='Attn_Date', null=True),
        ),
        migrations.AlterField(
            model_name='attendance2',
            name='attn_mov_in',
            field=models.IntegerField(db_column='Attn_Mov_In', null=True),
        ),
        migrations.AlterField(
            model_name='attendance2',
            name='attn_time',
            field=models.DateTimeField(auto_now_add=True, db_column='Attn_Time', null=True),
        ),
        migrations.AlterField(
            model_name='attendance2',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, db_column='Create_date', null=True),
        ),
        migrations.AlterField(
            model_name='attendance2',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, db_column='Create_time', null=True),
        ),
        migrations.AlterField(
            model_name='attendance2',
            name='missing_clock',
            field=models.BooleanField(db_column='Missing_Clock', null=True),
        ),
        migrations.AlterField(
            model_name='controlno',
            name='controldate',
            field=models.DateField(blank=True, db_column='CONTROLDATE', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='empsitelist',
            name='emp_code',
            field=models.CharField(db_column='Emp_Code', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='empsitelist',
            name='isactive',
            field=models.BooleanField(db_column='IsActive', default=True),
        ),
        migrations.AlterField(
            model_name='empsitelist',
            name='site_code',
            field=models.CharField(db_column='Site_Code', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='itemclass',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='allowcashsales',
            field=models.BooleanField(db_column='AllowCashSales', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='is_compound',
            field=models.BooleanField(db_column='Is_Compound', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='is_package',
            field=models.BooleanField(db_column='Is_Package', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='is_prepaid',
            field=models.BooleanField(db_column='Is_Prepaid', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='is_retailproduct',
            field=models.BooleanField(db_column='Is_RetailProduct', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='is_salonproduct',
            field=models.BooleanField(db_column='Is_SalonProduct', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='is_service',
            field=models.BooleanField(db_column='Is_Service', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='is_voucher',
            field=models.BooleanField(db_column='Is_Voucher', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='itm_showonsales',
            field=models.BooleanField(db_column='ITM_ShowOnSales', null=True),
        ),
        migrations.AlterField(
            model_name='itemdept',
            name='itm_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='itemdiv',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='itemdiv',
            name='itm_seq',
            field=models.IntegerField(db_column='ITM_SEQ', null=True),
        ),
        migrations.AlterField(
            model_name='itemhelper',
            name='helper_code',
            field=models.CharField(db_column='Helper_Code', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='itemhelper',
            name='helper_transacno',
            field=models.CharField(db_column='Helper_transacno', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='itemhelper',
            name='item_code',
            field=models.CharField(db_column='Item_Code', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='itemhelper',
            name='line_no',
            field=models.IntegerField(db_column='Line_No', null=True),
        ),
        migrations.AlterField(
            model_name='itemhelper',
            name='sa_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='itemhelper',
            name='sa_transacno',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='itemhelper',
            name='site_code',
            field=models.CharField(db_column='Site_code', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='iscompound',
            field=models.BooleanField(db_column='IsCompound', null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='isprepaid',
            field=models.BooleanField(db_column='IsPrepaid', null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='isproduct',
            field=models.BooleanField(db_column='isProduct', null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='isservice',
            field=models.BooleanField(db_column='IsService', null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='isvoucher',
            field=models.BooleanField(db_column='IsVoucher', null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='itm_status',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='prepaid_for_all',
            field=models.BooleanField(db_column='Prepaid_For_All', null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='prepaid_for_product',
            field=models.BooleanField(db_column='Prepaid_For_Product', null=True),
        ),
        migrations.AlterField(
            model_name='itemrange',
            name='prepaid_for_service',
            field=models.BooleanField(db_column='Prepaid_For_Service', null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='dt_lineno',
            field=models.IntegerField(db_column='Dt_LineNo', null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='emp_code',
            field=models.CharField(db_column='Emp_Code', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='isdelete',
            field=models.BooleanField(db_column='IsDelete', null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='item_code',
            field=models.CharField(db_column='Item_Code', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='ratio',
            field=models.FloatField(db_column='Ratio', null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='role',
            field=models.CharField(db_column='Role', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='sa_transacno',
            field=models.CharField(db_column='sa_transacNo', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='salesamt',
            field=models.FloatField(db_column='SalesAmt', null=True),
        ),
        migrations.AlterField(
            model_name='multistaff',
            name='type',
            field=models.CharField(db_column='Type', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='paygroup',
            name='pay_group_code',
            field=models.CharField(db_column='PAY_GROUP_CODE', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='creditcardcharges',
            field=models.DecimalField(db_column='CreditCardCharges', decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='gt_group',
            field=models.CharField(blank=True, choices=[('GT1', 'GT1'), ('GT2', 'GT2')], db_column='GT_Group', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='iscomm',
            field=models.BooleanField(db_column='IsComm', null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='iscustapptpromo',
            field=models.BooleanField(db_column='IsCustApptPromo', null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='isvoucher_extvoucher',
            field=models.BooleanField(db_column='IsVoucher_ExtVoucher', null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='onlinepaymentcharges',
            field=models.DecimalField(db_column='OnlinePaymentCharges', decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='open_cashdrawer',
            field=models.BooleanField(db_column='Open_CashDrawer', null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='pay_is_gst',
            field=models.BooleanField(db_column='PAY_IS_GST', null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='pay_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='rw_usebp',
            field=models.BooleanField(db_column='RW_useBP', null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='show_in_report',
            field=models.BooleanField(db_column='Show_In_Report', null=True),
        ),
        migrations.AlterField(
            model_name='paytable',
            name='voucher_payment_control',
            field=models.BooleanField(db_column='Voucher_Payment_Control', null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='dt_auto',
            field=models.BooleanField(db_column='dt_Auto', null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='dt_date',
            field=models.DateTimeField(auto_now_add=True, db_column='dt_Date', null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='dt_itemno',
            field=models.CharField(db_column='dt_ItemNo', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='dt_lineno',
            field=models.IntegerField(db_column='dt_LineNo', null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='dt_status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='istransdisc',
            field=models.BooleanField(db_column='IsTransDisc', null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='line_no',
            field=models.IntegerField(db_column='Line_no', null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='lnow',
            field=models.BooleanField(db_column='lNow', null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='sa_transacno',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='posdisc',
            name='site_code',
            field=models.CharField(db_column='Site_Code', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='schedulehour',
            name='itm_isactive',
            field=models.BooleanField(blank=True, db_column='ITM_ISACTIVE', default=True, null=True),
        ),
        migrations.AlterField(
            model_name='schedulehour',
            name='offday',
            field=models.BooleanField(db_column='OFFDAY', null=True),
        ),
        migrations.AlterField(
            model_name='schedulehour',
            name='timeframe',
            field=models.CharField(db_column='TimeFrame', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='schedulemonth',
            name='ledit',
            field=models.BooleanField(db_column='lEdit', null=True),
        ),
    ]
