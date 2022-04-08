from rest_framework import serializers
from .models import (TimeLogModel, ProjectModel, ActivityModel, QuotationModel, POModel, QuotationAddrModel, POAddrModel, QuotationDetailModel, PODetailModel, QuotationItemModel, POItemModel, DropdownModel, EmpLevel, Room, Combo_Services,ItemCart,VoucherRecord, PaymentRemarks, HolditemSetup,
PosPackagedeposit,SmtpSettings,AuthoriseModel, POModel, PODetailModel, POApprovalModel, ItemUOMPriceModel, 
ItemBatchModel, ItemBrandModel, ItemRangeModel, ItemDeptModel, EmployeeListModel, SiteCodeModel, ModeOfPayment,
ItemSupplyModel, DOModel, DODetailModel, StockModel, MovHdrModel, MovDtlModel, PHYHdrModel, PHYDtlModel, 
StktrnModel, SystemLogModel, SupplyContactInfoModel, ControlNoModel,CommissionProfile,CommTarget,CommDeduction, SalarySubTypeLookup,
ManualInvoiceModel,ManualInvoiceDetailModel,ManualInvoiceAddrModel,ManualInvoiceItemModel,WorkOrderInvoiceModel,
WorkOrderInvoiceDetailModel,WorkOrderInvoiceAddrModel,WorkOrderInvoiceItemModel)
from cl_table.models import (Treatment, Stock, PackageDtl, ItemClass, ItemRange, Employee, Tmptreatment,
TmpItemHelper,PosHaud,City, State, Country, Stock )
from cl_table.serializers import get_client_ip
from django.db.models import Sum
from datetime import date, timedelta, datetime
import datetime
from cl_app.models import ItemSitelist




class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemClass
        fields = ['id','itm_desc']
        read_only_fields = ('created_at', 'updated_at','itm_isactive') 

class TypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemRange
        fields = ['id','itm_desc']
        read_only_fields = ('created_at', 'updated_at')  
      
class EmpLevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmpLevel
        fields = ['id','level_desc','level_isactive']
        read_only_fields = ('created_at', 'updated_at','level_isactive') 

class RoomSerializer(serializers.ModelSerializer):

    sitecode_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)
    room_img = serializers.SerializerMethodField() 
    
    def get_room_img(self, obj):
        ip = get_client_ip(self.context['request'])
        if obj.Room_PIC:
            pic = str(obj.Room_PIC.url)
        else:
            pic = None    
        return pic

    class Meta:
        model = Room
        fields = ['id','displayname','room_img','Site_Codeid','sitecode_name','isactive']
        read_only_fields = ('created_at','Site_Codeid','sitecode_name', 'updated_at','isactive') 


class ComboServicesSerializer(serializers.ModelSerializer):

    # sitecode_name = serializers.CharField(source='Site_Code.itemsite_desc',required=False)

    class Meta:
        model = Combo_Services
        fields = ['id','Price','discount','services','combo_names']
        # read_only_fields = ('created_at', 'Site_Code','sitecode_name','updated_at','Isactive')

    def validate(self, data):
        if 'services' in data:
            if data['services'] is not None:
                for t in data['services']:
                    if Stock.objects.filter(id=t.id,item_isactive=False):
                        raise serializers.ValidationError("Services ID Does not exist!!")

        return data    

    def create(self, validated_data):
        services_data = validated_data.pop('services')
        combo = Combo_Services.objects.create(Price=validated_data.get('Price'))
        
        for s in services_data:
            combo.services.add(s)

        return combo 

    def update(self, instance, validated_data):
        instance.Price = validated_data.get("Price", instance.Price)
        services_data = validated_data.pop('services')
        if services_data:
            for existing in instance.services.all():
                instance.services.remove(existing) 

            for s in services_data:
                instance.services.add(s)

        instance.save()    
          
        return instance   


    def to_representation(self, value):
        ip = get_client_ip(self.context['request'])
        obj = Combo_Services.objects.filter(id=value.id).first()
        if obj.services.all():
            string = ""
            for i in obj.services.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc

        val =  list(set([str(ip)+str(t.Stock_PIC.url) for t in obj.services.all() if t.Stock_PIC]))

        mapped_object = {
            'id': value.id,
            'Price': "{:.2f}".format(float(value.Price)),
            'discount': "{:.2f}".format(float(value.discount)),
            'services' : list(set([t.pk for t in obj.services.all() if t.pk])),
            'combo_names' : string,
            'images' : val
            }
       
        return mapped_object           
                          

class itemCartSerializer(serializers.ModelSerializer): 
    sitecode_name = serializers.CharField(source='sitecodeid.itemsite_desc',required=False)
    itemstatus_name = serializers.CharField(source='itemstatus.status_short_desc',required=False)
    customer = serializers.CharField(source='cust_noid.cust_name',required=False)
    helper_name = serializers.SerializerMethodField() 
    ori_stockid = serializers.SerializerMethodField() 


    def get_helper_name(self, obj):
        if obj.helper_ids.all().exists():
            string = ""
            for i in obj.helper_ids.all():
                if string == "":
                    string = string + i.helper_id.display_name
                elif not string == "":
                    string = string +","+ i.helper_id.display_name
            return string
        else:
            return None 

    def get_ori_stockid(self, obj):
        return None
            

    class Meta:
        model = ItemCart
        fields = ['id','cust_noid','customer','customercode','cart_id','cart_date','cart_status','lineno',
        'check','itemcodeid','itemdesc','quantity','price','total_price','sitecodeid','sitecode_name',
        'sitecode','discount','discount_amt','discount_price','additional_discount','additional_discountamt',
        'deposit','trans_amt','tax','itemstatus','itemstatus_name','ratio','helper_name','done_sessions',
        'type','treatment_account','treatment','deposit_account','prepaid_account','item_uom','recorddetail',
        'itemtype','ori_stockid','treatment_no','is_service']
        read_only_fields = ('sitecode',)

    # def get_validation_exclusions(self):
    #     exclusions = super(itemCartSerializer, self).get_validation_exclusions()
    #     print(exclusions,"exclusions")
    #     return exclusions + ['cust_noid']    
    
class itemCartListSerializer(serializers.ModelSerializer): 
    item = serializers.CharField(source='itemcodeid.item_desc',required=False)
    item_class = serializers.CharField(source='itemcodeid.Item_Classid.itm_desc',required=False)
    itemstatus_name = serializers.CharField(source='itemstatus.status_short_desc',required=False)
    focreason_name = serializers.CharField(source='focreason.foc_reason_ldesc',required=False)
    holdreason_name = serializers.CharField(source='holdreason.hold_desc',required=False)

    class Meta:
        model = ItemCart
        fields = ['id','item','item_class','quantity','price','total_price','discount_price','trans_amt','deposit','itemstatus',
        'itemstatus_name','remark','focreason','focreason_name','holdreason','holdreason_name','holditemqty','ratio','discount',
        'discount_amt','additional_discountamt','is_foc']
        
    
class VoucherRecordSerializer(serializers.ModelSerializer): 

    sitecode_name = serializers.CharField(source='site_codeid.itemsite_desc',required=False)
    cust_name = serializers.CharField(source='cust_codeid.cust_name',required=False)


    class Meta:
        model = VoucherRecord
        fields = ['id','voucher_no','cust_codeid','cust_name','value','percent','site_codeid','sitecode_name','issued_expiry_date','isvalid']
                 
class VoucherRecordAccSerializer(serializers.ModelSerializer):

    class Meta:
        model = VoucherRecord
        fields = ['id','voucher_name','voucher_no','value','issued_expiry_date','sa_date']
         




class EmployeeDropSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    emp_name =  serializers.SerializerMethodField() 

    def get_emp_name(self, obj):
        return obj.display_name

    class Meta:
        model = Employee
        fields = ['id','emp_name','emp_pic']

class PaymentRemarksSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = PaymentRemarks
        fields = ['id','r_code','r_desc']

class HolditemSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolditemSetup
        fields = ['id','hold_code','hold_desc']

class PosPackagedepositSerializer(serializers.ModelSerializer):
    
    net_amt = serializers.SerializerMethodField() 
    is_td = serializers.SerializerMethodField() 

    def get_net_amt(self, obj):
        if obj.price and obj.qty:
            netamt = obj.price * obj.qty
        else:
            netamt =  0.00
        return netamt        
    
    def get_is_td(self, obj):
        is_td = False
        if obj.code:
            itmstock = Stock.objects.filter(item_code=obj.code[:-4],item_isactive=True).order_by('pk').first()
            if itmstock and itmstock.item_div and int(itmstock.item_div) == 3:
                is_td = True
                return is_td
            else:
                return is_td
        else:
            return is_td
        return netamt 

    class Meta:
        model = PosPackagedeposit
        fields = ['id','description','qty','deposit_amt','net_amt','auto','hold_qty','itemcart','is_td']
        

class PosPackagedepositpostSerializer(serializers.ModelSerializer):

    class Meta:
        model = PosPackagedeposit
        fields = ['id','deposit_amt','hold_qty','itemcart']


class ExchangeProductSerializer(serializers.Serializer):

    cust_id = serializers.CharField(required=True)
    cart_id = serializers.CharField(required=True, max_length=100)
    remarks = serializers.CharField(required=False)
    return_type = serializers.CharField(required=False)


class SmtpSettingsSerializer(serializers.ModelSerializer):

    sitecode = serializers.CharField(source='site_codeid.itemsite_code',required=False)

    class Meta:
        model = SmtpSettings
        fields = ['id','sender_name','sender_address','smtp_serverhost','port','user_email','user_password',
        'email_use_ssl','email_use_tls','email_subject','email_content','sms_content','site_codeid','sitecode']

   

class CartItemStatusSerializer(serializers.ModelSerializer): 
   
    class Meta:
        model = ItemCart
        fields = ['id','itemdesc','quantity','price','discount_price','trans_amt','deposit']

    def to_representation(self, obj):
        totl_disc = obj.discount_amt + obj.additional_discountamt
        service_data = []; sales_data = []
       

        # if obj.type in ['Sales','Deposit'] and int(obj.itemcodeid.item_div) == 3:
        #     service_data = [{'tmp_id': i.pk, 'emp_id': i.helper_id.pk ,'emp_name': i.helper_name,'percent' : int(i.percent) if i.percent else None, 'work_amt' : "{:.2f}".format(float(i.work_amt)) if i.work_amt else None, 'wp': int(i.wp1) if i.wp1 else None} for i in obj.helper_ids.all()]

        # if obj.type in ['Deposit','Top Up','Exchange']:
        #     sales_data = [{'tmp_id': i.pk, 'emp_id': i.emp_id.pk ,'emp_name': i.emp_id.display_name , 'percent' : int(i.ratio) if i.ratio else None, 'sales_amt' : "{:.2f}".format(float(i.salesamt)) if i.salesamt else None, 'sp': int(i.salescommpoints) if i.salescommpoints else None} for i in obj.multistaff_ids.all()]


        mapped_object = {
            'id': obj.id,
            'type' : obj.type,
            'itemdesc' : obj.itemdesc,
            'quantity': obj.quantity,
            'price': "{:.2f}".format(float(obj.price)),
            'totl_disc': "{:.2f}".format(float(totl_disc)),
            'discount_amt' : "{:.2f}".format(float(obj.discount_amt)),
            'additional_discountamt' : "{:.2f}".format(float(obj.additional_discountamt)),
            'discount_price' : "{:.2f}".format(float(obj.discount_price)),
            'trans_amt' : "{:.2f}".format(float(obj.trans_amt)),
            'deposit' : "{:.2f}".format(float(obj.deposit)),
            'is_foc': obj.is_foc,
            'itemstatus' : obj.itemstatus.pk if obj.itemstatus else None,
            'focreason' : obj.focreason.pk if obj.focreason else None,
            'holdreason' : obj.holdreason.pk if obj.holdreason else None,
            'holditemqty' : obj.holditemqty if obj.holditemqty else None,
            'work_point' : obj.itemcodeid.workcommpoints,
            'sales_point' : obj.itemcodeid.salescommpoints,
            'sales_staffs' : ",".join([i.display_name for i in obj.sales_staff.all()]),
            # 'sales_data' : sales_data,
            'service_staff' : ','.join([v.display_name for v in obj.service_staff.all() if v]),
            # 'service_data' : service_data,
            }
       
        return mapped_object  


class CartStaffsSerializer(serializers.ModelSerializer): 
   
    class Meta:
        model = ItemCart
        fields = ['id','itemdesc','quantity','price','discount_price','trans_amt','deposit']


    def to_representation(self, obj):
        totl_disc = obj.discount_amt + obj.additional_discountamt
        data = []; workamount = obj.trans_amt / obj.quantity

        # if obj.type == 'Sales' and int(obj.itemcodeid.item_div) == 3:
        #     data = [{'work':True,'sales':False,'staff':i.helper_id.display_name,'emp_id': i.helper_id.pk,
        #     'sales_percentage': None,'sales_amount': None,'sp': 0,
        #     'work_percentage': int(i.percent) if i.percent else None,
        #     'work_amount': "{:.2f}".format(float(i.work_amt)) if i.work_amt else None,
        #     'wp': int(i.wp1) if i.wp1 else 0,'tmp_workid': i.pk, 'tmp_saleid': None} for i in obj.helper_ids.all()]
        
        # elif obj.type == 'Deposit' and int(obj.itemcodeid.item_div) == 3:
        #     if obj.sessiondone and int(obj.sessiondone) != 0:
        #         done = int(obj.sessiondone)
        #         tmp_treatids = Tmptreatment.objects.filter(itemcart=obj).order_by('pk')[:done]
        #         workamount = sum([i.unit_amount for i in tmp_treatids])
        #     else:
        #         if obj.treatment_no and int(obj.treatment_no) != 0:
        #             workamount = obj.trans_amt / int(obj.treatment_no)
               

        #     data = [{'work':True,'sales':False,'staff':i.helper_id.display_name,'emp_id': i.helper_id.pk,
        #     'sales_percentage': None,'sales_amount': None,'sp': 0,
        #     'work_percentage': int(i.percent) if i.percent else None,
        #     'work_amount': "{:.2f}".format(float(i.work_amt)) if i.work_amt else None,
        #     'wp': int(i.wp1) if i.wp1 else 0,'tmp_workid': i.pk, 'tmp_saleid': None} for i in obj.helper_ids.all()]

        #     for i in obj.multistaff_ids.all():
        #         if not any(d['emp_id'] == i.emp_id.pk for d in data):
        #             val = {'work':False,'sales': True,'staff': i.emp_id.display_name,'emp_id': i.emp_id.pk,
        #                     'sales_percentage': int(i.ratio) if i.ratio else None,
        #                     'sales_amount': "{:.2f}".format(float(i.salesamt)) if i.salesamt else None,
        #                     'sp': int(i.salescommpoints) if i.salescommpoints else 0,
        #                     'work_percentage': None,'work_amount': None,'wp': 0,
        #                     'tmp_workid': None, 'tmp_saleid': i.pk}
        #             data.append(val)
        #         else:
        #             for j in data:
        #                 if i.emp_id.pk == j['emp_id']:
        #                     j.update({'sales': True, 'sales_percentage' : int(i.ratio) if i.ratio else None,
        #                     'sales_amount':"{:.2f}".format(float(i.salesamt)) if i.salesamt else None,
        #                     'sp': int(i.salescommpoints) if i.salescommpoints else 0,
        #                     'tmp_saleid' :i.pk })

        if obj.type in ['Deposit','Top Up','Exchange'] and int(obj.itemcodeid.item_div) == 3:  
            data = [{'work':False,'sales': True,'staff': i.emp_id.display_name,'emp_id': i.emp_id.pk,
            'sales_percentage': int(i.ratio) if i.ratio else None,
            'sales_amount': "{:.2f}".format(float(i.salesamt)) if i.salesamt else None,
            'sp': int(i.salescommpoints) if i.salescommpoints else 0,
            'work_percentage': None,'work_amount': None,'wp': 0,
            'tmp_workid': None, 'tmp_saleid': i.pk} for i in obj.multistaff_ids.all()]
                          

        elif obj.type in ['Deposit','Top Up','Exchange'] and int(obj.itemcodeid.item_div) != 3: 
            data = [{'work':False,'sales': True,'staff': i.emp_id.display_name,'emp_id': i.emp_id.pk,
            'sales_percentage': int(i.ratio) if i.ratio else None,
            'sales_amount': "{:.2f}".format(float(i.salesamt)) if i.salesamt else None,
            'sp': int(i.salescommpoints) if i.salescommpoints else 0,
            'work_percentage': None,'work_amount': None,'wp': 0,
            'tmp_workid': None, 'tmp_saleid': i.pk} for i in obj.multistaff_ids.all()]
        
      
        mapped_object = {
            'id': obj.id,
            'type' : obj.type,
            'div' :  obj.itemcodeid.item_div,
            'itemdesc' : obj.itemdesc,
            'quantity': obj.quantity,
            'price': "{:.2f}".format(float(obj.price)),
            'totl_disc': "{:.2f}".format(float(totl_disc)),
            'discount_price' : "{:.2f}".format(float(obj.discount_price)),
            'trans_amt' : "{:.2f}".format(float(obj.trans_amt)),
            'deposit' : "{:.2f}".format(float(obj.deposit)),
            'is_foc': obj.is_foc,
            'work_amount' : "{:.2f}".format(float(workamount)) if workamount else None,
            'work_point' : int(obj.itemcodeid.workcommpoints) if obj.itemcodeid.workcommpoints else 0,
            'sales_point' : int(obj.itemcodeid.salescommpoints) if obj.itemcodeid.salescommpoints else 0,
            'sales_staffs' : ",".join([i.display_name for i in obj.sales_staff.all()]),
            'service_staff' : ','.join([v.display_name for v in obj.service_staff.all() if v]),
            'data' : data,
            'sessiondone' : obj.sessiondone if obj.sessiondone else "",
            'td_session' : obj.multi_treat.all().count(),
            'treatment_ids' : obj.multi_treat.all().order_by('pk').values_list('pk', flat=True).distinct()
            }
       
        return mapped_object  
        

        
      
class CartDiscountSerializer(serializers.ModelSerializer): 
   
    class Meta:
        model = ItemCart
        fields = ['id','itemdesc','quantity','price','discount_price','trans_amt','deposit']

    def to_representation(self, obj):
        disclst_ids = obj.pos_disc.all().filter()
        disc_lst = [{'id': i.pk, 'disc_per': i.disc_percent, 
        'disc_amt': i.disc_amt,
        'remark': i.remark, 'transac': True if i.istransdisc == True else False} for i in disclst_ids]
        
        price = obj.price
        for i in disc_lst:
            i['amount'] = "{:.2f}".format(float(price))
            val = float(price) - float(i['disc_amt'])
            i['after_disc'] = "{:.2f}".format(float(val))
            i['disc_amt'] = "{:.2f}".format(float(i['disc_amt']))
            price = val


        mapped_object = {
            'id': obj.id,
            'itemdesc' : obj.itemdesc,
            'quantity': obj.quantity,
            'price': "{:.2f}".format(float(obj.price)),
            'discount_price' : "{:.2f}".format(float(obj.discount_price)),
            'trans_amt' : "{:.2f}".format(float(obj.trans_amt)),
            'deposit' : "{:.2f}".format(float(obj.deposit)),
            'disc_lst' : disc_lst
            }
       
        return mapped_object     


class CartServiceCourseSerializer(serializers.ModelSerializer): 

    cart_id = serializers.SerializerMethodField() 
   
    class Meta:
        model = ItemCart
        fields = ['id','itemdesc','quantity','price','total_price','discount_price','trans_amt','deposit',
        'discount','discount_amt','cart_id','treatment_no','free_sessions','sessiondone']


    def to_representation(self, obj):
       
        tmpids = Tmptreatment.objects.filter(itemcart=obj).order_by('pk')
        
        data = [{'slno': i,'program': c.course,'next_appt': datetime.datetime.strptime(str(c.next_appt), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") ,'unit_amount': "{:.2f}".format(c.unit_amount)} 
        for i, c in enumerate(tmpids, start=1)]

        disclst_ids = obj.pos_disc.all().filter()
        disc_lst = [{'id': i.pk, 'disc_per': i.disc_percent, 
        'disc_amt': i.disc_amt,
        'remark': i.remark, 'transac': True if i.istransdisc == True else False} for i in disclst_ids]
        
        price = obj.price
        for i in disc_lst:
            i['amount'] = "{:.2f}".format(float(price))
            val = float(price) - float(i['disc_amt'])
            i['after_disc'] = "{:.2f}".format(float(val))
            i['disc_amt'] = "{:.2f}".format(float(i['disc_amt']))
            price = val



        is_done = True

        h_obj = TmpItemHelper.objects.filter(itemcart=obj).order_by('pk')
        if h_obj:
            is_done = False
        
        lst = []
        emplst = list(set([i.helper_id.pk for i in h_obj]))  
        for i in emplst:
            hl_obj = TmpItemHelper.objects.filter(itemcart=obj,helper_id__pk=i).order_by('pk').last()
            emp = Employee.objects.filter(pk=i,emp_isactive=True).first() 
            if emp and hl_obj:
                lst.append({'name': emp.display_name,'wp1': "{:.2f}".format(float(hl_obj.wp1)),'session': "{:.2f}".format(float(hl_obj.session))})

    
        mapped_object = {
            'id': obj.id,
            'itemdesc' : obj.itemdesc,
            'quantity': obj.quantity,
            'price': "{:.2f}".format(float(obj.price)),
            'total_price' : "{:.2f}".format(float(obj.total_price)),
            'discount_price' : "{:.2f}".format(float(obj.discount_price)),
            'trans_amt' : "{:.2f}".format(float(obj.trans_amt)),
            'deposit' : "{:.2f}".format(float(obj.deposit)),
            'treatment_no': obj.treatment_no,
            'free_sessions' : obj.free_sessions,
            'discount' : "{:.2f}".format(float(obj.discount)),
            'discount_amt' : "{:.2f}".format(float(obj.discount_amt)),
            'tmp_treatment' : data,
            'disc_lst' : disc_lst,
            'is_total' : obj.is_total,
            'sessiondone': obj.sessiondone if obj.sessiondone else "",
            'is_done': is_done,
            'tstaff' : lst,
            'is_treat' : False if obj.treatment_no else True,
            'is_service' : obj.is_service
            }
       
        return mapped_object


class CourseTmpSerializer(serializers.ModelSerializer): 

    id = serializers.IntegerField(source='pk',required=False)
    cart_id = serializers.SerializerMethodField() 
    treatment_no = serializers.SerializerMethodField()
    free_sessions = serializers.SerializerMethodField() 
    total_price = serializers.SerializerMethodField() 
    disc_amount = serializers.SerializerMethodField() 
    disc_percent = serializers.SerializerMethodField() 
    unit_price = serializers.SerializerMethodField()
    auto_propation = serializers.SerializerMethodField() 
 

    def get_cart_id(self, obj):
        return None 

    def get_treatment_no(self, obj):
        return None 

    def get_free_sessions(self, obj):
        return None     

    def get_total_price(self, obj):
        return None  

    def get_disc_amount(self, obj):
        return None 

    def get_disc_percent(self, obj):
        return None  

    def get_unit_price(self, obj):
        return None 

    def get_auto_propation(self, obj):
        return None     
       
        
    class Meta:
        model = Tmptreatment
        fields = ['id','cart_id','treatment_no','free_sessions','total_price','disc_amount',
        'disc_percent','unit_price','auto_propation']


class CartPrepaidSerializer(serializers.ModelSerializer): 

    class Meta:
        model = ItemCart
        fields = ['id','itemdesc','quantity','price','trans_amt','deposit',
        'prepaid_value','isopen_prepaid']


    def to_representation(self, obj):
        # print(obj.prepaid_value,"obj.prepaid_value")
        if obj.prepaid_value == None:
            prepaid_value = "{:.2f}".format(float(obj.itemcodeid.prepaid_value)),
        else:
            prepaid_value = "{:.2f}".format(obj.prepaid_value),

        # print(prepaid_value,"prepaid_value")   
        mapped_object = {
            'id': obj.id,
            'itemdesc' : obj.itemdesc,
            'quantity': obj.quantity,
            'price': "{:.2f}".format(float(obj.price)),
            'trans_amt' : "{:.2f}".format(float(obj.trans_amt)),
            'deposit' : "{:.2f}".format(float(obj.deposit)),
            'prepaid_value' : prepaid_value[0],
            'isopen_prepaid' : obj.isopen_prepaid,
            }
       
        return mapped_object

    
class ChangePaymentDateSerializer(serializers.ModelSerializer): 
   
    class Meta:
        model = PosHaud
        fields = ['id','sa_transacno']


class AddRemoveSalesStaffSerializer(serializers.ModelSerializer): 
   
    class Meta:
        model = PosHaud
        fields = ['id',]


class DateFormatSerializer(serializers.ModelSerializer):
    def datetime_formatting(self,instance):
        splt = str(instance.created_at).split(" ")
        created_at = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
        mapped_object = {'created_at': created_at if created_at else ''}
        return mapped_object

class ItemSitelistSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemSitelist
        fields = '__all__'

class TimeLogSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = TimeLogModel
        fields = '__all__'



class QPOItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = '__all__'
 
class ProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ProjectModel
        fields = '__all__'
        
class ActivitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ActivityModel
        fields = '__all__'

class QuotationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = QuotationModel
        fields = '__all__'

class ManualInvoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ManualInvoiceModel
        fields = '__all__'

class WorkOrderInvoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = WorkOrderInvoiceModel
        fields = '__all__'
            

class POSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = POModel
        fields = '__all__'

class QuotationAddrSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = QuotationAddrModel
        fields = '__all__'

class ManualInvoiceAddrSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ManualInvoiceAddrModel
        fields = '__all__'


class WorkOrderInvoiceAddrSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = WorkOrderInvoiceAddrModel
        fields = '__all__'

class POAddrSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = POAddrModel
        fields = '__all__'

class QuotationDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = QuotationDetailModel
        fields = '__all__'

class ManualInvoiceDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ManualInvoiceDetailModel
        fields = '__all__'

class WorkOrderDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = WorkOrderInvoiceDetailModel
        fields = '__all__'


class PODetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = PODetailModel
        fields = '__all__'

class QuotationItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = QuotationItemModel
        fields = '__all__'

class ManualInvoiceItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ManualInvoiceItemModel
        fields = '__all__'

class WorkOrderInvoiceItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = WorkOrderInvoiceItemModel
        fields = '__all__'


class POItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = POItemModel
        fields = '__all__'




class SystemLogSerializer(serializers.ModelSerializer):
    ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = SystemLogModel
        fields = '__all__'


class POApprovalSerializer(serializers.ModelSerializer):
    POAPP_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = POApprovalModel
        fields = '__all__'

class ItemUOMPriceSerializer(serializers.ModelSerializer):
    ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemUOMPriceModel
        fields = '__all__'


class ItemBatchSerializer(serializers.ModelSerializer):
    ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemBatchModel
        fields = '__all__'

class ItemBrandSerializer(serializers.ModelSerializer):
    itm_id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemBrandModel
        fields = '__all__'


class ItemRangeSerializer(serializers.ModelSerializer):
    itm_id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemRangeModel
        fields = '__all__'

class ItemDeptSerializer(serializers.ModelSerializer):
    itm_id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemDeptModel
        fields = '__all__'


class EmployeeListSerializer(serializers.ModelSerializer):
    Emp_no = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = EmployeeListModel
        fields = '__all__'

class SiteCodeSerializer(serializers.ModelSerializer):
    ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = SiteCodeModel
        fields = '__all__'

class ItemSupplySerializer(serializers.ModelSerializer):
    SPLY_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemSupplyModel
        fields = '__all__'

class DOSerializer(serializers.ModelSerializer):
    DO_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = DOModel
        fields = '__all__'



class DODetailSerializer(serializers.ModelSerializer):
    DO_Detail_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = DODetailModel
        fields = '__all__'



class AuthoriseSerializer(serializers.ModelSerializer):
    PW_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = AuthoriseModel
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    Item_no = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = StockModel
        fields = '__all__'

class MovHdrSerializer(serializers.ModelSerializer):
    PO_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = MovHdrModel
        fields = '__all__'

class MovDtlSerializer(serializers.ModelSerializer):
    DOC_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = MovDtlModel
        fields = '__all__'

class StktrnSerializer(serializers.ModelSerializer):
    ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = StktrnModel
        fields = '__all__'

class PHYHdrSerializer(serializers.ModelSerializer):
    PHY_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = PHYHdrModel
        fields = '__all__'

class PHYDtlSerializer(serializers.ModelSerializer):
    PHY_ID = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = PHYDtlModel
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = City
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = State
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Country
        fields = '__all__'

class DropdownSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = DropdownModel
        fields = '__all__'

class SupplyContactInfoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = SupplyContactInfoModel
        fields = '__all__'

class ControlNoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ControlNoModel
        fields = '__all__'


class CommissionProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    #employe_level_id = serializers.PrimaryKeyRelatedField(queryset=EmpLevel.objects.all(pk=int(request.data['employe_level_id']))).first()
    
    class Meta:
        model = CommissionProfile
               
        fields = ['id','employe_level_id','profile_name','period','from_date','to_date','min_value','max_value',
                    'commission','ispercent','incentive','incentive_ispercent','range_id','brand_id','department_id',
                    'commission_type','rangee_comm_id','brand_comm_id','department_comm_id']

class CommTargetSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommTarget
        fields = ['id','profile_name','from_date_comm','to_date_comm','min_value_comm','max_value_comm','commission_comm',
        'ispercent_comm','incentive_comm','incentive_ispercent_comm']

class CommDeductionSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = CommDeduction
        fields = ['id','profile_name','gst','gst_ispercent','bank_changes','bc_ispercent','emi',
        'emi_ispercent']

class SalarySubTypeLookupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = SalarySubTypeLookup
        fields = ['id','typename','accountcode','showinallowance','showindeduction','showinpayment']

class ModeOfPaymentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ModeOfPayment
        fields = ['id','modename','accountcode']

