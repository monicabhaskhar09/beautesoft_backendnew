from locale import currency
from django.db import models
from cl_table.models import (Treatment, Stock, ItemStatus, Customer, TmpItemHelper, FocReason,
DepositAccount,PrepaidAccount)
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# Create your models here.
#intial

#Final

class EmpLevel(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    level_code = models.CharField(db_column='Level_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    level_desc = models.CharField(db_column='Level_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    level_isactive = models.BooleanField(db_column='Level_IsActive',default=True)  # Field name made lowercase.
    level_sequence = models.IntegerField(db_column='Level_sequence', blank=True, null=True)  # Field name made lowercase.
    level_spa = models.BooleanField(db_column='Level_SPA', null=True)  # Field name made lowercase.
    mintarget = models.FloatField(db_column='MinTarget', blank=True, null=True)  # Field name made lowercase.
    fromsalary = models.FloatField(db_column='FromSalary', blank=True, null=True)  # Field name made lowercase.
    tosalary = models.FloatField(db_column='ToSalary', blank=True, null=True)  # Field name made lowercase.
    getgroupcomm = models.BooleanField(db_column='GetGroupComm', blank=True, null=True)  # Field name made lowercase.
    group_code = models.CharField(db_column='Group_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'Emp_Level'
    
    def __str__(self):
        return str(self.level_desc)

class Room(models.Model):
    room_code = models.CharField(db_column='Room_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    displayname = models.CharField(db_column='DisplayName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='Isactive', blank=True, null=True,default=True)  # Field name made lowercase.
    equipment = models.CharField(db_column='Equipment', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    id = models.AutoField(primary_key=True)
    roomtype = models.CharField(db_column='roomType', max_length=20, blank=True, null=True)  # Field name made lowercase.
    equipmentpicturelocation = models.CharField(db_column='equipmentPictureLocation', max_length=100, blank=True, null=True)  # Field name made lowercase.
    Sequence_No = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    Room_PIC = models.ImageField(upload_to='img', null=True)

    class Meta:
        db_table = 'Room'

    def __str__(self):
        return str(self.displayname)          

# new tabel
class Combo_Services(models.Model):
    
    id = models.AutoField(primary_key=True)
    services = models.ManyToManyField(Stock, blank=True)
    unit_price = models.FloatField(db_column='Unit_Price',null=True)  # Field name made lowercase.
    Price = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    discount = models.FloatField(null=True)
    updated_at  = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    Isactive = models.BooleanField(default=True)
    Site_Code = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = 'Combo_Services'

    def __str__(self):
        services = ""
        for i in self.services.all():
            if i.item_desc:
                if services == '':
                    services += i.item_desc
                else:
                    services += ","+i.item_desc

        return str(services)

   
    @property
    def get_combo_names(self,obj):
        if obj.services.all():
            string = ""
            for i in obj.services.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None                               

class RoundPoint(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    point = models.FloatField(db_column='Point', blank=True, null=True)  # Field name made lowercase.
    roundvalue = models.FloatField(db_column='RoundValue', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Round_Point'

    def __str__(self):
        return str(self.point) 

class RoundSales(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sales = models.FloatField(db_column='Sales', blank=True, null=True)  # Field name made lowercase.
    roundvalue = models.FloatField(db_column='RoundValue', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Round_Sales'

    def __str__(self):
        return str(self.roundvalue)    

class PaymentRemarks(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    r_code = models.CharField(db_column='R_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    r_desc = models.CharField(db_column='R_Desc', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Payment_Remarks'

    def __str__(self):
        return str(self.r_desc)

class HolditemSetup(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    hold_code = models.CharField(db_column='Hold_code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hold_desc = models.CharField(db_column='Hold_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'HoldItem_Setup'

    def __str__(self):
        return str(self.hold_desc)            

class VoucherRecord(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20, blank=True, null=True)
    voucher_name = models.CharField(db_column='Voucher_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    voucher_no = models.CharField(db_column='Voucher_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    value = models.FloatField(db_column='Value', blank=True, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    cust_codeid = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT,db_column='Cust_codeid',null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    percent = models.FloatField(db_column='Percent', blank=True, null=True)  # Field name made lowercase.
    site_codeid =  models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, db_column='Site_Codeid',null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    issued_expiry_date = models.DateTimeField(db_column='issued_Expiry_Date', blank=True, null=True)  # Field name made lowercase.
    issued_staff = models.CharField(db_column='issued_Staff', max_length=50, blank=True, null=True)  # Field name made lowercase.
    onhold = models.CharField(db_column='onHold', max_length=50, blank=True, null=True)  # Field name made lowercase.
    paymenttype = models.CharField(db_column='PaymentType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=100, blank=True, null=True)  # Field name made lowercase.
    type_code = models.CharField(max_length=50, blank=True, null=True)
    used = models.IntegerField(db_column='Used', blank=True, null=True)  # Field name made lowercase.
    ref_fullvoucherno = models.CharField(db_column='Ref_FullVoucherNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ref_rangefrom = models.CharField(db_column='Ref_RangeFrom', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ref_rangeto = models.CharField(db_column='Ref_RangeTo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    site_allocate = models.CharField(db_column='Site_Allocate', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    isvalid = models.BooleanField(db_column='isValid',default=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Voucher_Record'

    def __str__(self):
        return str(self.voucher_no)     

class ItemCart(models.Model):
    STATUS = [
        ("Inprogress", "Inprogress" ),
        ("Suspension", "Suspension"),
        ("Completed", "Completed"),
    ]

    CHECK = [
        ("New", "New" ),
        ("Old", "Old"),
    ]

    TYPE = [
        ('Deposit', 'Deposit'),
        ('Top Up', 'Top Up'),
        ('Sales','Sales'),
        ('VT-Deposit', 'VT-Deposit'),
        ('VT-Top Up', 'VT-Top Up'),
        ('VT-Sales','VT-Sales'),
        ('Exchange', 'Exchange'),

    ]

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    customercode = models.CharField(db_column='customerCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemcodeid = models.ForeignKey('cl_table.Stock', on_delete=models.PROTECT,db_column='itemCodeid', null=True)   # Field name made lowercase.
    itemcode = models.CharField(db_column='itemCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemdesc = models.CharField(db_column='itemDesc', max_length=500, blank=True, null=True)  # Field name made lowercase.
    quantity = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    sitecodeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, db_column='sitecodeid', null=True)  # Field name made lowercase.
    sitecode = models.CharField(db_column='siteCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True, default=True)  # Field name made lowercase.
    timstamp = models.DateTimeField(db_column='timStamp', blank=True, null=True)  # Field name made lowercase.
    redeempoint = models.FloatField(db_column='redeemPoint', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    Appointment = models.ForeignKey('cl_table.Appointment', on_delete=models.PROTECT, null=True)
    discount = models.FloatField(default=0.0,  null=True)
    discount_amt = models.FloatField(default=0.0,  null=True)
    discount_price = models.FloatField(default=0.0,  null=True)
    sales_staff = models.ManyToManyField('cl_table.Employee',related_name='sales_staff', blank=True)
    service_staff = models.ManyToManyField('cl_table.Employee',related_name='service_staff',  blank=True)
    tax = models.FloatField(  null=True)
    is_payment = models.BooleanField(default=False,null=True)
    additional_discount = models.FloatField( null=True,default=0.0)
    additional_discountamt = models.FloatField( null=True,default=0.0)
    deposit = models.FloatField(default=0.0,  null=True)
    total_price = models.FloatField(default=0.0,  null=True)
    trans_amt = models.FloatField(default=0.0,  null=True)
    itemstatus = models.ForeignKey('cl_table.ItemStatus', on_delete=models.PROTECT,null=True)
    cust_noid =  models.ForeignKey(Customer, on_delete=models.PROTECT,null=True)
    cart_id = models.CharField(max_length=20, null=True)
    cart_date = models.DateField(db_column='Cart_Date',null=True)  # Field name made lowercase.
    cart_status = models.CharField(db_column='Cart_Status', max_length=20, choices=STATUS,default='Inprogress')  # Field name made lowercase.
    lineno = models.IntegerField(db_column='LineNo',null=True)  # Field name made lowercase.
    check = models.CharField(db_column='Check', max_length=20, choices=CHECK, null=True)  # Field name made lowercase.
    ratio = models.DecimalField(max_digits=18,decimal_places=15,db_column='Ratio',null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20,  null=True)
    helper_ids = models.ManyToManyField('cl_table.TmpItemHelper', related_name='itemhelper', blank=True)
    remark = models.CharField(db_column='Remark', max_length=500, null=True)  # Field name made lowercase.
    products_used = models.ManyToManyField('cl_table.Stock',related_name='salon_product', blank=True)   # Field name made lowercase.
    disc_reason = models.ManyToManyField('custom.PaymentRemarks', blank=True)
    discreason_txt = models.CharField(max_length=500,  null=True)  # Field name made lowercase.
    focreason = models.ForeignKey('cl_table.FocReason', on_delete=models.PROTECT,null=True)
    holditemqty = models.IntegerField(db_column='HoldItemQty', null=True)  # Field name made lowercase.
    holdreason = models.ForeignKey('custom.HolditemSetup', on_delete=models.PROTECT,null=True)
    item_uom = models.ForeignKey('cl_table.ItemUom',  on_delete=models.PROTECT,null=True)
    pos_disc = models.ManyToManyField('cl_table.PosDisc', blank=True)
    auto = models.BooleanField(default=True)
    done_sessions = models.CharField(db_column='Done_Sessions', max_length=700, blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=10, blank=True, null=True, choices=TYPE)  # Field name made lowercase.
    treatment_account = models.ForeignKey('cl_table.TreatmentAccount',related_name='trmtacc', on_delete=models.PROTECT,blank=True, null=True)
    treatment = models.ForeignKey('cl_table.Treatment',related_name='Treatment', on_delete=models.PROTECT,blank=True, null=True)
    deposit_account = models.ForeignKey('cl_table.DepositAccount', on_delete=models.PROTECT,blank=True, null=True)
    prepaid_account = models.ForeignKey('cl_table.PrepaidAccount', on_delete=models.PROTECT,blank=True, null=True)
    is_foc =  models.BooleanField(default=False)
    recorddetail = models.CharField(max_length=20,  null=True)
    itemtype = models.CharField(max_length=20,  null=True)
    multistaff_ids = models.ManyToManyField('cl_table.Tmpmultistaff', related_name='multistaff', blank=True)
    treatment_no = models.CharField(db_column='Treatment_No', max_length=10, blank=True, null=True)  # Field name made lowercase.
    free_sessions = models.CharField(db_column='Free_Sessions', max_length=10, blank=True, null=True)  # Field name made lowercase.
    exchange_id = models.ForeignKey('cl_table.ExchangeDtl', on_delete=models.PROTECT,blank=True, null=True)
    is_total = models.BooleanField(default=False,null=True)
    prepaid_value = models.FloatField(db_column='Prepaid_Value', blank=True, null=True)  # Field name made lowercase.
    isopen_prepaid = models.BooleanField(db_column='isOpen_Prepaid',default=False)  # Field name made lowercase.
    sessiondone = models.CharField(db_column='Session_Done', max_length=700, blank=True, null=True)
    multi_treat = models.ManyToManyField('cl_table.Treatment', blank=True)
    is_service = models.BooleanField(default=False,null=True)
    treat_expiry = models.DateField(db_column='Treatment_Expiry', blank=True, null=True)  # Field name made lowercase.
    treat_type = models.CharField(db_column='treat_type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    treatment_limit_times = models.FloatField(db_column='Treatment_Limit_Times', blank=True, null=True)  # Field name made lowercase.
    is_flexi = models.BooleanField(default=False, blank=True, null=True)
    quotationitem_id = models.ForeignKey('custom.QuotationItemModel', on_delete=models.PROTECT,blank=True, null=True)
    is_flexinewservice = models.BooleanField(default=False, blank=True, null=True)
    
    class Meta:
        db_table = 'item_Cart'

    def __str__(self):
        return str(self.itemdesc)   


class PosPackagedeposit(models.Model):

    STATUS = [
        ("PENDING", "PENDING" ),
        ("COMPLETED", "COMPLETED"),
    ]

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    cas_logno = models.CharField(db_column='cas_logNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(db_column='sa_Date', blank=True, null=True, default=timezone.now, editable=False)  # Field name made lowercase.
    sa_time = models.DateTimeField(db_column='sa_Time', blank=True, null=True, default=timezone.now, editable=False)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(db_column='Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=80, blank=True, null=True)  # Field name made lowercase.
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.
    discount = models.CharField(db_column='Discount', max_length=20, blank=True, null=True)  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    package_description = models.CharField(db_column='Package_Description', max_length=80, blank=True, null=True)  # Field name made lowercase.
    qty = models.IntegerField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    unit_price = models.FloatField(db_column='Unit_Price', blank=True, null=True)  # Field name made lowercase.
    ttl_uprice = models.FloatField(db_column='Ttl_Uprice')  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=20)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20,choices=STATUS, blank=True, null=True)  # Field name made lowercase.
    deposit_amt = models.FloatField(db_column='Deposit_Amt')  # Field name made lowercase.
    deposit_lineno = models.IntegerField(db_column='Deposit_LineNo', blank=True, null=True)  # Field name made lowercase.
    hold_qty = models.FloatField(db_column='Hold_Qty', blank=True, null=True)  # Field name made lowercase.
    itemcart = models.ForeignKey('custom.ItemCart', on_delete=models.PROTECT,null=True)
    auto = models.BooleanField(default=True)

    class Meta:
        db_table = 'POS_PackageDeposit'

    def __str__(self):
        return str(self.code)


class SmtpSettings(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sender_name = models.CharField(db_column='Sender_Name', max_length=200, blank=True, null=True)  # Field name made lowercase.
    sender_address = models.CharField(db_column='Sender_Address', max_length=200, blank=True, null=True)  # Field name made lowercase.
    smtp_serverhost = models.CharField(db_column='Smtp_Serverhost', max_length=500, blank=True, null=True)  # Field name made lowercase.
    port = models.CharField(db_column='Port', max_length=100, blank=True, null=True)  # Field name made lowercase.
    user_email = models.EmailField(db_column='User_Email', max_length=255, blank=True, null=True)  # Field name made lowercase.
    user_password = models.CharField(db_column='User_Password', max_length=15, blank=True, null=True)  # Field name made lowercase.
    email_use_ssl = models.BooleanField(db_column='EMAIL_USE_SSL',default=True)
    email_use_tls = models.BooleanField(db_column='EMAIL_USE_TLS',default=False)
    email_subject = models.CharField(db_column='Email_Subject', max_length=300, blank=True, null=True)  # Field name made lowercase.
    email_content = models.TextField(db_column='Email_Content', blank=True, null=True)  # Field name made lowercase.
    sms_content = models.TextField(db_column='Sms_Content', blank=True, null=True)  # Field name made lowercase.
    site_codeid =  models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, db_column='Site_Codeid',null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    
    class Meta:
        db_table = 'smtp_settings'
        unique_together = (('site_code'),)


    def __str__(self):
        return str(self.sender_name)


class MultiPricePolicy(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    item_class_code = models.CharField(db_column='Item_Class_Code', max_length=20)  # Field name made lowercase.
    cust_class_code = models.CharField(db_column='Cust_Class_Code', max_length=20)  # Field name made lowercase.
    disc_percent_limit = models.FloatField(db_column='Disc_Percent_Limit', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    
    class Meta:
        db_table = 'Multi_Price_Policy'

    def __str__(self):
        return str(self.cust_class_code)
    

class salesStaffChangeLog(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.CharField(db_column='sa_transacNo',  max_length=20, null=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code', max_length=20, null=True)  # Field name made lowercase.
    emp_code = models.CharField(db_column='Emp_Code', max_length=20, null=True)  # Field name made lowercase.
    ratio = models.FloatField(db_column='Ratio', null=True)  # Field name made lowercase.
    salesamt = models.FloatField(db_column='SalesAmt', null=True)  # Field name made lowercase.
    salescommpoints = models.FloatField(db_column='SalesCommPoints', blank=True, null=True)  # Field name made lowercase.
    newempcode = models.CharField(db_column='NewEmp_Code', max_length=20, null=True)  # Field name made lowercase.
    newratio = models.FloatField(db_column='NewRatio', null=True)  # Field name made lowercase.
    newsalesamt = models.FloatField(db_column='NewSalesAmt', null=True)  # Field name made lowercase.
    newsalescommpoints = models.FloatField(db_column='NewSalesCommPoints', blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='Dt_LineNo', null=True)  # Field name made lowercase.
    itemsite_code = models.CharField(db_column='itemsite_code', max_length=10, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'salesStaffChangeLog'

class serviceStaffChangeLog(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.CharField(db_column='sa_transacNo',  max_length=20, null=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code', max_length=20, null=True)  # Field name made lowercase.
    emp_code = models.CharField(db_column='Emp_Code', max_length=20, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    share_amt = models.FloatField(db_column='Share_Amt', blank=True, null=True)  # Field name made lowercase.
    work_amt = models.FloatField(db_column='Work_Amount', blank=True, null=True)
    newempcode = models.CharField(db_column='NewEmp_Code', max_length=20, null=True)  # Field name made lowercase.
    newamount = models.FloatField(db_column='NewAmount', blank=True, null=True)  # Field name made lowercase.
    newshareamt = models.FloatField(db_column='NewShare_Amt', blank=True, null=True)  # Field name made lowercase.
    newworkamt = models.FloatField(db_column='NewWork_Amount', blank=True, null=True)
    line_no = models.IntegerField(db_column='Line_No', null=True)  # Field name made lowercase.
    itemsite_code = models.CharField(db_column='itemsite_code', max_length=10, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'serviceStaffChangeLog'


class payModeChangeLog(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.CharField( max_length=20,blank=True,  null=True)
    paytype = models.CharField(max_length=30, blank=True, null=True)
    payamt = models.FloatField(blank=True, null=True)
    newpaytype = models.CharField(max_length=30, blank=True, null=True)
    newpayamt = models.FloatField(blank=True, null=True)
    taudid = models.ForeignKey('cl_table.PosTaud', on_delete=models.PROTECT, null=True)
    dt_lineno = models.IntegerField( null=True)
    itemsite_code = models.CharField(db_column='itemsite_code', max_length=10, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'payModeChangeLog'


class dateChangeLog(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(blank=True, null=True)
    new_date = models.DateTimeField(blank=True, null=True)
    haud_id = models.ForeignKey('cl_table.PosHaud', on_delete=models.PROTECT, null=True)
    logtime = models.DateTimeField(blank=True, null=True, default=timezone.now, editable=False)
    itemsite_code = models.CharField(db_column='itemsite_code', max_length=10, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'dateChangeLog'

class POModel(models.Model):
    id = models.AutoField(db_column='PO_ID',primary_key=True)  # Field name made lowercase.
    po_number = models.CharField(db_column='PO_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    title = models.CharField(db_column='PO_Project', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    company = models.CharField(db_column='PO_Company', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contact_person = models.CharField(db_column='PO_ContactPerson', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    status = models.CharField(db_column='PO_Status', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    in_charge = models.CharField(db_column='PO_InCharge', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='PO_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_project = models.ForeignKey('custom.ProjectModel', on_delete=models.PROTECT, null=True)
    fk_quotation = models.ForeignKey('custom.QuotationModel', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(db_column='PO_Date',null=True)
    cust_id = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True) 
    
    class Meta:
        db_table = 'PurchaseOrder_List'


class TimeLogModel(models.Model):
    id = models.AutoField(db_column='TimeLog_ID',primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='TimeLog_Username', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    createormodify = models.CharField(db_column='CreateOrModify', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    fk_project = models.ForeignKey('custom.ProjectModel', on_delete=models.PROTECT, null=True)
    fk_quotation = models.ForeignKey('custom.QuotationModel', on_delete=models.PROTECT, null=True)
    fk_po = models.ForeignKey('custom.POModel', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(db_column='TimeLog_Date',auto_now_add=True,null=True)

    class Meta:
        db_table = 'TimeLog'

class ProjectModel(models.Model):
    id = models.AutoField(db_column='Project_ID',primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Project_Title', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    desc = models.CharField(db_column='Project_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Project_Status', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    customer_name = models.CharField(db_column='Customer_Name', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contact_person = models.CharField(db_column='Contact_Person', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contact_number = models.CharField(db_column='Contact_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='Project_Date',auto_now_add=True,null=True)
    sales_staff = models.CharField(db_column='sales_staff', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    admin_staff = models.CharField(db_column='admin_staff', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    operation_staff = models.CharField(db_column='operation_staff', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    cust_id = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True) 

    class Meta:
        db_table = 'Project_List'


class ActivityModel(models.Model):
    id = models.AutoField(db_column='Activity_ID',primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Activity_Title', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    name = models.CharField(db_column='Creator_Name', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    activity_type = models.CharField(db_column='Activity_Type', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_project = models.ForeignKey('custom.ProjectModel', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(db_column='Activity_Date',null=True)

    class Meta:
        db_table = 'Project_Activities'
           

class QuotationModel(models.Model):
    id = models.AutoField(db_column='Quotation_ID',primary_key=True)  # Field name made lowercase.
    quotation_number = models.CharField(db_column='Quotation_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Quotation_Project', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    company = models.CharField(db_column='Quotation_Company', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contact_person = models.CharField(db_column='Quotation_ContactPerson', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Quotation_Status', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    validity = models.CharField(db_column='Quotation_Validity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    terms = models.CharField(db_column='Quotation_Terms', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    in_charge = models.CharField(db_column='Quotation_InCharge', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Quotation_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    footer = models.CharField(db_column='Quotation_Footer', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_project = models.ForeignKey('custom.ProjectModel', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(db_column='Quotation_Date',null=True)
    cust_id = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True)
    currency_id =  models.ForeignKey('custom.Currencytable', on_delete=models.PROTECT, null=True)
    revision = models.IntegerField(db_column='revision', blank=True,  null=True)
    rev_quoteno = models.CharField(db_column='rev_quoteno', blank=True, max_length = 255, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Quotation_List'
    

class ManualInvoiceModel(models.Model):
    id = models.AutoField(db_column='ManualInvoice_ID',primary_key=True)  # Field name made lowercase.
    manualinv_number = models.CharField(db_column='ManualInvoice_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    title = models.CharField(db_column='ManualInvoice_Project', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    company = models.CharField(db_column='ManualInvoice_Company', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contact_person = models.CharField(db_column='ManualInvoice_ContactPerson', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    status = models.CharField(db_column='ManualInvoice_Status', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    validity = models.CharField(db_column='ManualInvoice_Validity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    terms = models.CharField(db_column='ManualInvoice_Terms', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    in_charge = models.CharField(db_column='ManualInvoice_InCharge', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='ManualInvoice_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    footer = models.CharField(db_column='ManualInvoice_Footer', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_project = models.ForeignKey('custom.ProjectModel', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(db_column='ManualInvoice_Date',null=True)
    sa_transacno_ref = models.CharField(max_length=255, null=True)
    cust_id = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True)
    currency_id =  models.ForeignKey('custom.Currencytable', on_delete=models.PROTECT, null=True)
    quotation_number = models.CharField(db_column='Quotation_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
   
    class Meta:
        db_table = 'ManualInvoice_List'


class WorkOrderInvoiceModel(models.Model):
    id = models.AutoField(db_column='WorkOrderInvoice_ID',primary_key=True)  # Field name made lowercase.
    workorderinv_number = models.CharField(db_column='WorkOrderInvoice_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    title = models.CharField(db_column='WorkOrderInvoice_Project', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    company = models.CharField(db_column='WorkOrderInvoice_Company', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contact_person = models.CharField(db_column='WorkOrderInvoice_ContactPerson', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    status = models.CharField(db_column='WorkOrderInvoice_Status', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    validity = models.CharField(db_column='WorkOrderInvoice_Validity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    terms = models.CharField(db_column='WorkOrderInvoice_Terms', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    in_charge = models.CharField(db_column='WorkOrderInvoice_InCharge', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='WorkOrderInvoice_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    footer = models.CharField(db_column='WorkOrderInvoice_Footer', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_project = models.ForeignKey('custom.ProjectModel', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(db_column='WorkOrderInvoice_Date',null=True)
    sa_transacno_ref = models.CharField(max_length=255, null=True)
    cust_id = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True) 
    
    class Meta:
        db_table = 'WorkOrderInvoice_List'
            
class DeliveryOrderModel(models.Model):
    id = models.AutoField(db_column='DeliveryOrder_ID',primary_key=True)  # Field name made lowercase.
    do_number = models.CharField(db_column='Do_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Do_Project', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    company = models.CharField(db_column='Do_Company', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contact_person = models.CharField(db_column='Do_ContactPerson', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Do_Status', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    validity = models.CharField(db_column='Do_Validity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    terms = models.CharField(db_column='Do_Terms', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    in_charge = models.CharField(db_column='Do_InCharge', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Do_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    footer = models.CharField(db_column='Do_Footer', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_project = models.ForeignKey('custom.ProjectModel', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(db_column='Do_Date',null=True)
    fk_workorder = models.ForeignKey('custom.WorkOrderInvoiceModel', on_delete=models.PROTECT, null=True)
    cust_id = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True) 

    class Meta:
        db_table = 'DeliveryOrder_List'
        


class QuotationAddrModel(models.Model):
    id = models.AutoField(db_column='Quotation_Addr_ID',primary_key=True)  # Field name made lowercase.
    billto = models.CharField(db_column='Quotation_Bill_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr1 = models.CharField(db_column='Quotation_Bill_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr2 = models.CharField(db_column='Quotation_Bill_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr3 = models.CharField(db_column='Quotation_Bill_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_postalcode = models.CharField(db_column='Quotation_Bill_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_city = models.CharField(db_column='Quotation_Bill_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_state = models.CharField(db_column='Quotation_Bill_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_country = models.CharField(db_column='Quotation_Bill_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    shipto = models.CharField(db_column='Quotation_Ship_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr1 = models.CharField(db_column='Quotation_Ship_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr2 = models.CharField(db_column='Quotation_Ship_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr3 = models.CharField(db_column='Quotation_Ship_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_postalcode = models.CharField(db_column='Quotation_Ship_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_city = models.CharField(db_column='Quotation_Ship_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_state = models.CharField(db_column='Quotation_Ship_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_country = models.CharField(db_column='Quotation_Ship_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_quotation = models.ForeignKey('custom.QuotationModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'Quotation_Address'

class ManualInvoiceAddrModel(models.Model):
    id = models.AutoField(db_column='ManualInvoice_Addr_ID',primary_key=True)  # Field name made lowercase.
    billto = models.CharField(db_column='ManualInvoice_Bill_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr1 = models.CharField(db_column='ManualInvoice_Bill_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr2 = models.CharField(db_column='ManualInvoice_Bill_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr3 = models.CharField(db_column='ManualInvoice_Bill_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_postalcode = models.CharField(db_column='ManualInvoice_Bill_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_city = models.CharField(db_column='ManualInvoice_Bill_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_state = models.CharField(db_column='ManualInvoice_Bill_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_country = models.CharField(db_column='ManualInvoice_Bill_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    shipto = models.CharField(db_column='ManualInvoice_Ship_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr1 = models.CharField(db_column='ManualInvoice_Ship_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr2 = models.CharField(db_column='ManualInvoice_Ship_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr3 = models.CharField(db_column='ManualInvoice_Ship_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_postalcode = models.CharField(db_column='ManualInvoice_Ship_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_city = models.CharField(db_column='ManualInvoice_Ship_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_state = models.CharField(db_column='ManualInvoice_Ship_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_country = models.CharField(db_column='ManualInvoice_Ship_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_manualinvoice = models.ForeignKey('custom.ManualInvoiceModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'ManualInvoice_Address'        

class WorkOrderInvoiceAddrModel(models.Model):
    id = models.AutoField(db_column='WorkOrderInvoice_Addr_ID',primary_key=True)  # Field name made lowercase.
    billto = models.CharField(db_column='WorkOrderInvoice_Bill_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr1 = models.CharField(db_column='WorkOrderInvoice_Bill_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr2 = models.CharField(db_column='WorkOrderInvoice_Bill_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr3 = models.CharField(db_column='WorkOrderInvoice_Bill_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_postalcode = models.CharField(db_column='WorkOrderInvoice_Bill_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_city = models.CharField(db_column='WorkOrderInvoice_Bill_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_state = models.CharField(db_column='WorkOrderInvoice_Bill_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_country = models.CharField(db_column='WorkOrderInvoice_Bill_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    shipto = models.CharField(db_column='WorkOrderInvoice_Ship_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr1 = models.CharField(db_column='WorkOrderInvoice_Ship_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr2 = models.CharField(db_column='WorkOrderInvoice_Ship_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr3 = models.CharField(db_column='WorkOrderInvoice_Ship_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_postalcode = models.CharField(db_column='WorkOrderInvoice_Ship_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_city = models.CharField(db_column='WorkOrderInvoice_Ship_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_state = models.CharField(db_column='WorkOrderInvoice_Ship_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_country = models.CharField(db_column='WorkOrderInvoice_Ship_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_workorderinvoice = models.ForeignKey('custom.WorkOrderInvoiceModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'WorkOrderInvoice_Address'        
    
class DeliveryOrderAddrModel(models.Model):
    id = models.AutoField(db_column='Do_Addr_ID',primary_key=True)  # Field name made lowercase.
    billto = models.CharField(db_column='Do_Bill_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr1 = models.CharField(db_column='Do_Bill_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr2 = models.CharField(db_column='Do_Bill_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr3 = models.CharField(db_column='Do_Bill_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_postalcode = models.CharField(db_column='Do_Bill_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_city = models.CharField(db_column='Do_Bill_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_state = models.CharField(db_column='Do_Bill_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_country = models.CharField(db_column='Do_Bill_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    shipto = models.CharField(db_column='Do_Ship_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr1 = models.CharField(db_column='Do_Ship_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr2 = models.CharField(db_column='Do_Ship_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr3 = models.CharField(db_column='Do_Ship_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_postalcode = models.CharField(db_column='Do_Ship_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_city = models.CharField(db_column='Do_Ship_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_state = models.CharField(db_column='Do_Ship_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_country = models.CharField(db_column='Do_Ship_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_deliveryorder = models.ForeignKey('custom.DeliveryOrderModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'DeliveryOrder_Address'
    

class POAddrModel(models.Model):
    id = models.AutoField(db_column='PO_Addr_ID',primary_key=True)  # Field name made lowercase.
    billto = models.CharField(db_column='PO_Bill_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr1 = models.CharField(db_column='PO_Bill_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr2 = models.CharField(db_column='PO_Bill_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_addr3 = models.CharField(db_column='PO_Bill_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_postalcode = models.CharField(db_column='PO_Bill_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_city = models.CharField(db_column='PO_Bill_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_state = models.CharField(db_column='PO_Bill_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    bill_country = models.CharField(db_column='PO_Bill_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    shipto = models.CharField(db_column='PO_Ship_To', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr1 = models.CharField(db_column='PO_Ship_Addr1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr2 = models.CharField(db_column='PO_Ship_Addr2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_addr3 = models.CharField(db_column='PO_Ship_Addr3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_postalcode = models.CharField(db_column='PO_Ship_PostalCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_city = models.CharField(db_column='PO_Ship_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_state = models.CharField(db_column='PO_Ship_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ship_country = models.CharField(db_column='PO_Ship_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_po = models.ForeignKey('custom.POModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'PurchaseOrder_Address'
    

class QuotationDetailModel(models.Model):
    id = models.AutoField(db_column='Quotation_Detail_ID',primary_key=True)  # Field name made lowercase.
    q_shipcost = models.CharField(db_column='Quotation_ShipCost', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_discount = models.CharField(db_column='Quotation_Discount', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_discpercent = models.FloatField(default=0.0,  null=True)
    q_taxes = models.CharField(db_column='Quotation_Taxes', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_total = models.CharField(db_column='Quotation_Total', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_quotation = models.ForeignKey('custom.QuotationModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'Quotation_Detail'

class QuotationPayment(models.Model):
    id = models.AutoField(db_column='id',primary_key=True)  # Field name made lowercase.
    payment_schedule = models.CharField(db_column='payment_schedule', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    payment_term = models.CharField(db_column='payment_term', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_quotation = models.ForeignKey('custom.QuotationModel', on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = 'Quotation_Payment'
                

class ManualInvoiceDetailModel(models.Model):
    id = models.AutoField(db_column=' ManualInvoice_Detail_ID',primary_key=True)  # Field name made lowercase.
    q_shipcost = models.CharField(db_column=' ManualInvoice_ShipCost', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_discount = models.CharField(db_column=' ManualInvoice_Discount', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_discpercent = models.FloatField(default=0.0,  null=True)
    q_taxes = models.CharField(db_column='ManualInvoice_Taxes', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_total = models.CharField(db_column=' ManualInvoice_Total', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_manualinvoice = models.ForeignKey('custom.ManualInvoiceModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'ManualInvoice_Detail'


class ManualInvoicePayment(models.Model):
    id = models.AutoField(db_column='id',primary_key=True)  # Field name made lowercase.
    payment_schedule = models.CharField(db_column='payment_schedule', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    payment_term = models.CharField(db_column='payment_term', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_manualinvoice = models.ForeignKey('custom.ManualInvoiceModel', on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = 'ManualInvoice_Payment'
      
            

class WorkOrderInvoiceDetailModel(models.Model):
    id = models.AutoField(db_column='WorkOrderInvoice_Detail_ID',primary_key=True)  # Field name made lowercase.
    q_shipcost = models.CharField(db_column=' WorkOrderInvoice_ShipCost', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_discount = models.CharField(db_column=' WorkOrderInvoice_Discount', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_taxes = models.CharField(db_column='WorkOrderInvoice_Taxes', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_total = models.CharField(db_column=' WorkOrderInvoice_Total', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_workorderinvoice = models.ForeignKey('custom.WorkOrderInvoiceModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'WorkOrderInvoice_Detail'

class DeliveryOrderDetailModel(models.Model):
    id = models.AutoField(db_column='Do_Detail_ID',primary_key=True)  # Field name made lowercase.
    q_shipcost = models.CharField(db_column='Do_ShipCost', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_discount = models.CharField(db_column='Do_Discount', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_taxes = models.CharField(db_column='Do_Taxes', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    q_total = models.CharField(db_column='Do_Total', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_deliveryorder = models.ForeignKey('custom.DeliveryOrderModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'DeliveryOrder_Detail'


class PODetailModel(models.Model):
    id = models.AutoField(db_column='PO_Detail_ID',primary_key=True)  # Field name made lowercase.
    po_shipcost = models.CharField(db_column='PO_ShipCost', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    po_discount = models.CharField(db_column='PO_Discount', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    po_taxes = models.CharField(db_column='PO_Taxes', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    po_total = models.CharField(db_column='PO_Total', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_po = models.ForeignKey('custom.POModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'PurchaseOrder_Detail'
       

class QuotationItemModel(models.Model):
    id = models.AutoField(db_column='Quotation_Item_ID',primary_key=True)  # Field name made lowercase.
    quotation_quantity = models.CharField(db_column='Quotation_Item_Quantity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_unitprice = models.CharField(db_column='Quotation_Item_UnitPrice', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemremarks = models.CharField(db_column='Quotation_Item_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemcode = models.CharField(db_column='Quotation_Item_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemdesc = models.CharField(db_column='Quotation_Item_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_quotation = models.ForeignKey('custom.QuotationModel', on_delete=models.PROTECT, null=True, default=1)
    discount_percent = models.FloatField(default=0.0,  null=True)
    discount_amt = models.FloatField(default=0.0,  null=True)
    # discount_price = models.FloatField(default=0.0,  null=True)
    # additional_discount = models.FloatField( null=True,default=0.0)
    # additional_discountamt = models.FloatField( null=True,default=0.0)
    # trans_amt = models.FloatField(default=0.0,  null=True)
    # disc_reason = models.ManyToManyField('custom.PaymentRemarks', blank=True)
    # discreason_txt = models.CharField(max_length=500,  null=True, blank=True)  # Field name made lowercase.
    # pos_disc = models.ManyToManyField('custom.PosDiscQuant', blank=True)
    # auto = models.BooleanField(default=True)
  

    class Meta:
        db_table = 'Quotation_Item'

class ManualInvoiceItemModel(models.Model):
    id = models.AutoField(db_column='ManualInvoice_Item_ID',primary_key=True)  # Field name made lowercase.
    quotation_quantity = models.CharField(db_column='ManualInvoice_Item_Quantity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_unitprice = models.CharField(db_column='ManualInvoice_Item_UnitPrice', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemremarks = models.CharField(db_column='ManualInvoice_Item_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemcode = models.CharField(db_column='ManualInvoice_Item_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemdesc = models.CharField(db_column='ManualInvoice_Item_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_manualinvoice = models.ForeignKey('custom.ManualInvoiceModel', on_delete=models.PROTECT, null=True, default=1)
    discount_percent = models.FloatField(default=0.0,  null=True)
    discount_amt = models.FloatField(default=0.0,  null=True)

    class Meta:
        db_table = 'ManualInvoice_Item'

class WorkOrderInvoiceItemModel(models.Model):
    id = models.AutoField(db_column='WorkOrderInvoice_Item_ID',primary_key=True)  # Field name made lowercase.
    quotation_quantity = models.CharField(db_column='WorkOrderInvoice_Item_Quantity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_unitprice = models.CharField(db_column='WorkOrderInvoice_Item_UnitPrice', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemremarks = models.CharField(db_column='WorkOrderInvoice_Item_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemcode = models.CharField(db_column='WorkOrderInvoice_Item_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemdesc = models.CharField(db_column='WorkOrderInvoice_Item_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_workorderinvoice = models.ForeignKey('custom.WorkOrderInvoiceModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'WorkOrderInvoice_Item'

class DeliveryOrderItemModel(models.Model):
    id = models.AutoField(db_column='Do_Item_ID',primary_key=True)  # Field name made lowercase.
    quotation_quantity = models.CharField(db_column='Do_Item_Quantity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_unitprice = models.CharField(db_column='Do_Item_UnitPrice', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemremarks = models.CharField(db_column='Do_Item_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemcode = models.CharField(db_column='Do_Item_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemdesc = models.CharField(db_column='Do_Item_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_deliveryorder = models.ForeignKey('custom.DeliveryOrderModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'DeliveryOrder_Item'

            
class POItemModel(models.Model):
    id = models.AutoField(db_column='PO_Item_ID',primary_key=True)  # Field name made lowercase.
    po_quantity = models.CharField(db_column='PO_Item_Quantity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    po_unitprice = models.CharField(db_column='PO_Item_UnitPrice', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    po_itemremarks = models.CharField(db_column='PO_Item_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    po_itemcode = models.CharField(db_column='PO_Item_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    po_itemdesc = models.CharField(db_column='PO_Item_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_po = models.ForeignKey('custom.POModel', on_delete=models.PROTECT, null=True, default=1)

    class Meta:
        db_table = 'PurchaseOrder_Item'

class DropdownModel(models.Model):
    id = models.AutoField(db_column='Dropdown_ID',primary_key=True)  # Field name made lowercase.
    dropdown_item = models.CharField(db_column='Dropdown_Item', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    dropdown_desc = models.CharField(db_column='Dropdown_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'Dropdown_List'
    

    

# class POModel(models.Model):
#     PO_ID = models.AutoField(db_column='PO_ID',primary_key=True)  # Field name made lowercase.
#     PO_NO = models.CharField(db_column='PO_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     ItemSite_Code = models.CharField(db_column='ItemSite_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     SUPP_Code = models.CharField(db_column='SUPP_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_REF = models.CharField(db_column='PO_REF', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_User = models.CharField(db_column='PO_User', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_DATE = models.DateTimeField(db_column='PO_DATE',null=True)
#     PO_STATUS = models.CharField(db_column='PO_STATUS', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_TTQTY = models.FloatField(db_column='PO_TTQTY', blank=True,  null=True)  # Field name made lowercase.
#     PO_TTFOC = models.FloatField(db_column='PO_TTFOC', blank=True, null=True)  # Field name made lowercase.
#     PO_TTDISC = models.FloatField(db_column='PO_TTDISC', blank=True,null=True)  # Field name made lowercase.
#     PO_TTAMT = models.FloatField(db_column='PO_TTAMT', blank=True, null=True)  # Field name made lowercase.
#     PO_ATTN = models.CharField(db_column='PO_ATTN', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_REMK1 = models.CharField(db_column='PO_REMK1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_REMK2 = models.CharField(db_column='PO_REMK2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_BNAME = models.CharField(db_column='PO_BNAME', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_BADDR1 = models.CharField(db_column='PO_BADDR1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_BADDR2 = models.CharField(db_column='PO_BADDR2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_BADDR3 = models.CharField(db_column='PO_BADDR3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_BPOSTCODE = models.CharField(db_column='PO_BPOSTCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_BSTATE = models.CharField(db_column='PO_BSTATE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_BCITY = models.CharField(db_column='PO_BCITY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_BCOUNTRY = models.CharField(db_column='PO_BCOUNTRY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_DADDR1 = models.CharField(db_column='PO_DADDR1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_DADDR2 = models.CharField(db_column='PO_DADDR2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_DADDR3 = models.CharField(db_column='PO_DADDR3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_DPOSTCODE = models.CharField(db_column='PO_DPOSTCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_DSTATE = models.CharField(db_column='PO_DSTATE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_DCITY = models.CharField(db_column='PO_DCITY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_DCOUNTRY = models.CharField(db_column='PO_DCOUNTRY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_CANCELQTY = models.FloatField(db_column='PO_CANCELQTY', blank=True,  null=True)  # Field name made lowercase.
#     PO_RECSTATUS = models.CharField(db_column='PO_RECSTATUS', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PO_RECEXPECT = models.DateTimeField(db_column='PO_RECEXPECT',null=True)
#     PO_RECTTL = models.FloatField(db_column='PO_RECTTL', blank=True,  null=True)  # Field name made lowercase.
#     PO_TIME = models.DateTimeField(db_column='PO_TIME',null=True)
#     REQ_NO = models.CharField(db_column='REQ_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     contactPerson = models.CharField(db_column='contactPerson', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     terms = models.CharField(db_column='terms', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     IsApproved = models.IntegerField(db_column='IsApproved', blank=True,null=True)  # Field name made lowercase.
#     PersonApproved = models.CharField(db_column='PersonApproved', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     DO_NO = models.CharField(db_column='DO_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    

#     class Meta:
#         db_table = 'PO'
    
# class PODetailModel(models.Model):
#     PO_ID = models.AutoField(db_column='PO_ID',primary_key=True)  # Field name made lowercase.
#     POD_ID = models.IntegerField(db_column='POD_ID', blank=True, null=True)  # Field name made lowercase.
#     ITEMSITE_CODE = models.CharField(db_column='ITEMSITE_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     STATUS = models.CharField(db_column='STATUS', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     POD_ITEMCODE = models.CharField(db_column='POD_ITEMCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     POD_ITEMDESC = models.CharField(db_column='POD_ITEMDESC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     POD_ITEMPRICE = models.FloatField(db_column='POD_ITEMPRICE', blank=True,  null=True)  # Field name made lowercase.
#     POD_QTY = models.IntegerField(db_column='POD_QTY', blank=True,  null=True)  # Field name made lowercase.
#     POD_FOCQTY = models.IntegerField(db_column='POD_FOCQTY', blank=True,  null=True)  # Field name made lowercase.
#     POD_TTLQTY = models.IntegerField(db_column='POD_TTLQTY', blank=True, null=True)  # Field name made lowercase.
#     POD_PRICE = models.FloatField(db_column='POD_PRICE', blank=True,  null=True)  # Field name made lowercase.
#     POD_DISCPER = models.FloatField(db_column='POD_DISCPER', blank=True, null=True)  # Field name made lowercase.
#     POD_DISCAMT = models.FloatField(db_column='POD_DISCAMT', blank=True, null=True)  # Field name made lowercase.
#     POD_AMT = models.FloatField(db_column='POD_AMT', blank=True,  null=True)  # Field name made lowercase.
#     POD_RECQTY = models.IntegerField(db_column='POD_RECQTY', blank=True,  null=True)  # Field name made lowercase.
#     POD_CANCELQTY = models.IntegerField(db_column='POD_CANCELQTY', blank=True, null=True)  # Field name made lowercase.
#     POD_OUTQTY = models.IntegerField(db_column='POD_OUTQTY', blank=True,  null=True)  # Field name made lowercase.
#     POD_DATE = models.DateTimeField(db_column='POD_DATE',null=True)
#     POD_TIME = models.DateTimeField(db_column='POD_TIME',null=True)
#     BrandCode = models.CharField(db_column='BrandCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     BrandName = models.CharField(db_column='BrandName', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     LineNumber = models.IntegerField(db_column='LineNumber', blank=True,  null=True)  # Field name made lowercase.
#     PO_No = models.CharField(db_column='PO_No', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     PostStatus = models.IntegerField(db_column='PostStatus', blank=True, null=True)  # Field name made lowercase.
#     IsApproved = models.IntegerField(db_column='IsApproved', blank=True,  null=True)  # Field name made lowercase.
#     PersonApproved = models.CharField(db_column='PersonApproved', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
#     POD_APPQTY = models.IntegerField(db_column='POD_APPQTY', blank=True, null=True)  # Field name made lowercase.
    
#     class Meta:
#         db_table = 'PO_DETAIL'

class POApprovalModel(models.Model):
    POAPP_ID = models.AutoField(db_column='POAPP_ID',primary_key=True)  # Field name made lowercase.
    PO_No = models.CharField(db_column='PO_No', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    GRN_No = models.CharField(db_column='GRN_No', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ITEMSITE_CODE = models.CharField(db_column='ITEMSITE_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STATUS = models.CharField(db_column='STATUS', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    POAPP_ITEMCODE = models.IntegerField(db_column='POAPP_ITEMCODE', blank=True,  null=True)  # Field name made lowercase.
    POAPP_ITEMDESC = models.CharField(db_column='POAPP_ITEMDESC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    POAPP_ITEMPRICE = models.FloatField(db_column='POAPP_ITEMPRICE', blank=True, null=True)  # Field name made lowercase.
    POAPP_QTY = models.IntegerField(db_column='POAPP_QTY', blank=True,  null=True)  # Field name made lowercase.
    POAPP_TTLQTY = models.IntegerField(db_column='POAPP_TTLQTY', blank=True,  null=True)  # Field name made lowercase.
    POAPP_AMT = models.FloatField(db_column='POAPP_AMT', blank=True,null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'PO_Approval'



class DOModel(models.Model):
    DO_ID = models.AutoField(db_column='DO_ID',primary_key=True)  # Field name made lowercase.
    DO_NO = models.CharField(db_column='DO_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Code = models.CharField(db_column='ItemSite_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SUPP_Code = models.CharField(db_column='SUPP_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_REF = models.CharField(db_column='DO_REF', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_User = models.CharField(db_column='DO_User', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_DATE = models.DateTimeField(db_column='DO_DATE',null=True)
    DO_STATUS = models.CharField(db_column='DO_STATUS', blank=True, max_length = 255,default='', null=True)  # Field name made lowercase.
    DO_TTQTY = models.FloatField(db_column='DO_TTQTY', blank=True,  null=True)  # Field name made lowercase.
    DO_TTFOC = models.FloatField(db_column='DO_TTFOC', blank=True,  null=True)  # Field name made lowercase.
    DO_TTDISC = models.FloatField(db_column='DO_TTDISC', blank=True,  null=True)  # Field name made lowercase.
    DO_TTAMT = models.FloatField(db_column='DO_TTAMT', blank=True,  null=True)  # Field name made lowercase.
    DO_ATTN = models.CharField(db_column='DO_ATTN', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_REMK1 = models.CharField(db_column='DO_REMK1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_REMK2 = models.CharField(db_column='DO_REMK2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_BNAME = models.CharField(db_column='DO_BNAME', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_BADDR1 = models.CharField(db_column='DO_BADDR1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_BADDR2 = models.CharField(db_column='DO_BADDR2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_BADDR3 = models.CharField(db_column='DO_BADDR3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_BPOSTCODE = models.CharField(db_column='DO_BPOSTCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_BSTATE = models.CharField(db_column='DO_BSTATE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_BCITY = models.CharField(db_column='DO_BCITY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_BCOUNTRY = models.CharField(db_column='DO_BCOUNTRY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_DADDR1 = models.CharField(db_column='DO_DADDR1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_DADDR2 = models.CharField(db_column='DO_DADDR2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_DADDR3 = models.CharField(db_column='DO_DADDR3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_DPOSTCODE = models.CharField(db_column='DO_DPOSTCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_DSTATE = models.CharField(db_column='DO_DSTATE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_DCITY = models.CharField(db_column='DO_DCITY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_DCOUNTRY = models.CharField(db_column='DO_DCOUNTRY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_CANCELQTY = models.FloatField(db_column='DO_CANCELQTY', blank=True,null=True)  # Field name made lowercase.
    DO_RECSTATUS = models.CharField(db_column='DO_RECSTATUS', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DO_RECEXPECT = models.DateTimeField(db_column='DO_RECEXPECT',null=True)
    DO_RECTTL = models.FloatField(db_column='DO_RECTTL', blank=True,  null=True)  # Field name made lowercase.
    DO_TIME = models.DateTimeField(db_column='DO_TIME',null=True)
    PO_NO = models.CharField(db_column='PO_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contactPerson = models.CharField(db_column='contactPerson', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    terms = models.CharField(db_column='terms', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'DO'
    
class DODetailModel(models.Model):
    DO_ID = models.AutoField(db_column='DO_ID',primary_key=True)  # Field name made lowercase.
    ITEMSITE_CODE = models.CharField(db_column='ITEMSITE_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STATUS = models.CharField(db_column='STATUS', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOD_ITEMCODE = models.CharField(db_column='DOD_ITEMCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOD_ITEMDESC = models.CharField(db_column='DOD_ITEMDESC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOD_ITEMPRICE = models.FloatField(db_column='DOD_ITEMPRICE', blank=True, null=True)  # Field name made lowercase.
    DOD_QTY = models.IntegerField(db_column='DOD_QTY', blank=True, null=True)  # Field name made lowercase.
    DOD_FOCQTY = models.IntegerField(db_column='DOD_FOCQTY', blank=True, null=True)  # Field name made lowercase.
    DOD_TTLQTY = models.IntegerField(db_column='DOD_TTLQTY', blank=True, null=True)  # Field name made lowercase.
    DOD_PRICE = models.FloatField(db_column='DOD_PRICE', blank=True, null=True)  # Field name made lowercase.
    DOD_DISCPER = models.FloatField(db_column='DOD_DISCPER', blank=True,  null=True)  # Field name made lowercase.
    DOD_DISCAMT = models.FloatField(db_column='DOD_DISCAMT', blank=True, null=True)  # Field name made lowercase.
    DOD_AMT = models.FloatField(db_column='DOD_AMT', blank=True,  null=True)  # Field name made lowercase.
    DOD_RECQTY = models.IntegerField(db_column='DOD_RECQTY', blank=True, null=True)  # Field name made lowercase.
    DOD_CANCELQTY = models.IntegerField(db_column='DOD_CANCELQTY', blank=True, null=True)  # Field name made lowercase.
    DOD_OUTQTY = models.IntegerField(db_column='DOD_OUTQTY', blank=True,null=True)  # Field name made lowercase.
    DOD_DATE = models.DateTimeField(db_column='DOD_DATE',null=True)
    DOD_TIME = models.DateTimeField(db_column='DOD_TIME',null=True)
    BrandCode = models.CharField(db_column='BrandCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BrandName = models.CharField(db_column='BrandName', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    LineNumber = models.IntegerField(db_column='LineNumber', blank=True, null=True)  # Field name made lowercase.
    DO_No = models.CharField(db_column='DO_No', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PostStatus = models.IntegerField(db_column='PostStatus', blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        db_table = 'DO_DETAIL'


class AuthoriseModel(models.Model):
    PW_ID = models.AutoField(db_column='PW_ID',primary_key=True)  # Field name made lowercase.
    PW_UserLogin = models.CharField(db_column='PW_UserLogin', blank=True, max_length = 255,  null=True)  # Field name made lowercase.
    flgdisc = models.IntegerField(db_column='flgdisc', blank=True,  null=True)  # Field name made lowercase.
    LEVEL_ItmID = models.IntegerField(db_column='LEVEL_ItmID', blank=True,  null=True)  # Field name made lowercase.
    Level_Desc = models.CharField(db_column='Level_Desc', blank=True, max_length = 255,  null=True)  # Field name made lowercase.
    Emp_Code = models.CharField(db_column='Emp_Code', blank=True, max_length = 255,  null=True)  # Field name made lowercase.
    flgPHY = models.IntegerField(db_column='flgPHY', blank=True,  null=True)  # Field name made lowercase.
    flgGRN = models.IntegerField(db_column='flgGRN', blank=True,  null=True)  # Field name made lowercase.
    flgADJ = models.IntegerField(db_column='flgADJ', blank=True,  null=True)  # Field name made lowercase.
    flgTFR = models.IntegerField(db_column='flgTFR', blank=True,  null=True)  # Field name made lowercase.
    flgStockUsageMemo = models.IntegerField(db_column='flgStockUsageMemo', blank=True,  default=1, null=True)  # Field name made lowercase.
    flgDelArt = models.IntegerField(db_column='flgDelArt', blank=True,  null=True)  # Field name made lowercase.
    flgMClock = models.IntegerField(db_column='flgMClock', blank=True,  null=True)  # Field name made lowercase.
    lallowFlgDelArt = models.IntegerField(db_column='lallowFlgDelArt', blank=True,  null=True)  # Field name made lowercase.
    flgopendrawer = models.IntegerField(db_column='flgopendrawer', blank=True,  null=True)  # Field name made lowercase.
    flgExchange = models.IntegerField(db_column='flgExchange', blank=True,  null=True)  # Field name made lowercase.
    flgRevTrm = models.IntegerField(db_column='flgRevTrm', blank=True,  null=True)  # Field name made lowercase.
    flgVoid = models.IntegerField(db_column='flgVoid', blank=True,  null=True)  # Field name made lowercase.
    flgRefund = models.IntegerField(db_column='flgRefund', blank=True,  null=True)  # Field name made lowercase.
    flgEmail = models.IntegerField(db_column='flgEmail', blank=True,  null=True)  # Field name made lowercase.
    flgCustAdd = models.IntegerField(db_column='flgCustAdd', blank=True,  null=True)  # Field name made lowercase.
    flgViewCost = models.IntegerField(db_column='flgViewCost', blank=True,  null=True)  # Field name made lowercase.
    flgFOC = models.IntegerField(db_column='flgFOC', blank=True,  null=True)  # Field name made lowercase.
    flgAppt = models.IntegerField(db_column='flgAppt', blank=True,  null=True)  # Field name made lowercase.
    flgExpire = models.IntegerField(db_column='flgExpire', blank=True,  null=True)  # Field name made lowercase.
    flgViewAth = models.IntegerField(db_column='flgViewAth', blank=True,  null=True)  # Field name made lowercase.
    flgAddAth = models.IntegerField(db_column='flgAddAth', blank=True,  null=True)  # Field name made lowercase.
    flgEditAth = models.IntegerField(db_column='flgEditAth', blank=True,  null=True)  # Field name made lowercase.
    flgRefundPP = models.IntegerField(db_column='flgRefundPP', blank=True,  null=True)  # Field name made lowercase.
    flgRefundCN = models.IntegerField(db_column='flgRefundCN', blank=True,  null=True)  # Field name made lowercase.
    flgAttn = models.IntegerField(db_column='flgAttn', blank=True,  null=True)  # Field name made lowercase.
    flgChangeExpiryDate = models.IntegerField(db_column='flgChangeExpiryDate', blank=True,  null=True)  # Field name made lowercase.
    flgOutletRequest = models.IntegerField(db_column='flgOutletRequest', blank=True,  null=True)  # Field name made lowercase.
    flgApptEditAth = models.IntegerField(db_column='flgApptEditAth', blank=True,  null=True)  # Field name made lowercase.
    flgChangeUnitPrice = models.IntegerField(db_column='flgChangeUnitPrice', blank=True,  null=True)  # Field name made lowercase.
    flgLuckyDraw = models.IntegerField(db_column='flgLuckyDraw', blank=True,  null=True)  # Field name made lowercase.
    flgOverideARStaff = models.IntegerField(db_column='flgOverideARStaff', blank=True,  null=True)  # Field name made lowercase.
    flgAccountInterface = models.IntegerField(db_column='flgAccountInterface', blank=True,  null=True)  # Field name made lowercase.
    flgVoidCurrentDay = models.IntegerField(db_column='flgVoidCurrentDay', blank=True,  null=True)  # Field name made lowercase.
    flgAllCom = models.IntegerField(db_column='flgAllCom', blank=True,  null=True)  # Field name made lowercase.
    flgAllowInsufficent = models.IntegerField(db_column='flgAllowInsufficent', blank=True,  null=True)  # Field name made lowercase.
    flgAllowCardUsage = models.IntegerField(db_column='flgAllowCardUsage', blank=True,  null=True)  # Field name made lowercase.
    flgAllowBlockAppointment = models.IntegerField(db_column='flgAllowBlockAppointment', blank=True,  null=True)  # Field name made lowercase.
    flgAllowTDExpiryService = models.IntegerField(db_column='flgAllowTDExpiryService', blank=True,  null=True)  # Field name made lowercase.
    flgAllDayEndSettlement = models.IntegerField(db_column='flgAllDayEndSettlement', blank=True,  null=True)  # Field name made lowercase.
    LEVEL_ItmIDid_id = models.IntegerField(db_column='LEVEL_ItmIDid_id', blank=True,  null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)
    flgCallDateChange = models.IntegerField(db_column='flgCallDateChange', blank=True,  null=True)  # Field name made lowercase.
    flgCallModule = models.IntegerField(db_column='flgCallModule', blank=True,  null=True)  # Field name made lowercase.
    flgGiftModule = models.IntegerField(db_column='flgGiftModule', blank=True,  null=True)  # Field name made lowercase.
    flgHMSetting = models.IntegerField(db_column='flgHMSetting', blank=True,  null=True)  # Field name made lowercase.
    flgSales = models.IntegerField(db_column='flgSales', blank=True,  null=True)  # Field name made lowercase.
    loginsite_id = models.IntegerField(db_column='loginsite_id', blank=True,  null=True)  # Field name made lowercase.
    PW_Isactive = models.IntegerField(db_column='PW_Isactive', blank=True,  default=1, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    user_id = models.IntegerField(db_column='user_id', blank=True,  null=True)  # Field name made lowercase.
    Emp_Codeid_id = models.IntegerField(db_column='Emp_Codeid_id', blank=True,  null=True)  # Field name made lowercase.
    is_reversal = models.BooleanField(db_column='Reversal', default=False)
    # reversal = models.IntegerField(db_column='reversal', blank=True,  null=True)  # Field name made lowercase.
    # POaccess = models.IntegerField(db_column='POaccess', blank=True,  null=True)  # Field name made lowercase.
    # POapprovalaccess = models.IntegerField(db_column='POapprovalaccess', blank=True,  null=True)  # Field name made lowercase.
    # POhqaccess = models.IntegerField(db_column='POhqaccess', blank=True,  null=True)  # Field name made lowercase.
    # DOaccess = models.IntegerField(db_column='DOaccess', blank=True,  null=True)  # Field name made lowercase.
    # GRNaccess = models.IntegerField(db_column='GRNaccess', blank=True,  null=True)  # Field name made lowercase.
    # VGRNaccess = models.IntegerField(db_column='VGRNaccess', blank=True,  null=True)  # Field name made lowercase.
    # TFRTaccess = models.IntegerField(db_column='TFRTaccess', blank=True,  null=True)  # Field name made lowercase.
    # TFRFaccess = models.IntegerField(db_column='TFRFaccess', blank=True,  null=True)  # Field name made lowercase.
    # ADJaccess = models.IntegerField(db_column='ADJaccess', blank=True,  null=True)  # Field name made lowercase.
    # PHYaccess = models.IntegerField(db_column='PHYaccess', blank=True,  null=True)  # Field name made lowercase.
    # SUMaccess = models.IntegerField(db_column='SUMaccess', blank=True,  null=True)  # Field name made lowercase.
    # Sheetaccess = models.IntegerField(db_column='Sheetaccess', blank=True,  null=True)  # Field name made lowercase.
    
    
    class Meta:
        db_table = 'FMSPW'
        managed = False


class ItemUOMPriceModel(models.Model):
    ID = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    ITEM_CODE = models.CharField(db_column='ITEM_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ITEM_UOM = models.CharField(db_column='ITEM_UOM', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    UOM_DESC = models.CharField(db_column='UOM_DESC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    UOM_UNIT = models.FloatField(db_column='UOM_UNIT', blank=True,  null=True)  # Field name made lowercase.
    ITEM_UOM2 = models.CharField(db_column='ITEM_UOM2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    UOM2_DESC = models.CharField(db_column='UOM2_DESC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ITEM_PRICE = models.FloatField(db_column='ITEM_PRICE', blank=True,  null=True)  # Field name made lowercase.
    ITEM_COST = models.FloatField(db_column='ITEM_COST', blank=True,  null=True)  # Field name made lowercase.
    MIN_MARGIN = models.FloatField(db_column='MIN_MARGIN', blank=True,  null=True)  # Field name made lowercase.
    IsActive = models.IntegerField(db_column='IsActive', blank=True, default=1, null=True)  # Field name made lowercase.
    Item_UOMPrice_SEQ = models.FloatField(db_column='Item_UOMPrice_SEQ', blank=True, null=True)  # Field name made lowercase.
    Delete_User = models.CharField(db_column='Delete_User', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Delete_DATE = models.DateTimeField(db_column='Delete_DATE',null=True)
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)

    class Meta:
        db_table = 'ITEM_UOMPRICE'
        managed = False
        

class ItemBatchModel(models.Model):
    ID = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    ITEM_CODE = models.CharField(db_column='ITEM_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SITE_CODE = models.CharField(db_column='SITE_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BATCH_NO = models.CharField(db_column='BATCH_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    UOM = models.CharField(db_column='UOM', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    QTY = models.FloatField(db_column='QTY', blank=True, null=True)  # Field name made lowercase.
    EXP_DATE = models.DateTimeField(db_column='EXP_DATE',null=True)
    BATCH_COST = models.FloatField(db_column='BATCH_COST', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)
    IsActive = models.IntegerField(db_column='IsActive', blank=True, default=1, null=True)  # Field name made lowercase.    
    

    class Meta:
        db_table = 'ITEM_BATCH'
        managed = False


class ItemBrandModel(models.Model):
    itm_id = models.AutoField(db_column='itm_id',primary_key=True)  # Field name made lowercase.
    itm_code = models.IntegerField(db_column='itm_code', blank=True, null=True)  # Field name made lowercase.
    itm_desc = models.CharField(db_column='itm_desc', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    itm_status = models.IntegerField(db_column='itm_status', blank=True, null=True)  # Field name made lowercase.
    ITM_SEQ = models.CharField(db_column='ITM_SEQ', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    PIC_PATH = models.CharField(db_column='PIC_PATH', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    Voucher_For_Sales = models.IntegerField(db_column='Voucher_For_Sales', blank=True,  default=1, null=True)  # Field name made lowercase.
    Voucher_Brand = models.IntegerField(db_column='Voucher_Brand', blank=True, default=1, null=True)  # Field name made lowercase.
    Retail_Product_Brand = models.IntegerField(db_column='Retail_Product_Brand', blank=True, default=1, null=True)  # Field name made lowercase.
    Prepaid_Brand = models.IntegerField(db_column='Prepaid_Brand', blank=True, default=1, null=True)  # Field name made lowercase.
    Process_Remark = models.CharField(db_column='Process_Remark', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    

    class Meta:
        db_table = 'Item_Brand'
        managed = False


class ItemRangeModel(models.Model):
    itm_id = models.AutoField(db_column='itm_id',primary_key=True)  # Field name made lowercase.
    itm_code = models.IntegerField(db_column='itm_code', blank=True,null=True)  # Field name made lowercase.
    itm_desc = models.CharField(db_column='itm_desc', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    itm_status = models.IntegerField(db_column='itm_status', blank=True,  null=True)  # Field name made lowercase.
    ITM_SEQ = models.CharField(db_column='ITM_SEQ', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    itm_brand = models.CharField(db_column='itm_brand', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    itm_Dept = models.CharField(db_column='itm_Dept', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    isProduct = models.IntegerField(db_column='isProduct', blank=True,  null=True)  # Field name made lowercase.
    PIC_PATH = models.CharField(db_column='PIC_PATH', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    Prepaid_For_Product = models.IntegerField(db_column='Prepaid_For_Product', blank=True,  default=1, null=True)  # Field name made lowercase.
    Prepaid_For_Service = models.IntegerField(db_column='Prepaid_For_Service', blank=True,default=1, null=True)  # Field name made lowercase.
    Prepaid_For_All = models.IntegerField(db_column='Prepaid_For_All', blank=True, default=1, null=True)  # Field name made lowercase.
    IsService = models.IntegerField(db_column='IsService', blank=True, default=1, null=True)  # Field name made lowercase.
    IsVoucher = models.IntegerField(db_column='IsVoucher', blank=True, default=1, null=True)  # Field name made lowercase.
    IsPrepaid = models.IntegerField(db_column='IsPrepaid', blank=True, default=1, null=True)  # Field name made lowercase.
    IsCompound = models.IntegerField(db_column='IsCompound', blank=True, default=1, null=True)  # Field name made lowercase.
    Process_Remark = models.CharField(db_column='Process_Remark', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)
    itm_Deptid_id = models.IntegerField(db_column='itm_Deptid_id', blank=True, default=1, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    

    class Meta:
        db_table = 'Item_Range'
        managed = False

class ItemDeptModel(models.Model):
    itm_id = models.AutoField(db_column='itm_id',primary_key=True)  # Field name made lowercase.
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_status = models.BooleanField(default=True)
    itm_seq = models.IntegerField(db_column='ITM_SEQ', blank=True, null=True)  # Field name made lowercase.
    process_remark = models.CharField(db_column='Process_Remark', max_length=250, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_Dept'
        managed = False

class EmployeeListModel(models.Model):
    Emp_no = models.AutoField(db_column='Emp_no',primary_key=True)  # Field name made lowercase.
    Emp_code = models.CharField(db_column='Emp_code', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    Emp_name = models.CharField(db_column='Emp_name', blank=True, max_length = 255, null=True)  # Field name made lowercase.
    
    

    class Meta:
        db_table = 'Employee'
        managed = False

class SiteCodeModel(models.Model):
    ItemSite_ID = models.AutoField(db_column='ItemSite_ID',primary_key=True)  # Field name made lowercase.
    ItemSite_Code = models.CharField(db_column='ItemSite_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Desc = models.CharField(db_column='ItemSite_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Type = models.CharField(db_column='ItemSite_Type', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_PurchaseDept = models.CharField(db_column='Item_PurchaseDept', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Address = models.CharField(db_column='ItemSite_Address', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Postcode = models.CharField(db_column='ItemSite_Postcode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_City = models.CharField(db_column='ItemSite_City', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_State = models.CharField(db_column='ItemSite_State', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Country = models.CharField(db_column='ItemSite_Country', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Phone1 = models.CharField(db_column='ItemSite_Phone1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Phone2 = models.CharField(db_column='ItemSite_Phone2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Fax = models.CharField(db_column='ItemSite_Fax', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Email = models.CharField(db_column='ItemSite_Email', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_User = models.CharField(db_column='ItemSite_User', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ItemSite_Date = models.DateField(db_column='ItemSite_Date',null=True)
    ItemSite_Time = models.DateTimeField(db_column='ItemSite_Time',null=True)
    ItemSite_Isactive = models.IntegerField(db_column='ItemSite_Isactive', blank=True, null=True)  # Field name made lowercase.
    ITEMSITE_REFCODE = models.CharField(db_column='ITEMSITE_REFCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Site_Group = models.CharField(db_column='Site_Group', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    site_is_gst = models.BooleanField(db_column='SITE_IS_GST', null=True,default=False)  # Field name made lowercase.
    Account_Code = models.CharField(db_column='Account_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ClientIndex = models.IntegerField(db_column='ClientIndex', blank=True, null=True)  # Field name made lowercase.
    HeartBeat = models.DateTimeField(db_column='HeartBeat',null=True)
    SystemLog_MDPL_Update = models.IntegerField(db_column='SystemLog_MDPL_Update', blank=True, null=True)  # Field name made lowercase.
    geolink = models.CharField(db_column='geolink', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    weekdays_timing = models.CharField(db_column='weekdays_timing', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    weekend_timing = models.CharField(db_column='weekend_timing', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    holliday_timing = models.CharField(db_column='holliday_timing', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Closed_on = models.CharField(db_column='Closed_on', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    picpath = models.CharField(db_column='picpath', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Owner = models.CharField(db_column='Owner', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Site_Groupid_id = models.IntegerField(db_column='Site_Groupid_id', blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)
    pic_Path = models.CharField(db_column='pic_Path', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    QRCode = models.CharField(db_column='QRCode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Ratings = models.CharField(db_column='Ratings', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    siteDbConnectionUrl = models.CharField(db_column='siteDbConnectionUrl', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    skills_list = models.CharField(db_column='skills_list', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    ItemSite_Cityid_id = models.IntegerField(db_column='ItemSite_Cityid_id', blank=True, null=True)  # Field name made lowercase.
    ItemSite_Countryid_id = models.IntegerField(db_column='ItemSite_Countryid_id', blank=True, null=True)  # Field name made lowercase.
    ItemSite_Stateid_id = models.IntegerField(db_column='ItemSite_Stateid_id', blank=True, null=True)  # Field name made lowercase.
    ItemSite_Userid_id = models.IntegerField(db_column='ItemSite_Userid_id', blank=True,  null=True)  # Field name made lowercase.
    is_nric = models.IntegerField(db_column='Nric', blank=True, null=True)  # Field name made lowercase.
    is_automember = models.IntegerField(db_column='IsAutoMember', blank=True, null=True)  # Field name made lowercase.
    Invoice_TemplateName = models.CharField(db_column='Invoice_TemplateName', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    resource_count = models.CharField(db_column='resource_count', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    cell_duration = models.CharField(db_column='Cell_Duration', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    EndDay_Hour = models.CharField(db_column='EndDay_Hour', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    # Interval = models.CharField(db_column='Interval', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    StartDay_Hour = models.CharField(db_column='StartDay_Hour', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    # nric = models.IntegerField(db_column='nric', blank=True,  null=True)  # Field name made lowercase.
    url = models.CharField(db_column='url', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    is_dragappt = models.IntegerField(db_column='is_dragappt', blank=True, null=True)  # Field name made lowercase.
    is_empvalidate = models.IntegerField(db_column='is_empvalidate', blank=True, null=True)  # Field name made lowercase.
    # hq_only = models.IntegerField(db_column='hq_only', blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'Item_SiteList'
        managed = False

class ItemSupplyModel(models.Model):
    SPLY_ID = models.AutoField(db_column='SPLY_ID',primary_key=True)  # Field name made lowercase.
    SPLY_CODE = models.CharField(db_column='SPLY_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SUPPLYDESC = models.CharField(db_column='SUPPLYDESC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_DATE = models.DateTimeField(db_column='SPLY_DATE',null=True)
    SPLY_ATTN = models.CharField(db_column='SPLY_ATTN', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_IC = models.CharField(db_column='SPLY_IC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_TYPE = models.CharField(db_column='SPLY_TYPE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_ADDR1 = models.CharField(db_column='SPLY_ADDR1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_ADDR2 = models.CharField(db_column='SPLY_ADDR2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_ADDR3 = models.CharField(db_column='SPLY_ADDR3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_POSCD = models.CharField(db_column='SPLY_POSCD', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_STATE = models.CharField(db_column='SPLY_STATE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_CITY = models.CharField(db_column='SPLY_CITY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_CNTRY = models.CharField(db_column='SPLY_CNTRY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLYMADDR1 = models.CharField(db_column='SPLYMADDR1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLYMADDR2 = models.CharField(db_column='SPLYMADDR2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLYMADDR3 = models.CharField(db_column='SPLYMADDR3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLYMPOSCD = models.CharField(db_column='SPLYMPOSCD', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLYMSTATE = models.CharField(db_column='SPLYMSTATE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLYMCITY = models.CharField(db_column='SPLYMCITY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLYMCNTRY = models.CharField(db_column='SPLYMCNTRY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_TELNO = models.CharField(db_column='SPLY_TELNO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_FAXNO = models.CharField(db_column='SPLY_FAXNO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_REMK1 = models.CharField(db_column='SPLY_REMK1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_REMK2 = models.CharField(db_column='SPLY_REMK2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_REMK3 = models.CharField(db_column='SPLY_REMK3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_TERM = models.CharField(db_column='SPLY_TERM', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SPLY_LIMIT = models.IntegerField(db_column='SPLY_LIMIT', blank=True,  null=True)  # Field name made lowercase.
    SPLY_BAL = models.IntegerField(db_column='SPLY_BAL', blank=True, null=True)  # Field name made lowercase.
    SPLYACTIVE = models.IntegerField(db_column='SPLYACTIVE', blank=True,  null=True)  # Field name made lowercase.
    SPLY_COMM = models.IntegerField(db_column='SPLY_COMM', blank=True, null=True)  # Field name made lowercase.
    FIRST_NAME = models.CharField(db_column='FIRST_NAME', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    NETSEQ = models.CharField(db_column='NETSEQ', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    CREATE_USER = models.CharField(db_column='CREATE_USER', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    CREATE_DATE = models.DateTimeField(db_column='CREATE_DATE',auto_now_add=True,null=True)
    numberOfTotalPOs = models.CharField(db_column='numberOfTotalPOs', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    numberOfOpenPOs = models.CharField(db_column='numberOfOpenPOs', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    accountNumber = models.CharField(db_column='accountNumber', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'Item_Supply'






class StockModel(models.Model):
    Item_no = models.AutoField(db_column='Item_no',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='item_code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Itm_ICID = models.FloatField(db_column='Itm_ICID', blank=True, null=True)  # Field name made lowercase.
    Itm_Code = models.CharField(db_column='Itm_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_Div = models.CharField(db_column='Item_Div', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_Dept = models.CharField(db_column='Item_Dept', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_Class = models.CharField(db_column='Item_Class', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_Barcode = models.CharField(db_column='Item_Barcode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ONHAND_CST = models.FloatField(db_column='ONHAND_CST', blank=True,  null=True)  # Field name made lowercase.
    Item_Margin = models.FloatField(db_column='Item_Margin', blank=True, null=True)  # Field name made lowercase.
    item_isactive = models.IntegerField(db_column='item_isactive', blank=True, default=1, null=True)  # Field name made lowercase.
    Item_Name = models.CharField(db_column='Item_Name', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_abbc = models.CharField(db_column='Item_abbc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_Desc = models.CharField(db_column='Item_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    COST_PRICE = models.FloatField(db_column='COST_PRICE', blank=True,  null=True)  # Field name made lowercase.
    Item_Price = models.FloatField(db_column='Item_Price', blank=True,  null=True)  # Field name made lowercase.
    ONHAND_QTY = models.FloatField(db_column='ONHAND_QTY', blank=True,  null=True)  # Field name made lowercase.
    Itm_PromotionYN = models.CharField(db_column='Itm_PromotionYN', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Itm_Disc = models.FloatField(db_column='Itm_Disc', blank=True,  null=True)  # Field name made lowercase.
    Itm_Commission = models.FloatField(db_column='Itm_Commission', blank=True, null=True)  # Field name made lowercase.
    Item_Type = models.CharField(db_column='Item_Type', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Itm_Duration = models.FloatField(db_column='Itm_Duration', blank=True,null=True)  # Field name made lowercase.
    Item_Price2 = models.FloatField(db_column='Item_Price2', blank=True, null=True)  # Field name made lowercase.
    Item_Price3 = models.FloatField(db_column='Item_Price3', blank=True,  null=True)  # Field name made lowercase.
    Item_Price4 = models.FloatField(db_column='Item_Price4', blank=True,  null=True)  # Field name made lowercase.
    Item_Price5 = models.FloatField(db_column='Item_Price5', blank=True, null=True)  # Field name made lowercase.
    Itm_Remark = models.CharField(db_column='Itm_Remark', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Itm_Value = models.CharField(db_column='Itm_Value', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Itm_ExpireDate = models.DateTimeField(db_column='Itm_ExpireDate',null=True)
    Itm_Status = models.CharField(db_column='Itm_Status', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_minqty = models.IntegerField(db_column='item_minqty', blank=True,  null=True)  # Field name made lowercase.
    item_maxqty = models.IntegerField(db_column='item_maxqty', blank=True,  null=True)  # Field name made lowercase.
    item_OnHandCost = models.CharField(db_column='item_OnHandCost', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_Barcode1 = models.CharField(db_column='item_Barcode1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_Barcode2 = models.CharField(db_column='item_Barcode2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_Barcode3 = models.CharField(db_column='item_Barcode3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_marginamt = models.FloatField(db_column='item_marginamt', blank=True, null=True)  # Field name made lowercase.
    item_date = models.DateTimeField(db_column='item_date',auto_now_add=True,null=True)
    item_time = models.DateTimeField(db_column='item_time',auto_now_add=True,null=True)
    item_ModDate = models.DateTimeField(db_column='item_ModDate',auto_now=True,null=True)
    item_ModTime = models.DateTimeField(db_column='item_ModTime',auto_now=True,null=True)
    item_createuser = models.CharField(db_column='item_createuser', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_supp = models.CharField(db_column='item_supp', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_Parentcode = models.CharField(db_column='item_Parentcode', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_color = models.CharField(db_column='item_color', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_SizePack = models.CharField(db_column='item_SizePack', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_size = models.CharField(db_column='item_size', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_Season = models.CharField(db_column='item_Season', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_fabric = models.CharField(db_column='item_fabric', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_Brand = models.CharField(db_column='item_Brand', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    LSTPO_UCST = models.FloatField(db_column='LSTPO_UCST', blank=True, null=True)  # Field name made lowercase.
    LSTPO_NO = models.CharField(db_column='LSTPO_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    LSTPO_Date = models.DateTimeField(db_column='LSTPO_Date',auto_now_add=True,null=True)
    item_haveChild = models.IntegerField(db_column='item_haveChild', blank=True,  null=True)  # Field name made lowercase.
    Value_ApplyToChild = models.IntegerField(db_column='Value_ApplyToChild', blank=True,null=True)  # Field name made lowercase.
    Package_Disc = models.FloatField(db_column='Package_Disc', blank=True, null=True)  # Field name made lowercase.
    Have_Package_Disc = models.IntegerField(db_column='Have_Package_Disc', blank=True,  null=True)  # Field name made lowercase.
    PIC_Path = models.CharField(db_column='PIC_Path', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_FOC = models.IntegerField(db_column='Item_FOC', blank=True, null=True)  # Field name made lowercase.
    Item_UOM = models.CharField(db_column='Item_UOM', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    MIXBRAND = models.IntegerField(db_column='MIXBRAND', blank=True, null=True)  # Field name made lowercase.
    SERVICERETAIL = models.IntegerField(db_column='SERVICERETAIL', blank=True, null=True)  # Field name made lowercase.
    Item_Range = models.CharField(db_column='Item_Range', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Commissionable = models.IntegerField(db_column='Commissionable', blank=True,null=True)  # Field name made lowercase.
    Trading = models.IntegerField(db_column='Trading', blank=True,null=True)  # Field name made lowercase.
    Cust_Replenish_Days = models.CharField(db_column='Cust_Replenish_Days', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Cust_Advance_Days = models.CharField(db_column='Cust_Advance_Days', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SalesComm = models.CharField(db_column='SalesComm', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    WorkComm = models.CharField(db_column='WorkComm', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Reminder_Active = models.IntegerField(db_column='Reminder_Active', blank=True, null=True)  # Field name made lowercase.
    DiscLimit = models.FloatField(db_column='DiscLimit', blank=True,  null=True)  # Field name made lowercase.
    DiscTypeAmount = models.IntegerField(db_column='DiscTypeAmount', blank=True, null=True)  # Field name made lowercase.
    AutoCustDisc = models.IntegerField(db_column='AutoCustDisc', blank=True, null=True)  # Field name made lowercase.
    ReOrder_Active = models.IntegerField(db_column='ReOrder_Active', blank=True, null=True)  # Field name made lowercase.
    ReOrder_MinQty = models.FloatField(db_column='ReOrder_MinQty', blank=True, null=True)  # Field name made lowercase.
    Service_Expire_Active = models.IntegerField(db_column='Service_Expire_Active', blank=True,null=True)  # Field name made lowercase.
    Service_Expire_Month = models.FloatField(db_column='Service_Expire_Month', blank=True, null=True)  # Field name made lowercase.
    Treatment_Limit_Active = models.IntegerField(db_column='Treatment_Limit_Active', blank=True, null=True)  # Field name made lowercase.
    Treatment_Limit_Count = models.FloatField(db_column='Treatment_Limit_Count', blank=True,null=True)  # Field name made lowercase.
    LimitService_FlexiOnly = models.IntegerField(db_column='LimitService_FlexiOnly', blank=True, null=True)  # Field name made lowercase.
    SalesCommPoints = models.FloatField(db_column='SalesCommPoints', blank=True, null=True)  # Field name made lowercase.
    WorkCommPoints = models.FloatField(db_column='WorkCommPoints', blank=True, null=True)  # Field name made lowercase.
    Item_Price_Floor = models.FloatField(db_column='Item_Price_Floor', blank=True, null=True)  # Field name made lowercase.
    Voucher_Value = models.FloatField(db_column='Voucher_Value', blank=True, null=True)  # Field name made lowercase.
    Voucher_Value_Is_Amount = models.IntegerField(db_column='Voucher_Value_Is_Amount', blank=True, null=True)  # Field name made lowercase.
    Voucher_Valid_Period = models.CharField(db_column='Voucher_Valid_Period', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Prepaid_Value = models.FloatField(db_column='Prepaid_Value', blank=True,  null=True)  # Field name made lowercase.
    Prepaid_Sell_Amt = models.FloatField(db_column='Prepaid_Sell_Amt', blank=True, null=True)  # Field name made lowercase.
    Prepaid_Valid_Period = models.CharField(db_column='Prepaid_Valid_Period', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    MemberCardNoAccess = models.IntegerField(db_column='MemberCardNoAccess', blank=True, null=True)  # Field name made lowercase.
    Rpt_Code = models.CharField(db_column='Rpt_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    IS_GST = models.IntegerField(db_column='IS_GST', blank=True, null=True)  # Field name made lowercase.
    Account_Code = models.CharField(db_column='Account_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Stock_PIC_B = models.CharField(db_column='Stock_PIC_B', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    IS_OPEN_PREPAID = models.IntegerField(db_column='IS_OPEN_PREPAID', blank=True, null=True)  # Field name made lowercase.
    Appt_WD_Min = models.FloatField(db_column='Appt_WD_Min', blank=True,  null=True)  # Field name made lowercase.
    Service_Cost = models.FloatField(db_column='Service_Cost', blank=True,  null=True)  # Field name made lowercase.
    Service_Cost_Percent = models.IntegerField(db_column='Service_Cost_Percent', blank=True, null=True)  # Field name made lowercase.
    Account_Code_TD = models.CharField(db_column='Account_Code_TD', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    IS_ALLOW_FOC = models.IntegerField(db_column='IS_ALLOW_FOC', blank=True, null=True)  # Field name made lowercase.
    Vilidity_From_Date = models.DateTimeField(db_column='Vilidity_From_Date',null=True)
    Vilidity_To_date = models.DateTimeField(db_column='Vilidity_To_date',null=True)
    Vilidity_From_Time = models.DateTimeField(db_column='Vilidity_From_Time',null=True)
    Vilidity_To_Time = models.DateTimeField(db_column='Vilidity_To_Time',null=True)
    Prepaid_Disc_Type = models.CharField(db_column='Prepaid_Disc_Type', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Prepaid_Disc_Percent = models.FloatField(db_column='Prepaid_Disc_Percent', blank=True, null=True)  # Field name made lowercase.
    AutoProportion = models.IntegerField(db_column='AutoProportion', blank=True,  null=True)  # Field name made lowercase.
    Voucher_IsValid_Until_Date = models.IntegerField(db_column='Voucher_IsValid_Until_Date', blank=True, null=True)  # Field name made lowercase.
    Voucher_Valid_Until_Date = models.DateTimeField(db_column='Voucher_Valid_Until_Date',null=True)
    T1_TAX_CODE = models.CharField(db_column='T1_TAX_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    IS_HAVE_TAX = models.IntegerField(db_column='IS_HAVE_TAX', blank=True, null=True)  # Field name made lowercase.
    T2_TAX_CODE = models.CharField(db_column='T2_TAX_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Srv_Duration = models.FloatField(db_column='Srv_Duration', blank=True, null=True)  # Field name made lowercase.
    Voucher_Template_Name = models.CharField(db_column='Voucher_Template_Name', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_PingYing = models.CharField(db_column='Item_PingYing', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Process_Remark = models.CharField(db_column='Process_Remark', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)
    GST_Item_Code = models.CharField(db_column='GST_Item_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    isTnc = models.IntegerField(db_column='isTnc', blank=True, null=True)  # Field name made lowercase.
    postatus = models.IntegerField(db_column='postatus', blank=True, null=True)  # Field name made lowercase.
    SST_Item_Code = models.CharField(db_column='SST_Item_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    WorkCommHolder = models.CharField(db_column='WorkCommHolder', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_Classid_id = models.IntegerField(db_column='Item_Classid_id', blank=True, null=True)  # Field name made lowercase.
    Item_Deptid_id = models.IntegerField(db_column='Item_Deptid_id', blank=True,null=True)  # Field name made lowercase.
    Item_Divid_id = models.IntegerField(db_column='Item_Divid_id', blank=True,  null=True)  # Field name made lowercase.
    Item_Rangeid_id = models.IntegerField(db_column='Item_Rangeid_id', blank=True,  null=True)  # Field name made lowercase.
    Item_Typeid_id = models.IntegerField(db_column='Item_Typeid_id', blank=True,  null=True)  # Field name made lowercase.
    equipmentcost = models.FloatField(db_column='equipmentcost', blank=True, null=True)  # Field name made lowercase.
    Stock_PIC = models.CharField(db_column='Stock_PIC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    description = models.CharField(db_column='description', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    procedure = models.CharField(db_column='procedure', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    description = models.CharField(db_column='description', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    sutiable_for = models.CharField(db_column='sutiable_for', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    tax = models.FloatField(db_column='tax', blank=True,null=True)  # Field name made lowercase.
    treatment_details = models.CharField(db_column='treatment_details', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    printUom = models.CharField(db_column='printUom', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    MOQQty = models.FloatField(db_column='MOQQty', blank=True,  null=True)  # Field name made lowercase.
    printDesc = models.CharField(db_column='printDesc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    printLineNo = models.FloatField(db_column='printLineNo', blank=True, null=True)  # Field name made lowercase.
    pinyin = models.CharField(db_column='pinyin', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PIC_Path2 = models.CharField(db_column='PIC_Path2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PIC_Path3 = models.CharField(db_column='PIC_Path3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PIC_Path4 = models.CharField(db_column='PIC_Path4', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PIC_Path5 = models.CharField(db_column='PIC_Path5', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'Stock'
        managed = False
        

class StktrnModel(models.Model):
    ID = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    TRN_POST = models.DateTimeField(db_column='TRN_POST',auto_now_add=True,null=True)
    TRN_NO = models.FloatField(db_column='TRN_NO', blank=True, null=True)  # Field name made lowercase.
    TRN_DATE = models.DateTimeField(db_column='TRN_DATE',auto_now_add=True,null=True)
    POST_TIME = models.CharField(db_column='POST_TIME', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    APERIOD = models.FloatField(db_column='APERIOD', blank=True,null=True)  # Field name made lowercase.
    ITEMCODE = models.CharField(db_column='ITEMCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STORE_NO = models.CharField(db_column='STORE_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    TSTORE_NO = models.CharField(db_column='TSTORE_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    FSTORE_NO = models.CharField(db_column='FSTORE_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    TRN_DOCNO = models.CharField(db_column='TRN_DOCNO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    TRN_TYPE = models.CharField(db_column='TRN_TYPE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    TRN_DB_QTY = models.FloatField(db_column='TRN_DB_QTY', blank=True,  null=True)  # Field name made lowercase.
    TRN_CR_QTY = models.FloatField(db_column='TRN_CR_QTY', blank=True, null=True)  # Field name made lowercase.
    TRN_QTY = models.FloatField(db_column='TRN_QTY', blank=True,null=True)  # Field name made lowercase.
    TRN_BALQTY = models.FloatField(db_column='TRN_BALQTY', blank=True,  null=True)  # Field name made lowercase.
    TRN_BALCST = models.FloatField(db_column='TRN_BALCST', blank=True, null=True)  # Field name made lowercase.
    TRN_AMT = models.FloatField(db_column='TRN_AMT', blank=True, null=True)  # Field name made lowercase.
    TRN_COST = models.FloatField(db_column='TRN_COST', blank=True,  null=True)  # Field name made lowercase.
    TRN_REF = models.CharField(db_column='TRN_REF', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    HQ_UPDATE = models.IntegerField(db_column='HQ_UPDATE', blank=True, null=True)  # Field name made lowercase.
    LINE_NO = models.FloatField(db_column='LINE_NO', blank=True,  null=True)  # Field name made lowercase.
    Item_UOM = models.CharField(db_column='Item_UOM', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_Batch = models.CharField(db_column='Item_Batch', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Mov_Type = models.CharField(db_column='Mov_Type', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Item_Batch_Cost = models.FloatField(db_column='Item_Batch_Cost', blank=True,  null=True)  # Field name made lowercase.
    Stock_In = models.IntegerField(db_column='Stock_In', blank=True, null=True)  # Field name made lowercase.
    TRANS_PACKAGE_LINE_NO = models.FloatField(db_column='TRANS_PACKAGE_LINE_NO', blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    

    class Meta:
        db_table = 'Stktrn'
        managed = False
        

class MovHdrModel(models.Model):
    PO_ID = models.AutoField(db_column='PO_ID',primary_key=True)  # Field name made lowercase.
    DOC_NO = models.CharField(db_column='DOC_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    MOV_CODE = models.CharField(db_column='MOV_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    MOV_TYPE = models.CharField(db_column='MOV_TYPE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STORE_NO = models.CharField(db_column='STORE_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    FSTORE_NO = models.CharField(db_column='FSTORE_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    TSTORE_NO = models.CharField(db_column='TSTORE_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    SUPPLY_NO = models.CharField(db_column='SUPPLY_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_REF1 = models.CharField(db_column='DOC_REF1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_REF2 = models.CharField(db_column='DOC_REF2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ACC_CODE = models.CharField(db_column='ACC_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STAFF_NO = models.CharField(db_column='STAFF_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_LINES = models.FloatField(db_column='DOC_LINES', blank=True, null=True)  # Field name made lowercase.
    DOC_DATE = models.DateTimeField(db_column='DOC_DATE',auto_now_add=True,null=True)
    POST_DATE = models.DateTimeField(db_column='POST_DATE',auto_now_add=True,null=True)
    DOC_STATUS = models.FloatField(db_column='DOC_STATUS', blank=True, null=True)  # Field name made lowercase.
    DOC_TERM = models.CharField(db_column='DOC_TERM', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_TIME = models.FloatField(db_column='DOC_TIME', blank=True,  null=True)  # Field name made lowercase.
    DOC_QTY = models.FloatField(db_column='DOC_QTY', blank=True, null=True)  # Field name made lowercase.
    DOC_FOC = models.FloatField(db_column='DOC_FOC', blank=True, null=True)  # Field name made lowercase.
    DOC_DISC = models.FloatField(db_column='DOC_DISC', blank=True,  null=True)  # Field name made lowercase.
    DOC_AMT = models.FloatField(db_column='DOC_AMT', blank=True, null=True)  # Field name made lowercase.
    DOC_TRNSPT = models.FloatField(db_column='DOC_TRNSPT', blank=True, null=True)  # Field name made lowercase.
    DOC_TAX = models.FloatField(db_column='DOC_TAX', blank=True, null=True)  # Field name made lowercase.
    DOC_ATTN = models.CharField(db_column='DOC_ATTN', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_REMK1 = models.CharField(db_column='DOC_REMK1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_REMK2 = models.CharField(db_column='DOC_REMK2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_REMK3 = models.CharField(db_column='DOC_REMK3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_SHIP = models.DateTimeField(db_column='DOC_SHIP',null=True)
    BNAME = models.CharField(db_column='BNAME', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BADDR1 = models.CharField(db_column='BADDR1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BADDR2 = models.CharField(db_column='BADDR2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BADDR3 = models.CharField(db_column='BADDR3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BPOSTCODE = models.CharField(db_column='BPOSTCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BSTATE = models.CharField(db_column='BSTATE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BCITY = models.CharField(db_column='BCITY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    BCOUNTRY = models.CharField(db_column='BCOUNTRY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DADDR1 = models.CharField(db_column='DADDR1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DADDR2 = models.CharField(db_column='DADDR2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DADDR3 = models.CharField(db_column='DADDR3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DPOSTCODE = models.CharField(db_column='DPOSTCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DSTATE = models.CharField(db_column='DSTATE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DCITY = models.CharField(db_column='DCITY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DCOUNTRY = models.CharField(db_column='DCOUNTRY', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    CANCEL_QTY = models.FloatField(db_column='CANCEL_QTY', blank=True, null=True)  # Field name made lowercase.
    REC_STATUS = models.FloatField(db_column='REC_STATUS', blank=True, null=True)  # Field name made lowercase.
    REC_EXPECT = models.DateTimeField(db_column='REC_EXPECT',null=True)
    REC_TTL = models.FloatField(db_column='REC_TTL', blank=True, null=True)  # Field name made lowercase.
    CREATE_USER = models.CharField(db_column='CREATE_USER', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    CREATE_DATE = models.DateTimeField(db_column='CREATE_DATE',auto_now_add=True,null=True)
    PHY_NO = models.CharField(db_column='PHY_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PO_NO = models.CharField(db_column='PO_NO',blank=True,max_length = 259, default='', null=True)  # Field name made lowercase.
    
    

    class Meta:
        db_table = 'Stk_MovDoc_Hdr'


class MovDtlModel(models.Model):
    DOC_ID = models.AutoField(db_column='DOC_ID',primary_key=True)  # Field name made lowercase.
    DOC_NO = models.CharField(db_column='DOC_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    MOV_CODE = models.CharField(db_column='MOV_CODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    MOV_TYPE = models.CharField(db_column='MOV_TYPE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_LINENO = models.FloatField(db_column='DOC_LINENO', blank=True, null=True)  # Field name made lowercase.
    DOC_DATE = models.DateTimeField(db_column='DOC_DATE',auto_now_add=True,null=True)
    GRN_NO = models.CharField(db_column='GRN_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    REF_NO = models.CharField(db_column='REF_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ITEMCODE = models.CharField(db_column='ITEMCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ITEMDESC = models.CharField(db_column='ITEMDESC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ITEMPRICE = models.FloatField(db_column='ITEMPRICE', blank=True, null=True)  # Field name made lowercase.
    DOC_UOMTYPE = models.CharField(db_column='DOC_UOMTYPE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_UOMQTY = models.FloatField(db_column='DOC_UOMQTY', blank=True, null=True)  # Field name made lowercase.
    DOC_QTY = models.FloatField(db_column='DOC_QTY', blank=True, null=True)  # Field name made lowercase.
    DOC_FOCQTY = models.FloatField(db_column='DOC_FOCQTY', blank=True, null=True)  # Field name made lowercase.
    DOC_TTLQTY = models.FloatField(db_column='DOC_TTLQTY', blank=True,null=True)  # Field name made lowercase.
    DOC_PRICE = models.FloatField(db_column='DOC_PRICE', blank=True,null=True)  # Field name made lowercase.
    DOC_MDISC = models.CharField(db_column='DOC_MDISC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_PDISC = models.FloatField(db_column='DOC_PDISC', blank=True, null=True)  # Field name made lowercase.
    DOC_DISC = models.FloatField(db_column='DOC_DISC', blank=True,null=True)  # Field name made lowercase.
    DOC_AMT = models.FloatField(db_column='DOC_AMT', blank=True, null=True)  # Field name made lowercase.
    REC_QTY1 = models.FloatField(db_column='REC_QTY1', blank=True, null=True)  # Field name made lowercase.
    REC_QTY2 = models.FloatField(db_column='REC_QTY2', blank=True,  null=True)  # Field name made lowercase.
    REC_QTY3 = models.FloatField(db_column='REC_QTY3', blank=True,  null=True)  # Field name made lowercase.
    REC_QTY5 = models.FloatField(db_column='REC_QTY5', blank=True, null=True)  # Field name made lowercase.
    REC_TTL = models.FloatField(db_column='REC_TTL', blank=True, null=True)  # Field name made lowercase.
    POSTED_QTY = models.FloatField(db_column='POSTED_QTY', blank=True, null=True)  # Field name made lowercase.
    CANCEL_QTY = models.FloatField(db_column='CANCEL_QTY', blank=True,  null=True)  # Field name made lowercase.
    ORD_MEMO1 = models.CharField(db_column='ORD_MEMO1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ORD_MEMO2 = models.CharField(db_column='ORD_MEMO2', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ORD_MEMO3 = models.CharField(db_column='ORD_MEMO3', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ORD_MEMO4 = models.CharField(db_column='ORD_MEMO4', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    CREATE_USER = models.CharField(db_column='CREATE_USER', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    CREATE_DATE = models.DateTimeField(db_column='CREATE_DATE',auto_now_add=True,null=True)
    DOC_UOM = models.CharField(db_column='DOC_UOM', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOC_EXPDATE = models.DateTimeField(db_column='DOC_EXPDATE',auto_now=True,null=True)
    DOC_BATCH_NO = models.CharField(db_column='DOC_BATCH_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_NO = models.CharField(db_column='PHY_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    itm_Brand = models.CharField(db_column='itm_Brand', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    itm_Range = models.CharField(db_column='itm_Range', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Stk_Adj_Reason_Code = models.CharField(db_column='Stk_Adj_Reason_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ITEM_REMARK = models.CharField(db_column='ITEM_REMARK', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    DOCUOMDesc = models.CharField(db_column='DOCUOMDesc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    itmBrandDesc = models.CharField(db_column='itmBrandDesc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    itmRangeDesc = models.CharField(db_column='itmRangeDesc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    
    

    class Meta:
        db_table = 'Stk_MovDoc_Dtl'



class PHYHdrModel(models.Model):
    PHY_ID = models.AutoField(db_column='PHY_ID',primary_key=True)  # Field name made lowercase.
    PHY_NO = models.CharField(db_column='PHY_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STORE_NO = models.CharField(db_column='STORE_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_REF = models.CharField(db_column='PHY_REF', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_REMK1 = models.CharField(db_column='PHY_REMK1', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_DATE = models.DateTimeField(db_column='PHY_DATE',auto_now_add=True,null=True)
    POST_DATE = models.DateTimeField(db_column='POST_DATE',auto_now_add=True,null=True)
    STAFF_NO = models.CharField(db_column='STAFF_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STAFF_NAME = models.CharField(db_column='STAFF_NAME', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_STATUS = models.FloatField(db_column='PHY_STATUS', blank=True,null=True)  # Field name made lowercase.
    PHY_LINES = models.FloatField(db_column='PHY_LINES', blank=True,null=True)  # Field name made lowercase.
    PHY_TTLQTY = models.FloatField(db_column='PHY_TTLQTY', blank=True, null=True)  # Field name made lowercase.
    PHY_TTLAMT = models.FloatField(db_column='PHY_TTLAMT', blank=True,  null=True)  # Field name made lowercase.
    PHY_COUNTQTY = models.FloatField(db_column='PHY_COUNTQTY', blank=True, null=True)  # Field name made lowercase.
    
    

    class Meta:
        db_table = 'STK_PHYHdr'


class PHYDtlModel(models.Model):
    PHY_ID = models.AutoField(db_column='PHY_ID',primary_key=True)  # Field name made lowercase.
    PHY_NO = models.CharField(db_column='PHY_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STORE_NO = models.CharField(db_column='STORE_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_LINENO = models.FloatField(db_column='PHY_LINENO', blank=True,  null=True)  # Field name made lowercase.
    PHY_DATE = models.DateTimeField(db_column='PHY_DATE',auto_now_add=True,null=True)
    STAFF_NO = models.CharField(db_column='STAFF_NO', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    STATUS = models.FloatField(db_column='STATUS', blank=True, null=True)  # Field name made lowercase.
    ITEMCODE = models.CharField(db_column='ITEMCODE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ITEMDESC = models.CharField(db_column='ITEMDESC', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_REMARK = models.CharField(db_column='PHY_REMARK', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_UOM = models.CharField(db_column='PHY_UOM', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_UOMTYPE = models.CharField(db_column='PHY_UOMTYPE', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    PHY_UOMQTY = models.FloatField(db_column='PHY_UOMQTY', blank=True, null=True)  # Field name made lowercase.
    PHY_QTY = models.FloatField(db_column='PHY_QTY', blank=True,  null=True)  # Field name made lowercase.
    PHY_TTLQTY = models.FloatField(db_column='PHY_TTLQTY', blank=True, null=True)  # Field name made lowercase.
    PHY_COUNTQTY = models.FloatField(db_column='PHY_COUNTQTY', blank=True,  null=True)  # Field name made lowercase.
    PHY_VARIANCE = models.FloatField(db_column='PHY_VARIANCE', blank=True, null=True)  # Field name made lowercase.
    PHY_AMT = models.FloatField(db_column='PHY_AMT', blank=True, null=True)  # Field name made lowercase.
    PHY_COST = models.FloatField(db_column='PHY_COST', blank=True, null=True)  # Field name made lowercase.
    PHY_UCOST = models.FloatField(db_column='PHY_UCOST', blank=True, null=True)  # Field name made lowercase.
    
    

    class Meta:
        db_table = 'STK_PHYdtl'


    
class SystemLogModel(models.Model):
    ID = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    Log_Type = models.CharField(db_column='Log_Type', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Log_DateTime = models.DateTimeField(db_column='Log_DateTime',auto_now_add=True,null=True)
    Log_User = models.CharField(db_column='Log_User', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Log_Process = models.CharField(db_column='Log_Process', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Log_Message = models.CharField(db_column='Log_Message', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Log_Site_Code = models.CharField(db_column='Log_Site_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='created_at',auto_now_add=True,null=True)
    updated_at = models.DateTimeField(db_column='updated_at',auto_now=True,null=True)
    

    class Meta:
        db_table = 'SystemLog'
        managed = False
        

class City(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'City'
        managed = False

    def __str__(self):
        return str(self.itm_desc)            
    
class State(models.Model):
    itm_id = models.AutoField(db_column='itm_ID', primary_key=True)  # Field name made lowercase.
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'State'
        managed = False

    def __str__(self):
        return str(self.itm_desc)

class Country(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    phonecode = models.CharField(db_column='phoneCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Country'
        managed = False

    def __str__(self):
        return str(self.itm_desc) 


class AllDropdownModel(models.Model):
    AllDropdown_ID = models.AutoField(db_column='AllDropdown_ID',primary_key=True)  # Field name made lowercase.
    AllDropdown_Item = models.CharField(db_column='AllDropdown_Item', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    AllDropdown_Desc = models.CharField(db_column='AllDropdown_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'AllDropdown_List'
   
class SupplyContactInfoModel(models.Model):
    ContactInfo_ID = models.AutoField(db_column='ContactInfo_ID',primary_key=True)  # Field name made lowercase.
    Supplier_Code = models.CharField(db_column='Supplier_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ContactInfo_Name = models.CharField(db_column='ContactInfo_Name', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ContactInfo_PhoneNo = models.CharField(db_column='ContactInfo_PhoneNo', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    ContactInfo_Email = models.CharField(db_column='ContactInfo_Email', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'Supply_ContactInfo'



class ControlNoModel(models.Model):
    id = models.AutoField(db_column='Control_id',primary_key=True)  # Field name made lowercase.
    control_prefix = models.CharField(db_column='control_prefix', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    control_description = models.CharField(db_column='control_description', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    control_no = models.CharField(db_column='control_no', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    Site_Code = models.CharField(db_column='Site_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'Control_No'
        managed = False


class CommissionProfile(models.Model):
    
    PERIOD_CHOICES = (
        ("1", "year"),
        ("2", "month"),
        ("3", "week"),
    )

    COMM_CHOICES = (
        ("1", "commission"),
        ("2", "incentive"),
    )
    
    employe_level_id =models.ForeignKey(EmpLevel, on_delete=models.CASCADE,blank=True,null=True) 
    profile_name = models.CharField(max_length=255)
    period = models.CharField(max_length = 20,choices = PERIOD_CHOICES,default = None)
   # item_div_id = models.ForeignKey(ItemDiv, on_delete=models.CASCADE) 
   # item_id = models.ForeignKey(ItemDiv, on_delete=models.CASCADE) 
    from_date = models.DateField(null=True,blank=True)
    to_date = models.DateField(null=True,blank=True) 
    min_value = models.FloatField(db_column='Target min')
    max_value = models.FloatField(db_column='Target max')
    commission = models.IntegerField(db_column='commission',blank=True,null=True)
    ispercent = models.BooleanField()
    incentive = models.FloatField(db_column='incentive',null=True)
    incentive_ispercent = models.BooleanField()
    range_id  = models.ForeignKey(ItemRangeModel,on_delete=models.CASCADE)
    brand_id =  models.ForeignKey(ItemBrandModel, on_delete=models.CASCADE) 
    department_id =  models.ForeignKey(ItemDeptModel, on_delete=models.CASCADE,related_name= 'item_department') 
    commission_type = models.BooleanField()
    rangee_comm_id  =  models.ForeignKey(ItemRangeModel,on_delete=models.CASCADE,related_name= 'range_commission',null=True)
    brand_comm_id =   models.ForeignKey(ItemBrandModel, on_delete=models.CASCADE,related_name= 'range_brand',null=True)
    department_comm_id = models.ForeignKey(ItemDeptModel, on_delete=models.CASCADE,related_name= 'range_dept',null=True) 
    
    class Meta:
        db_table = 'Commission_profile'

class CommTarget(models.Model):
    employe_level_id = models.ForeignKey(EmpLevel, on_delete=models.CASCADE)  
    profile_name = models.CharField(max_length=255)
    from_date_comm = models.DateField(null=True)
    to_date_comm = models.DateField(null=True)
    min_value_comm = models.FloatField(db_column='Target min comm',null=True,blank=True)
    max_value_comm = models.FloatField(db_column='Target max comm',null=True,blank=True)
    commission_comm = models.IntegerField(db_column='commission comm',null=True,blank=True)
    ispercent_comm = models.BooleanField(default=False)
    incentive_comm = models.FloatField(db_column='incentive comm',null=True,blank=True)
    incentive_ispercent_comm = models.BooleanField(default=False)
    comm_Profile_id = models.ForeignKey(CommissionProfile, on_delete=models.CASCADE,null=True) 
    
    class Meta:
        db_table = 'Comm_target'

class CommDeduction(models.Model): 
    employe_level_id = models.ForeignKey(EmpLevel, on_delete=models.CASCADE) 
    profile_name = models.CharField(max_length=255)
    gst =  models.FloatField(db_column='GST',null=True,blank=True)
    gst_ispercent = models.BooleanField(default=False)
    bank_changes =  models.FloatField(db_column='Bank changes',null=True,blank=True)
    bc_ispercent = models.BooleanField(default=False)
    emi =  models.FloatField(db_column='EMI',null=True,blank=True)
    emi_ispercent = models.BooleanField(default=False)
    comm_Profilede_id = models.ForeignKey(CommissionProfile, on_delete=models.CASCADE,null=True)
    
    class Meta:
        db_table = 'Comm_deduction'

class SalarySubTypeLookup(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    typename = models.CharField(max_length=40)
    accountcode = models.CharField(max_length=10)
    showinallowance = models.BooleanField(default=False)
    showindeduction = models.BooleanField(default=False)
    showinpayment = models.BooleanField(default=False)
    isactive = models.BooleanField(default=False)

    class Meta:
        db_table = 'SalarySubTypeLookup'

    def __str__(self):
        return str(self.accountcode) 

class ModeOfPayment(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    modename = models.CharField(max_length=40)
    accountcode = models.CharField(max_length=10)
    isactive = models.BooleanField(default=False)

    class Meta:
        db_table = 'modeofpayment'

    def __str__(self):
        return str(self.accountcode) 


class DeliveryOrdersign(models.Model):

    id = models.AutoField(db_column='ID', primary_key=True)
    do_id = models.ForeignKey('custom.DeliveryOrderModel', on_delete=models.PROTECT,null=True)   
    deliveryorder_no = models.CharField(db_column='DeliveryOrder_No', max_length=255, blank=True, null=True)  
    do_sig = models.ImageField(db_column='DO_Sig', blank=True, null=True,upload_to='img') 

    class Meta:
        db_table = 'DeliveryOrdersign'

class quotationsign(models.Model):

    id = models.AutoField(db_column='ID', primary_key=True)
    fk_quotation = models.ForeignKey('custom.QuotationModel', on_delete=models.PROTECT, null=True)
    quotation_number = models.CharField(db_column='Quotation_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quo_sig = models.ImageField(db_column='quo_sig', blank=True, null=True,upload_to='img') 

    class Meta:
        db_table = 'quotationsign'


class ManualInvoicesign(models.Model):

    id = models.AutoField(db_column='ID', primary_key=True)
    fk_manualinvoice = models.ForeignKey('custom.ManualInvoiceModel', on_delete=models.PROTECT, null=True, default=1)
    manualinv_number = models.CharField(db_column='ManualInvoice_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    manualinv_sig = models.ImageField(db_column='manualinv_sig', blank=True, null=True,upload_to='img') 

    class Meta:
        db_table = 'ManualInvoicesign'


class EquipmentUsage(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    eq_number = models.CharField(db_column='EQ_Number', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Project', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    company = models.CharField(db_column='Company', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    contact_person = models.CharField(db_column='ContactPerson', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    validity = models.CharField(db_column='Validity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    terms = models.CharField(db_column='Terms', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    in_charge = models.CharField(db_column='InCharge', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    footer = models.CharField(db_column='Footer', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='Issue_Date',null=True)
    is_issued = models.BooleanField(default=False)
    emp_id = models.ForeignKey('cl_table.Employee', on_delete=models.PROTECT,null=True)
    cust_id = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True) 
    
    class Meta:
        db_table = 'EquipmentUsage'


class EquipmentUsageItemModel(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    quotation_quantity = models.CharField(db_column='Item_Quantity', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_unitprice = models.CharField(db_column='Item_UnitPrice', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemremarks = models.CharField(db_column='Item_Remarks', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemcode = models.CharField(db_column='Item_Code', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    quotation_itemdesc = models.CharField(db_column='Item_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    item_uom = models.CharField(db_column='Item_UOM', max_length=600, blank=True, null=True)  # Field name made lowercase.
    active = models.CharField(db_column='Active', blank=True, max_length = 255, default='active', null=True)  # Field name made lowercase.
    fk_equipment = models.ForeignKey('custom.EquipmentUsage', on_delete=models.PROTECT, null=True, default=1)
    Item_Codeid = models.ForeignKey('cl_table.Stock', on_delete=models.PROTECT, null=True) 
    item_div = models.CharField(db_column='Item_Div', max_length=20, blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        db_table = 'EquipmentUsage_Item'


class EquipmentDropdownModel(models.Model):
    id = models.AutoField(db_column='Dropdown_ID',primary_key=True)  # Field name made lowercase.
    dropdown_item = models.CharField(db_column='Dropdown_Item', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    dropdown_desc = models.CharField(db_column='Dropdown_Desc', blank=True, max_length = 255, default='', null=True)  # Field name made lowercase.
    active = models.BooleanField(default=True)
    

    class Meta:
        db_table = 'EquipmentDropdownModel'

class Currencytable(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    curr_code = models.CharField(db_column='Curr_Code', max_length=3, blank=True, null=True)  
    curr_name = models.CharField(db_column='Curr_Name', max_length=255, blank=True, null=True)  
    curr_rate = models.DecimalField(db_column='Curr_Rate', max_digits=2, decimal_places=1, blank=True, null=True)  
    curr_isactive = models.BooleanField(db_column='Curr_isactive', default=True)  
   
    class Meta:
        db_table = 'CurrencyTable'        



class PosDiscQuant(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_no = models.CharField(max_length=500,null=True)
    dt_itemno = models.CharField(db_column='dt_ItemNo', max_length=50,null=True)  # Field name made lowercase.
    disc_amt = models.FloatField(db_column='Disc_Amt', blank=True, null=True)  # Field name made lowercase.
    disc_percent = models.FloatField(db_column='Disc_Percent', blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo',null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=200, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50,null=True)  # Field name made lowercase.
    dt_date = models.DateTimeField(db_column='dt_Date',null=True,auto_now_add=True)  # Field name made lowercase.
    dt_status = models.CharField(max_length=50,null=True)
    dt_auto = models.BooleanField(db_column='dt_Auto',null=True)  # Field name made lowercase.
    line_no = models.IntegerField(db_column='Line_no',null=True)  # Field name made lowercase.
    disc_user = models.CharField(db_column='Disc_User', max_length=250, blank=True, null=True)  # Field name made lowercase.
    lnow = models.BooleanField(db_column='lNow',null=True)  # Field name made lowercase.
    dt_price = models.FloatField(db_column='dt_Price', blank=True, null=True)  # Field name made lowercase.
    istransdisc = models.BooleanField(db_column='IsTransDisc',null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Pos_DiscQuant'
    
    def __str__(self):
        return str(self.dt_itemno)