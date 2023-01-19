from django.db import models
from cl_table.models import City, State, Country, Fmspw, ItemUom, Customer
from django.conf import settings

# Create your models here.
#intial

#Final
class SiteGroup(models.Model):
    id = models.BigAutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=20, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active',default=True)  # Field name made lowercase.
    is_delete = models.BooleanField(db_column='Is_Delete', null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at  = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        db_table = 'Site_Group'

    def __str__(self):
        return str(self.description)


class ItemSitelist(models.Model):
    itemsite_id = models.BigAutoField(db_column='ItemSite_ID', primary_key=True)  # Field name made lowercase.
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=20, null=True)  # Field name made lowercase.
    itemsite_desc = models.CharField(db_column='ItemSite_Desc', max_length=60, blank=True, null=True)  # Field name made lowercase.
    itemsite_type = models.CharField(db_column='ItemSite_Type', max_length=10, blank=True, null=True)  # Field name made lowercase.
    item_purchasedept = models.CharField(db_column='Item_PurchaseDept', max_length=20, blank=True, null=True)  # Field name made lowercase.
    itemsite_address = models.CharField(db_column='ItemSite_Address', max_length=255, blank=True, null=True)  # Field name made lowercase.
    itemsite_postcode = models.CharField(db_column='ItemSite_Postcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ItemSite_Cityid   = models.ForeignKey(City, on_delete=models.PROTECT, null=True)
    itemsite_city = models.CharField(db_column='ItemSite_City', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ItemSite_Stateid  = models.ForeignKey(State, on_delete=models.PROTECT, null=True)
    itemsite_state = models.CharField(db_column='ItemSite_State', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ItemSite_Countryid  = models.ForeignKey(Country, on_delete=models.PROTECT,  null=True)
    itemsite_country = models.CharField(db_column='ItemSite_Country', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemsite_phone1 = models.CharField(db_column='ItemSite_Phone1', max_length=50,  null=True)  # Field name made lowercase.
    itemsite_phone2 = models.CharField(db_column='ItemSite_Phone2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemsite_fax = models.CharField(db_column='ItemSite_Fax', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemsite_email = models.EmailField(db_column='ItemSite_Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ItemSite_Userid = models.ForeignKey(Fmspw, on_delete=models.PROTECT, null=True)
    itemsite_user = models.CharField(db_column='ItemSite_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemsite_date = models.DateField(db_column='ItemSite_Date', blank=True, null=True)  # Field name made lowercase.
    itemsite_time = models.DateTimeField(db_column='ItemSite_Time', blank=True, null=True)  # Field name made lowercase.
    itemsite_isactive = models.BooleanField(db_column='ItemSite_Isactive',default=True)  # Field name made lowercase.
    itemsite_refcode = models.CharField(db_column='ITEMSITE_REFCODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Site_Groupid    = models.ForeignKey(SiteGroup, on_delete=models.PROTECT, null=True)
    site_group = models.CharField(db_column='Site_Group', max_length=50, blank=True, null=True)  # Field name made lowercase.
    site_is_gst = models.BooleanField(db_column='SITE_IS_GST', null=True,default=False)  # Field name made lowercase.
    account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    clientindex = models.BigIntegerField(db_column='ClientIndex', blank=True, null=True)  # Field name made lowercase.
    heartbeat = models.DateTimeField(db_column='HeartBeat', blank=True, null=True)  # Field name made lowercase.
    systemlog_mdpl_update = models.BooleanField(db_column='SystemLog_MDPL_Update', null=True,default=False)  # Field name made lowercase.
    ratings = models.CharField(db_column='Ratings', max_length=40, blank=True, null=True)  # Field name made lowercase.
    pic_path = models.TextField(db_column='pic_Path', blank=True, null=True)  # Field name made lowercase.
    qrcode = models.CharField(db_column='QRCode', max_length=40, blank=True, null=True)  # Field name made lowercase.
    sitedbconnectionurl = models.CharField(db_column='siteDbConnectionUrl', max_length=100, blank=True, null=True)  # Field name made lowercase.
    geolink = models.CharField(max_length=100, blank=True, null=True)
    weekdays_timing = models.CharField(max_length=100, blank=True, null=True)
    weekend_timing = models.CharField(max_length=100, blank=True, null=True)
    holliday_timing = models.CharField(max_length=100, blank=True, null=True)
    closed_on = models.CharField(db_column='Closed_on', max_length=100, blank=True, null=True)
    picpath = models.CharField(max_length=100, blank=True, null=True)
    owner = models.CharField(db_column='Owner', max_length=300, blank=True, null=True)
    services = models.ManyToManyField('cl_table.Stock', blank=True) 
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    skills_list = models.CharField(max_length=1000, null=True)
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    service_sel = models.BooleanField(db_column='Service_Selection', default=False) 
    service_text = models.BooleanField(db_column='Service_Text', default=False) 
    is_nric = models.BooleanField(db_column='Nric', default=False) 
    is_automember = models.BooleanField(db_column='IsAutoMember', default=False) 
    startday_hour = models.CharField(db_column='StartDay_Hour', max_length=100, blank=True, null=True)
    endday_hour = models.CharField(db_column='EndDay_Hour', max_length=100, blank=True, null=True)
    cell_duration = models.CharField(db_column='Cell_Duration', max_length=100, blank=True, null=True)
    resource_count = models.CharField(db_column='resource_count', max_length=100, blank=True, null=True)
    inv_templatename = models.CharField(db_column='Invoice_TemplateName', max_length=500, blank=True, null=True)  # Field name made lowercase.
    url = models.CharField(max_length=1000, null=True)
    is_dragappt = models.BooleanField(db_column='is_dragappt',default=True)  # Field name made lowercase.
    is_empvalidate = models.BooleanField(db_column='is_empvalidate',default=True)  # Field name made lowercase.
    is_exclusive = models.BooleanField(null=True)
    walkin_custid = models.IntegerField(db_column='Walkin_Custid', blank=True, null=True)  # Field name made lowercase.
    showallsitebooking = models.BooleanField(db_column='showallsitebooking',default=False)  # Field name made lowercase.

    class Meta:
        db_table = 'Item_SiteList'
        unique_together = [['itemsite_desc','itemsite_phone1','itemsite_email']]

    def __str__(self):
        return str(self.itemsite_code)


# class TempUomPrice(models.Model):
#     id = models.AutoField(db_column='ID',primary_key=True)
#     Item_Codeid = models.ForeignKey('cl_table.Stock', on_delete=models.PROTECT, db_column='itemCodeid', blank=True, null=True) 
#     item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     Cust_Codeid = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, blank=True, null=True)
#     cust_code = models.CharField(db_column='Cust_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     cart_id = models.CharField(max_length=20,blank=True, null=True)
#     cart_date = models.DateField(db_column='Cart_Date',null=True, blank=True)
#     Item_UOMid = models.ForeignKey('cl_table.ItemUom', on_delete=models.PROTECT,null=True, blank=True)
#     item_uom = models.CharField(db_column='Item_UOM', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     item_price = models.FloatField(db_column='ITEM_PRICE', blank=True, null=True)  # Field name made lowercase.
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at  = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = 'Temp_UomPrice'

#     def __str__(self):
#         return str(self.item_uom)

class ReverseTrmtReason(models.Model):
    id = models.BigAutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    rev_no = models.CharField(db_column='Rev_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rev_desc = models.CharField(db_column='Rev_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rev_remark = models.CharField(db_column='Rev_Remark', max_length=50, blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_active', blank=True, null=True,default=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Reverse_Trmt_Reason'

    def __str__(self):
        return str(self.rev_desc)    


class VoidReason(models.Model):
    id = models.AutoField(primary_key=True)
    reason_code = models.CharField(db_column='Reason_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    reason_desc = models.CharField(db_column='Reason_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True,default=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Void_Reason'

    def __str__(self):
        return str(self.reason_desc)    
    
class LoggedInUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='logged_in_user', on_delete=models.PROTECT)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    current_key = models.CharField(max_length=40, blank=True, null=True)
    
    class Meta:
        db_table = 'logged_inuser'

    def str(self):
        return self.user.username

class TreatmentUsage(models.Model):
    id = models.BigAutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    treatment_code = models.CharField(db_column='Treatment_Code',  max_length=20)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code', max_length=20)  # Field name made lowercase.
    item_desc = models.CharField(db_column='Item_Desc', max_length=50)  # Field name made lowercase.
    qty = models.FloatField(db_column='Qty')  # Field name made lowercase.
    uom = models.CharField(db_column='UOM', max_length=20)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50)  # Field name made lowercase.
    usage_status = models.CharField(db_column='Usage_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    line_no = models.FloatField(db_column='Line_No', blank=True, null=True)  # Field name made lowercase.
    void_line_ref = models.CharField(db_column='Void_Line_Ref', max_length=20, blank=True, null=True)  # Field name made lowercase.
    usage_update = models.CharField(db_column='Usage_Update', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(db_column='SA_TRANSACNO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True,default=True)  # Field name made lowercase.
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at  = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        db_table = 'Treatment_Usage'
        # unique_together = (('treatment_code', 'item_code', 'site_code'),)

    def __str__(self):
        return str(self.treatment_code)    
        
class UsageMemo(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    memo_no = models.CharField(db_column='Memo_No', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_name = models.CharField(db_column='Item_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    date_out = models.DateTimeField(db_column='Date_Out', blank=True, null=True)  # Field name made lowercase.
    time_out = models.DateTimeField(db_column='Time_Out',auto_now=True, blank=True, null=True)  # Field name made lowercase.
    qty = models.IntegerField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    uom = models.CharField(db_column='UOM', max_length=10, blank=True, null=True)  # Field name made lowercase.
    staff_code = models.CharField(db_column='Staff_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    staff_name = models.CharField(db_column='Staff_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    staff_barcode = models.CharField(db_column='Staff_Barcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    date_return = models.DateTimeField(db_column='Date_Return', blank=True, null=True)  # Field name made lowercase.
    time_return = models.DateTimeField(db_column='Time_Return', blank=True, null=True)  # Field name made lowercase.
    created_by = models.CharField(db_column='Created_By', max_length=20, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    memo_remarks = models.CharField(db_column='Memo_Remarks', max_length=100, blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at  = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        db_table = 'Usage_Memo'


    def __str__(self):
        return str(self.memo_no)    
            

class Treatmentface(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    treatment_code = models.CharField(db_column='Treatment_Code', max_length=50)  # Field name made lowercase.
    str1 = models.CharField(db_column='Str1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    str2 = models.CharField(db_column='Str2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    str3 = models.CharField(db_column='Str3', max_length=100, blank=True, null=True)  # Field name made lowercase.
    str4 = models.CharField(db_column='Str4', max_length=100, blank=True, null=True)  # Field name made lowercase.
    str5 = models.CharField(db_column='Str5', max_length=100, blank=True, null=True)  # Field name made lowercase.
    str6 = models.CharField(db_column='Str6', max_length=100, blank=True, null=True)  # Field name made lowercase.
    str7 = models.CharField(db_column='Str7', max_length=100, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50)  # Field name made lowercase.
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at  = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        db_table = 'TreatmentFace'
        unique_together = (('treatment_code', 'site_code'),)


class Usagelevel(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    service_code = models.CharField(db_column='Service_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qty = models.CharField(db_column='Qty', max_length=10, blank=True, null=True)  # Field name made lowercase.
    uom = models.CharField(db_column='UOM', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sequence = models.IntegerField(db_column='Sequence', blank=True, null=True)  # Field name made lowercase.
    service_desc = models.CharField(db_column='Service_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    item_desc = models.CharField(db_column='Item_desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    optional = models.BooleanField(db_column='Optional')  # Field name made lowercase.


    class Meta:
        db_table = 'UsageLevel'


class priceChangeLog(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20,blank=True, null=True)
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=10,blank=True, null=True)  # Field name made lowercase.
    dt_itemno = models.CharField(max_length=20, blank=True, null=True)
    dt_lineno = models.IntegerField(db_column='dt_LineNo',blank=True, null=True)  # Field name made lowercase.
    lineno = models.IntegerField(db_column='LineNo',blank=True, null=True)  # Field name made lowercase.
    price = models.FloatField(db_column='price', blank=True, null=True)  # Field name made lowercase.
    discAmt = models.FloatField(db_column='discAmt', blank=True, null=True)  # Field name made lowercase.
    discPrice = models.FloatField(db_column='discPrice', blank=True, null=True)  # Field name made lowercase.
    transacAmount = models.FloatField(db_column='transacAmount', blank=True, null=True)  # Field name made lowercase.
    depositAmount = models.FloatField(db_column='depositAmount', blank=True, null=True)  # Field name made lowercase.
    newPrice = models.FloatField(db_column='newPrice', blank=True, null=True)  # Field name made lowercase.
    newDiscAmt = models.FloatField(db_column='newDiscAmt', blank=True, null=True)  # Field name made lowercase.
    newDiscPrice = models.FloatField(db_column='newDiscPrice', blank=True, null=True)  # Field name made lowercase.
    newTransacAmount = models.FloatField(db_column='newTransacAmount', blank=True, null=True)  # Field name made lowercase.
    newDepositAmount = models.FloatField(db_column='newDepositAmount', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


    class Meta:
        db_table = 'priceChangeLog'



class TmpTreatmentSession(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    treatment_parentcode = models.CharField(db_column='Treatment_ParentCode', max_length=200, blank=True, null=True)  # Field name made lowercase.
    session = models.IntegerField(db_column='session', blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'TmpTreatmentSession'

class VoucherPromo(models.Model):

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    voucher_code = models.CharField(db_column='voucher_code', max_length=200, blank=True, null=True)  # Field name made lowercase.
    voucher_desc =  models.CharField(db_column='voucher_desc', max_length=500, blank=True, null=True)  # Field name made lowercase.
    sms_text = models.TextField(db_column='sms_text', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.
    isdiscount = models.BooleanField(db_column='isdiscount',default=False)  # Field name made lowercase.
    conditiontype1 = models.CharField(db_column='conditiontype1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    conditiontype2 = models.CharField(db_column='conditiontype2', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'VoucherPromo'
        unique_together = (('price', 'isdiscount', 'conditiontype1','conditiontype2'),)

class SmsProcessLog(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sms_username = models.CharField(db_column='SMS_UserName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    sms_password = models.CharField(db_column='SMS_Password', max_length=100, blank=True, null=True)  # Field name made lowercase.
    sms_phone = models.CharField(db_column='SMS_Phone', max_length=300, blank=True, null=True)  # Field name made lowercase.
    sms_msg = models.CharField(db_column='SMS_Msg', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    sms_datetime = models.DateTimeField(db_column='SMS_DateTime', blank=True, null=True)  # Field name made lowercase.
    send_status = models.CharField(db_column='Send_Status', max_length=100, blank=True, null=True)  # Field name made lowercase.
    send_datetime = models.DateTimeField(db_column='Send_DateTime', blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    vendor_type = models.CharField(db_column='Vendor_Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    smsapireply = models.CharField(db_column='SMSApiReply', max_length=800, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    sms_task_number = models.CharField(db_column='SMS_Task_Number', max_length=10, blank=True, null=True)  # Field name made lowercase.
    sms_portno = models.CharField(db_column='SMS_PortNo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    sms_sendername = models.CharField(db_column='SMS_SenderName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    sms_campaignname = models.CharField(db_column='SMS_CampaignName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    sms_scheduleid = models.IntegerField(db_column='SMS_ScheduleID', blank=True, null=True)  # Field name made lowercase.
    sms_type = models.CharField(db_column='SMS_Type', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'SMS_Process_Log'

class TmpItemHelperSession(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    treatment_parentcode = models.CharField(db_column='Treatment_ParentCode', max_length=200, blank=True, null=True)  # Field name made lowercase.
    # treatmentpackage = models.ForeignKey('cl_table.TreatmentPackage', on_delete=models.PROTECT,null=True, blank=True)
    wp1 = models.FloatField(db_column='WP1', blank=True, null=True)  # Field name made lowercase.
    session = models.FloatField(db_column='Session', blank=True, null=True)  # Field name made lowercase.
    helper_name = models.CharField(db_column='Helper_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    helper_code = models.CharField(db_column='Helper_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(blank=True, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    helper_id = models.ForeignKey('cl_table.Employee', on_delete=models.PROTECT,null=True)

    class Meta:
        db_table = 'Tmp_Item_helperSession'
