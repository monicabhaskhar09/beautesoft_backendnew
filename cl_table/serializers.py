from rest_framework import serializers
from .models import (Gender,Employee,  Fmspw,  Attendance2, Customer, Images, Treatment, Stock , 
EmpSitelist, ItemClass, ItemRange,PackageDtl, Appointment,ItemDept, Treatment_Master,PayGroup,Paytable,
PosTaud,PosDaud,PosHaud,ItemStatus,Source,Securities,ScheduleHour,ApptType,TmpItemHelper,FocReason,
BlockReason,AppointmentLog,Title, Workschedule, CustomerFormControl,Country,State,Language,
CustomerClass, RewardPolicy, RedeemPolicy, Diagnosis, DiagnosisCompare, Securitylevellist,
DailysalesdataDetail, DailysalesdataSummary,Holditemdetail,PrepaidAccount,CreditNote,TreatmentAccount,
DepositAccount, CustomerPoint, MrRewardItemType,Smsreceivelog,Systemsetup,TreatmentProtocol,
CustomerTitle,ItemDiv,Tempcustsign,CustomerDocument,TreatmentPackage,ContactPerson,ItemFlexiservice)
from cl_app.models import ItemSitelist, SiteGroup
from custom.models import EmpLevel,Room,VoucherRecord
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from rest_framework import status
import datetime as dt
from django.db.models import Q
import datetime
from django.db.models import Count
from django.db.models import Sum
from datetime import date
from django.db.models.functions import Coalesce

from .utils import code_generator

def get_client_ip(request):
    # url = request.build_absolute_uri()
    # ip = url.split('api')
    # string = ""
    # for idx, val in enumerate(ip[0]):
    #     if idx != 21:
    #         string += val
    ip_str = str("http://"+request.META['HTTP_HOST'])
    return ip_str
  
# class GenderSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Gender
#         fields = '__all__'
#         read_only_fields = ('itm_isactive', 'Sync_LstUpd','created_at') 

class FMSPWSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(source='pk',required=False)
    sitecode = serializers.CharField(source='loginsite.itemsite_code',required=False)
    empcode = serializers.CharField(source='Emp_Codeid.emp_code',required=False)

    class Meta:
        model = Fmspw
        fields = ['id','pw_userlogin','pw_password','LEVEL_ItmIDid','level_desc','Emp_Codeid','empcode','user','loginsite','sitecode']
        read_only_fields = ('pw_isactive','level_desc','user','created_at') 

    def validate(self, data):
        if 'LEVEL_ItmIDid' in data:
            if data['LEVEL_ItmIDid'] is not None:
                if Securities.objects.filter(pk=data['LEVEL_ItmIDid'].pk,level_isactive=False):
                    raise serializers.ValidationError("Securities ID Does not exist!!")

                if not Securities.objects.filter(pk=data['LEVEL_ItmIDid'].pk,level_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Securities Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

        if 'Emp_Codeid' in data:
            if data['Emp_Codeid'] is not None:
                if Employee.objects.filter(pk=data['Emp_Codeid'].pk,emp_isactive=False):
                    raise serializers.ValidationError("Employee ID Does not exist!!")

                if not Employee.objects.filter(pk=data['Emp_Codeid'].pk,emp_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
     
        return data        


class UserLoginSerializer(serializers.Serializer):

    salon = serializers.IntegerField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True,style={'input_type': 'password'})

    default_error_messages = {
        'inactive_account': _('User account is disabled.'),
        'invalid_credentials': _('Unable to login with provided credentials.'),
        'invalid_user' : _('Invalid Username.'),
        'invalid_branch' : _('Salon Does not exist.'),
        'invalid' : _('Salon Does not match with User salon.'),
        'site_notmapped' : _('Users is not allowed to login in this site'),
        'sitegrp_notmapped' : _('Site Group is not mapped'),

    }

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        if attrs.get("salon"):
           branch = ItemSitelist.objects.filter(pk=attrs.get("salon"),itemsite_isactive=True) 
           if not branch:
                raise serializers.ValidationError(self.error_messages['invalid_branch']) 

        if User.objects.filter(username=attrs.get("username")):
            self.user = authenticate(username=attrs.get("username"), password=attrs.get('password'))
            if self.user:
                if not self.user.is_active:
                    raise serializers.ValidationError(self.error_messages['inactive_account'])

                fmspw = Fmspw.objects.filter(user=self.user.id,pw_isactive=True)
                if not fmspw:
                    raise serializers.ValidationError(self.error_messages['inactive_account'])

                emp = fmspw[0].Emp_Codeid.pk
                #sitelist_ids = EmpSitelist.objects.filter(Emp_Codeid=emp,Site_Codeid=branch[0].pk,isactive=True)
                #if not sitelist_ids:
                #    raise serializers.ValidationError(self.error_messages['site_notmapped'])

                #if int(sitelist_ids[0].Site_Codeid.pk) != int(attrs.get("salon")):
                #    raise serializers.ValidationError(self.error_messages['invalid']) 

                #if not branch[0].Site_Groupid:
                #    raise serializers.ValidationError(self.error_messages['sitegrp_notmapped'])

                return attrs
            else:
                raise serializers.ValidationError(self.error_messages['invalid_credentials'])
        else:
            raise serializers.ValidationError(self.error_messages['invalid_user']) 

        
class CustomerSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    gender = serializers.CharField(source='Cust_sexesid.itm_name',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_code','cust_name','cust_address','Site_Codeid','site_name','site_code','last_visit',
        'upcoming_appointments','cust_dob','cust_phone2','Cust_sexesid','gender','cust_email','prepaid_card',
        'cust_nric','cust_country','cust_state','cust_postcode','cust_language','cust_source','emergencycontact',
        'cardno1','cardno2','cardno3','cardno4','cardno5','cust_class','cust_title','cust_phone1',
        'creditnote','voucher_available','oustanding_payment','cust_refer','custallowsendsms','cust_maillist','cust_corporate']
        read_only_fields = ('cust_isactive','created_at', 'updated_at','last_visit','upcoming_appointments',
        'Site_Code','cust_code','ProneToComplain') 
        extra_kwargs = {'cust_name': {'required': True},'cust_address':{'required': True}} 


    def validate(self, data):
        request = self.context['request']
        if not 'cust_name' in request.data:
            raise serializers.ValidationError("cust_name Field is required.")
        else:
            if request.data['cust_name'] is None:
                raise serializers.ValidationError("cust_name Field is required.")
        # if not 'cust_address' in request.data:
        #     raise serializers.ValidationError("cust_address Field is required.")
        # else:
        #     if request.data['cust_address'] is None:
        #         raise serializers.ValidationError("cust_address Field is required.")
        # if not 'cust_dob' in request.data:
        #     raise serializers.ValidationError("cust_dob Field is required.")
        # else:
        #     if request.data['cust_dob'] is None:
        #         raise serializers.ValidationError("cust_dob Field is required.")
        if not 'cust_phone2' in request.data:
            raise serializers.ValidationError("cust_phone2 Field is required.")
        else:
            if request.data['cust_phone2'] is None:
                raise serializers.ValidationError("cust_phone2 Field is required.")
        # if not 'Cust_sexesid' in request.data:
        #     raise serializers.ValidationError("Cust_sexesid Field is required.")
        # else:
        #     if request.data['Cust_sexesid'] is None:
        #         raise serializers.ValidationError("Cust_sexesid Field is required.")
        # if not 'Site_Codeid' in request.data:
        #     raise serializers.ValidationError("Site_Codeid Field is required.")
        # else:
        #     if request.data['Site_Codeid'] is None:
        #         raise serializers.ValidationError("Site_Codeid Field is required.")
        
        if 'Cust_sexesid' in data:
            if data['Cust_sexesid'] is not None:
                if Gender.objects.filter(pk=data['Cust_sexesid'].pk,itm_isactive=False):
                    raise serializers.ValidationError("Gender ID Does not exist!!")

                if not Gender.objects.filter(pk=data['Cust_sexesid'].pk,itm_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Gender Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
        if 'Site_Codeid' in data:
            if data['Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")
        
        # if not 'cust_maillist' in request.data:
        #     raise serializers.ValidationError("cust_maillist Field is required.")
        # else:
        #     if request.data['cust_maillist'] is None:
        #         raise serializers.ValidationError("cust_maillist Field is required.")
        # if not 'custallowsendsms' in request.data:
        #     raise serializers.ValidationError("custallowsendsms Field is required.")
        # else:
        #     if request.data['custallowsendsms'] is None:
        #         raise serializers.ValidationError("custallowsendsms Field is required.")    
        # Email and Mobile number validation
        if request.data['cust_email']:
            customer_mail =  Customer.objects.filter(cust_email=request.data['cust_email'])
            if len(customer_mail) > 0:
                raise serializers.ValidationError("Email id is already associated with another account")
        customer =  Customer.objects.filter(cust_phone2=request.data['cust_phone2'])
        if len(customer) > 0:
            raise serializers.ValidationError("Mobile number is already associated with another account")
        return data    


class CustomerdetailSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_code','cust_name','cust_address',
        'cust_dob','cust_phone2','Cust_sexesid','cust_email','cust_joindate']

    def to_representation(self, obj):
        request = self.context['request']
        cust_dob = ''; cust_joindate = ''; cust_img = ''
        ip = "http://"+request.META['HTTP_HOST']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
        site = fmspw[0].loginsite
       
        if obj.cust_img:
            cust_img = ip+str(obj.cust_img.url)

        if obj.cust_dob:
            cust_dob = datetime.datetime.strptime(str(obj.cust_dob), "%Y-%m-%d").strftime("%d-%m-%Y")
        
        if obj.cust_joindate:
            splt = str(obj.cust_joindate).split(" ") 
            cust_joindate = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")


        total_inv = PosHaud.objects.filter(sa_custno=obj.cust_code,
        sa_transacno_type="Receipt",isvoid=False).only('sa_custno','sa_transacno_type').count()

        appt_ids = Appointment.objects.filter(appt_isactive=True,cust_no=obj.cust_code,
        appt_date__gte=date.today()).only('appt_isactive','cust_no','appt_date').count()
        
        appointment = "{0} appointments (upcoming)".format(str(appt_ids))        

        tr_open_ids = Treatment.objects.filter(cust_code=obj.cust_code,status="Open"
        ).only('cust_code','status').count()

        package_ids = Treatment.objects.filter(cust_code=obj.cust_code,status="Open").values('treatment_parentcode',
        ).order_by('treatment_parentcode').annotate(total=Count('treatment_parentcode'))
        # print(package_ids,"package_ids")

        if package_ids:
            package = len(package_ids)
        else:
            package = "0"


        tr_balance = 0.0 ; tr_outstanding = 0.0

        tr_acc = TreatmentAccount.objects.filter(cust_code=obj.cust_code,type='Deposit').exclude(sa_status="VOID").only('cust_code','type').order_by('pk')
        
        for i in tr_acc: 
            last_tracc_ids = TreatmentAccount.objects.filter(ref_transacno=i.sa_transacno,
            treatment_parentcode=i.treatment_parentcode
            ).only('ref_transacno','treatment_parentcode').order_by('-pk').first()
            if last_tracc_ids:
                tr_balance += last_tracc_ids.balance if last_tracc_ids.balance else 0
                tr_outstanding += last_tracc_ids.outstanding if last_tracc_ids.outstanding else 0 
        
        service_package = "{0} Sessions in {1} packages Balance: ${2} Outstanding: ${3}".format(str(tr_open_ids),str(package),str("{:.2f}".format(float(tr_balance))),str("{:.2f}".format(float(tr_outstanding))))        
        
        dp_balance = 0.0 ; dp_outstanding = 0.0 ; hold_qty = 0
        dep_acc = DepositAccount.objects.filter(cust_code=obj.cust_code,
        type='Deposit').only('cust_code','type').order_by('pk')
        for j in dep_acc:
            de_acc_ids = DepositAccount.objects.filter(sa_transacno=j.sa_transacno,
            ref_productcode=j.ref_productcode).only('sa_transacno','ref_productcode').order_by('-pk').first()
            # print(de_acc_ids,"de_acc_ids")
            # print(de_acc_ids.balance,"de_acc_ids.balance")
            if de_acc_ids and not de_acc_ids.balance is None and de_acc_ids.balance > 0:
                # print("iff")
                holdids = Holditemdetail.objects.filter(sa_transacno=de_acc_ids.sa_transacno,
                itemno=de_acc_ids.item_barcode,
                sa_custno=de_acc_ids.cust_code,status='OPEN').only('sa_transacno','itemno').order_by('pk').last()  
                # print(holdids,"holdids")
                # print(holdids or not de_acc_ids.outstanding is None and de_acc_ids.outstanding > 0,"kk")
                # print(de_acc_ids.outstanding,"print(de_acc_ids.outstanding)")       
                
                if holdids or not de_acc_ids.outstanding is None and de_acc_ids.outstanding > 0: 
                    dp_balance += de_acc_ids.balance if de_acc_ids.balance else 0

            if de_acc_ids:     
                dp_outstanding += de_acc_ids.outstanding if de_acc_ids.outstanding else 0

            holdids = Holditemdetail.objects.filter(sa_transacno=j.sa_transacno,
            itemno=j.item_barcode,sa_custno=obj.cust_code).only('sa_transacno','itemno',
            'sa_custno').order_by('-pk').first() 
            if holdids:
                hold_qty += holdids.holditemqty if holdids.holditemqty else 0
        
        product = "{0} Item on Hold Balance: {1} Outstanding: ${2}".format(str(hold_qty),str("{:.2f}".format(float(dp_balance))),str("{:.2f}".format(float(dp_outstanding))))             


        pre_balance = 0.0 ; pre_outstanding = 0.0

        prepaid_cnt = PrepaidAccount.objects.filter(cust_code=obj.cust_code,
        status=True,remain__gt=0).only('remain','cust_code','sa_status').order_by('pk').count()
       
        pre_acc = PrepaidAccount.objects.filter(cust_code=obj.cust_code,
        status=True,remain__gt=0).only('remain','cust_code','sa_status').order_by('pk')
        for i in pre_acc:
            lst_preacc_ids = PrepaidAccount.objects.filter(pp_no=i.pp_no,
            status=True,line_no=i.line_no).order_by('-pk').only('pp_no','status','line_no').first()
            if lst_preacc_ids:
                pre_balance += lst_preacc_ids.remain if lst_preacc_ids.remain else 0
                pre_outstanding += lst_preacc_ids.outstanding if lst_preacc_ids.outstanding else 0
                       
        prepaid = "Balance: {0} (in {1} cards) Outstanding {2}".format(str("{:.2f}".format(float(pre_balance))),str(prepaid_cnt),str("{:.2f}".format(float(pre_outstanding))))        

        credit_ids = CreditNote.objects.filter(cust_code=obj.cust_code, status='OPEN'
        ).only('cust_code','status').order_by('pk').count()

        credit = CreditNote.objects.filter(cust_code=obj.cust_code, status='OPEN'
        ).only('cust_code','status').order_by('pk').aggregate(amount=Coalesce(Sum('balance'), 0))
        if credit['amount'] > 0.0:
            credit_amt = "{:.2f}".format(credit['amount'])
        else:
            credit_amt = "0.00"  

        credit_val = "${0} (in {1} credit note)".format(str("{:.2f}".format(float(credit_amt))),str(credit_ids))               

          
        voucherids = VoucherRecord.objects.filter(isvalid=True,cust_code=obj.cust_code,
        used=False).order_by('-pk').count() 

        voucher_ids = VoucherRecord.objects.filter(isvalid=True,cust_code=obj.cust_code,
        used=False).order_by('-pk').aggregate(amount=Coalesce(Sum('value'), 0))

        if voucher_ids['amount'] > 0.0:
            voucher_amt = "{:.2f}".format(voucher_ids['amount'])
        else:
            voucher_amt = "0.00"

        voucher = "${0} (in {1} vouchers)".format(str("{:.2f}".format(float(voucher_amt))),str(voucherids))
        
        form_control_qs = CustomerFormControl.objects.filter(isActive=True,Site_Codeid=site) 
        
        cust_address = ""
        for f in form_control_qs:
            if f.field_name == 'cust_address':
                cust_address += str(obj.cust_address)
            if f.field_name == 'cust_address1':
                cust_address += " "+str(obj.cust_address1)
            if f.field_name == 'cust_address2':
                cust_address += " "+str(obj.cust_address2)
            if f.field_name == 'cust_address3':
                cust_address += " "+str(obj.cust_address3)  
            if f.field_name == 'sgn_block':
                cust_address += " "+str(obj.sgn_block) 
            if f.field_name == 'sgn_unitno':
                cust_address += " "+str(obj.sgn_unitno) 
            if f.field_name == 'sgn_street':
                cust_address += " "+str(obj.sgn_street) 
            if f.field_name == 'cust_postcode':
                cust_address += " "+str(obj.cust_postcode) 
        
        system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
        value_name='Other Outlet Customer Listings',isactive=True).first()

        system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Edit',
        value_name='Other Outlet Customer Edit',isactive=True).first()
           
        is_allowedit = False
        if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
            if obj.site_code != site.itemsite_code or obj.site_code == site.itemsite_code:
                is_allowedit = True
        else:
            if obj.site_code == site.itemsite_code: 
                is_allowedit = True

       

        mapped_object = {'id': obj.pk,'cust_code':obj.cust_code,'cust_name':obj.cust_name,
        'cust_address': cust_address,
        'cust_dob': cust_dob, 'cust_phone2': obj.cust_phone2 if obj.cust_phone2 else obj.cust_phone1 if obj.cust_phone1 else obj.cust_phoneo if obj.cust_phoneo else obj.phone4 if obj.phone4 else "",
        'Cust_sexesid': obj.Cust_sexesid.pk if obj.Cust_sexesid else "", 
        'cust_email': obj.cust_email if obj.cust_email else "",
        'cust_refer': obj.cust_refer if obj.cust_refer else '',
        'join_date': cust_joindate,
        'total_invoice': total_inv,
        'service_session' : tr_open_ids,
        'service_packages' : package,
        'service_balance' : "{:.2f}".format(float(tr_balance)),
        'service_outstanding' : "{:.2f}".format(float(tr_outstanding)),
        'prepaid_balance' : "{:.2f}".format(float(pre_balance)),
        'prepaid_card': prepaid_cnt,
        'prepaid_outstanding' : "{:.2f}".format(float(pre_outstanding)),
        'product_hold' : hold_qty,
        'product_balance' : "{:.2f}".format(float(dp_balance)),
        'product_outstanding' : "{:.2f}".format(float(pre_outstanding)),
        'credit_amount' : "{:.2f}".format(float(credit_amt)),
        'credit_count': credit_ids,
        'voucher_amount': "{:.2f}".format(float(voucher_amt)),
        'voucher_count': voucherids,
        'appoint' : appointment,
        'cust_img': cust_img,
        'is_allowedit':is_allowedit
        }
        return mapped_object    
       

class CustomerUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    gender = serializers.CharField(source='Cust_sexesid.itm_name',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_name','cust_address','Site_Codeid','site_name',
        'cust_dob','cust_phone2','Cust_sexesid','gender',
        'cust_email','custallowsendsms','cust_maillist']

    def validate(self, data):
        pk = self.instance.pk
        # Email and Mobile number validation
        customer_mail =  Customer.objects.filter(cust_email=data['cust_email']).exclude(pk=pk)
        if len(customer_mail) > 0:
            raise serializers.ValidationError("Email id is already associated with another account")
        customer =  Customer.objects.filter(cust_phone2=data['cust_phone2']).exclude(pk=pk)
        if len(customer) > 0:
            raise serializers.ValidationError("Mobile number is already associated with another account")
        return data


class CustomerallSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_name']

class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['id','image']

class StockListTreatmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','treatment_details','procedure','Stock_PIC']

class ServicesSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    images = ImagesSerializer(source='images_set', many=True, read_only=True)
    category_name = serializers.CharField(source='Item_Classid.itm_desc',required=False)
    type_name = serializers.CharField(source='Item_Rangeid.itm_desc',required=False)


    class Meta:
        model = Stock
        fields = ['id','item_desc','Item_Classid','category_name','item_price','tax','itm_disc','sutiable_for',
        'description','Item_Rangeid','type_name','images']
        read_only_fields = ('updated_at','item_isactive','category_name','Item_Class')
        

    def validate(self, data):
        request = self.context['request']
        if not 'item_desc' in request.data:
            raise serializers.ValidationError("item_desc Field is required.")
        else:
            if request.data['item_desc'] is None:
                raise serializers.ValidationError("item_desc Field is required.")
        if not 'Item_Classid' in request.data:
            raise serializers.ValidationError("Item_Classid Field is required.")
        else:
            if request.data['Item_Classid'] is None:
                raise serializers.ValidationError("Item_Classid Field is required.")
        if not 'item_price' in request.data:
            raise serializers.ValidationError("item_price Field is required.")
        else:
            if request.data['item_price'] is None:
                raise serializers.ValidationError("item_price Field is required.")
        if not 'tax' in request.data:
            raise serializers.ValidationError("tax Field is required.")
        else:
            if request.data['tax'] is None:
                raise serializers.ValidationError("tax Field is required.")
        if not 'itm_disc' in request.data:
            raise serializers.ValidationError("itm_disc Field is required.")
        else:
            if request.data['itm_disc'] is None:
                raise serializers.ValidationError("itm_disc Field is required.")

        if 'Item_Classid' in data:
            if data['Item_Classid'] is not None:
                if ItemClass.objects.filter(pk=data['Item_Classid'].pk,itm_isactive=False):
                    raise serializers.ValidationError("Category ID Does not exist!!")
                if not ItemClass.objects.filter(pk=data['Item_Classid'].pk,itm_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Category Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
     
        if 'Item_Rangeid' in data:
            if data['Item_Rangeid'] is not None:
                if ItemRange.objects.filter(pk=data['Item_Rangeid'].pk,itm_status=False):
                    raise serializers.ValidationError("Type ID Does not exist!!")
                if not ItemRange.objects.filter(pk=data['Item_Rangeid'].pk,itm_status=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Type Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)                        
        return data      
        
    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        stock = Stock.objects.create(item_desc=validated_data.get('item_desc'),Item_Classid=validated_data.get('Item_Classid'),
        item_price=validated_data.get('item_price'),tax=validated_data.get('tax'),itm_disc=validated_data.get('itm_disc'),
        sutiable_for=validated_data.get('sutiable_for'),description=validated_data.get('description'),
        Item_Rangeid=validated_data.get('Item_Rangeid'),item_code=validated_data.get('item_code'))
 
       
        for image_data in images_data.values():
            Images.objects.create(services=stock, image=image_data)
        return stock 

    def update(self, instance, validated_data):
        images_data = self.context.get('view').request.FILES
        instance.item_desc = validated_data.get("item_desc", instance.item_desc)
        instance.Item_Classid = validated_data.get("Item_Classid", instance.Item_Classid)
        instance.item_price = validated_data.get("item_price", instance.item_price)
        instance.tax = validated_data.get("tax", instance.tax)
        instance.itm_disc = validated_data.get("itm_disc", instance.itm_disc)
        instance.sutiable_for = validated_data.get("sutiable_for", instance.sutiable_for)
        instance.description = validated_data.get("description", instance.description)
        instance.Item_Rangeid = validated_data.get("Item_Rangeid", instance.Item_Rangeid)
        

        if self.context['request'].method == 'PUT': 
            if images_data:
                # instance.images_set.all().delete()
                for image_data in images_data.values():
                    Images.objects.create(services=instance, image=image_data)

        instance.save()    
          
        return instance

class ItemSiteListAPISerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemSitelist
        fields = ['id','itemsite_desc','itemsite_code']


class ItemSiteListSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    skills = serializers.SerializerMethodField() 
    images = ImagesSerializer(source='images_set', many=True, read_only=True)
    salon_name = serializers.CharField(source='Site_Groupid.description',required=False)

    def get_skills(self, obj):
        if obj.services:
            string = ""
            for i in obj.services.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None 


    class Meta:
        model = ItemSitelist
        fields = ['id','skills_list','itemsite_desc','itemsite_code','Site_Groupid','salon_name','skills','services',
        'itemsite_phone1','itemsite_date','itemsite_email','images']
        read_only_fields = ('created_at', 'updated_at','itemsite_isactive')


    def validate(self, data):
        request = self.context['request']
        if not 'itemsite_desc' in request.data:
            raise serializers.ValidationError("itemsite_desc Field is required.")
        else:
            if request.data['itemsite_desc'] is None:
                raise serializers.ValidationError("itemsite_desc Field is required.")
        if not 'itemsite_date' in request.data:
            raise serializers.ValidationError("itemsite_date Field is required.")
        else:
            if request.data['itemsite_date'] is None:
                raise serializers.ValidationError("itemsite_date Field is required.")
        if not 'Site_Groupid' in request.data:
            raise serializers.ValidationError("Site_Groupid Field is required.")
        else:
            if request.data['Site_Groupid'] is None:
                raise serializers.ValidationError("Site_Groupid Field is required.")
        if not 'skills_list' in request.data:
            raise serializers.ValidationError("skills_list Field is required.")
        else:
            if request.data['skills_list'] is None:
                raise serializers.ValidationError("skills_list Field is required.")
        if not 'itemsite_phone1' in request.data:
            raise serializers.ValidationError("itemsite_phone1 Field is required.")
        else:
            if request.data['itemsite_phone1'] is None:
                raise serializers.ValidationError("itemsite_phone1 Field is required.")
        if not 'itemsite_email' in request.data:
            raise serializers.ValidationError("itemsite_email Field is required.")
        else:
            if request.data['itemsite_email'] is None:
                raise serializers.ValidationError("itemsite_email Field is required.")
        if not 'itemsite_code' in request.data:
            raise serializers.ValidationError("itemsite_code Field is required.")
        else:
            if request.data['itemsite_code'] is None:
                raise serializers.ValidationError("itemsite_code Field is required.")
            
        if 'Site_Groupid' in data:
            if data['Site_Groupid'] is not None:
                if SiteGroup.objects.filter(id=data['Site_Groupid'].id,is_active=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not SiteGroup.objects.filter(id=data['Site_Groupid'].id,is_active=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Branch Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)      

        if 'services' in data:
            if data['services'] is not None:
                for t in data['services']:
                    if Stock.objects.filter(pk=t.pk,item_isactive=False):
                        raise serializers.ValidationError("Services ID Does not exist!!") 
                     

        if 'skills_list' in data:
            if data['skills_list'] is not None:
                if ',' in data['skills_list']:
                    res = data['skills_list'].split(',')
                else:
                    res = data['skills_list'].split(' ')
                for t in res:
                    id_val = int(t)
                    if Stock.objects.filter(pk=id_val,item_isactive=False):
                        raise serializers.ValidationError("Services ID Does not exist!!")    
                    if not Stock.objects.filter(pk=id_val,item_isactive=True):
                        raise serializers.ValidationError("Services ID Does not exist!!")    
                                   
        return data

    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        site_id = ItemSitelist.objects.create(itemsite_code=validated_data.get('itemsite_code'),
        itemsite_desc=validated_data.get('itemsite_desc'),itemsite_date=validated_data.get('itemsite_date'),
        itemsite_phone1=validated_data.get('itemsite_phone1'),itemsite_email=validated_data.get('itemsite_email'),
        Site_Groupid=validated_data.get('Site_Groupid'))
        
        skills_data = validated_data.pop('skills_list')
        if ',' in skills_data:
            res = skills_data.split(',')
        else:
            res = skills_data.split(' ')

        for service in res:
            site_id.services.add(service)

        for image_data in images_data.values():
            Images.objects.create(item_sitelist=site_id, image=image_data)
    
        return site_id 

    def update(self, instance, validated_data):
        images_data = self.context.get('view').request.FILES
        instance.itemsite_code = validated_data.get("itemsite_code", instance.itemsite_code)
        instance.itemsite_desc = validated_data.get("itemsite_desc", instance.itemsite_desc)
        instance.itemsite_date = validated_data.get("itemsite_date", instance.itemsite_date)
        instance.itemsite_phone1 = validated_data.get("itemsite_phone1", instance.itemsite_phone1)
        instance.itemsite_email = validated_data.get("itemsite_email", instance.itemsite_email)
        instance.Site_Groupid = validated_data.get("Site_Groupid", instance.Site_Groupid)

        if self.context['request'].method == 'PUT': 
            if images_data:
                # instance.images_set.all().delete()
                for image_data in images_data.values():
                    Images.objects.create(item_sitelist=instance, image=image_data)           


        skills_data = validated_data.pop('skills_list')
        if ',' in skills_data:
            res = skills_data.split(',')
        else:
            res = skills_data.split(' ')

        if skills_data:
            for existing in instance.services.all():
                instance.services.remove(existing) 

            for skill in res:
                instance.services.add(skill)

        instance.save()    
          
        return instance     


class EmployeeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    services =  serializers.SerializerMethodField() 
    gender = serializers.CharField(source='Emp_sexesid.itm_name',required=False)
    jobtitle_name = serializers.CharField(source='EMP_TYPEid.level_desc',required=False)
    shift_name = serializers.SerializerMethodField()
    level_desc = serializers.CharField(source='LEVEL_ItmIDid.level_description',required=False)
    site_name = serializers.CharField(source='defaultSiteCodeid.itemsite_desc',required=False)


    def get_shift_name(self, obj):
        if obj.shift:
            att = obj.shift
            return str(att.attn_time) +" "+ "to" +" "+str(att.attn_mov_in)
        else:
            return None    

    def get_services(self, obj):
        if obj.skills.all():
            string = ""
            for i in obj.skills.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None            


    class Meta:
        model = Employee
        fields = ['id','skills_list','emp_name','display_name','emp_phone1','emp_code','skills','services','emp_address',
        'Emp_sexesid','gender','defaultSiteCodeid','defaultsitecode','site_name','Site_Codeid','site_code',
        'emp_dob','emp_joindate','shift','shift_name','emp_email','emp_pic','EMP_TYPEid','jobtitle_name',
        'is_login','pw_password','LEVEL_ItmIDid','level_desc']
        read_only_fields = ('emp_isactive', 'updated_at','created_at','emp_code','branch') 
        extra_kwargs = {'emp_email': {'required': False},'Site_Codeid': {'required': False},
        'emp_name': {'required': True}}


    def validate(self, data):
        request = self.context['request']
        if not 'emp_name' in request.data:
            raise serializers.ValidationError("emp_name Field is required.")
        else:
            if request.data['emp_name'] is None:
                raise serializers.ValidationError("emp_name Field is required.")
        if not 'Emp_sexesid' in request.data:
            raise serializers.ValidationError("Emp_sexesid Field is required.")
        else:
            if request.data['Emp_sexesid'] is None:
                raise serializers.ValidationError("Emp_sexesid Field is required.")
        if not 'emp_phone1' in request.data:
            raise serializers.ValidationError("emp_phone1 Field is required.")
        else:
            if request.data['emp_phone1'] is None:
                raise serializers.ValidationError("emp_phone1 Field is required.")
        if not 'emp_address' in request.data:
            raise serializers.ValidationError("emp_address Field is required.")
        else:
            if request.data['emp_address'] is None:
                raise serializers.ValidationError("emp_address Field is required.")
        if not 'emp_dob' in request.data:
            raise serializers.ValidationError("emp_dob Field is required.")
        else:
            if request.data['emp_dob'] is None:
                raise serializers.ValidationError("emp_dob Field is required.")
        if not 'emp_joindate' in request.data:
            raise serializers.ValidationError("emp_joindate Field is required.")
        else:
            if request.data['emp_joindate'] is None:
                raise serializers.ValidationError("emp_joindate Field is required.")
        if not 'EMP_TYPEid' in request.data:
            raise serializers.ValidationError("EMP_TYPEid Field is required.")
        else:
            if request.data['EMP_TYPEid'] is None:
                raise serializers.ValidationError("EMP_TYPEid Field is required.")
        if not 'skills_list' in request.data:
            raise serializers.ValidationError("skills_list Field is required.")
        else:
            if request.data['skills_list'] is None:
                raise serializers.ValidationError("skills_list Field is required.")
        if not 'defaultSiteCodeid' in request.data:
            raise serializers.ValidationError("defaultSiteCodeid Field is required.")
        else:
            if request.data['defaultSiteCodeid'] is None:
                raise serializers.ValidationError("defaultSiteCodeid Field is required.")
        if not 'emp_pic' in request.data:
            raise serializers.ValidationError("emp_pic Field is required.")
        else:
            if request.data['emp_pic'] is None:
                raise serializers.ValidationError("emp_pic Field is required.")
            
        if 'skills_list' in data:
            if data['skills_list'] is not None:
                if ',' in data['skills_list']:
                    res = data['skills_list'].split(',')
                else:
                    res = data['skills_list'].split(' ')
                for t in res:
                    id_val = int(t)
                    if Stock.objects.filter(pk=id_val,item_isactive=False):
                        raise serializers.ValidationError("Services ID Does not exist!!")  

                    if not Stock.objects.filter(pk=id_val,item_isactive=True):
                        raise serializers.ValidationError("Services ID Does not exist!!")                
                                         
                                 
        if 'Emp_sexesid' in data:
            if data['Emp_sexesid'] is not None:
                if Gender.objects.filter(pk=data['Emp_sexesid'].pk,itm_isactive=False):
                    raise serializers.ValidationError("Gender ID Does not exist!!")
                if not Gender.objects.filter(pk=data['Emp_sexesid'].pk,itm_isactive=True):
                    raise serializers.ValidationError("Gender ID Does not exist!!")
 

        if 'shift' in data:
            if data['shift'] is not None:
                if Attendance2.objects.filter(pk=data['shift'].pk):
                    raise serializers.ValidationError("Shift ID Does not exist!!")
                if not Attendance2.objects.filter(pk=data['shift'].pk):
                    raise serializers.ValidationError("Shift ID Does not exist!!")


        if 'Site_Codeid' in data:
            if data['Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Branch ID Does not exist!!")


      
        if 'defaultSiteCodeid' in data:
            if data['defaultSiteCodeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['defaultSiteCodeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['defaultSiteCodeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Branch ID Does not exist!!")

        
        if 'EMP_TYPEid' in data:
            if data['EMP_TYPEid'] is not None:
                if EmpLevel.objects.filter(id=data['EMP_TYPEid'].id,level_isactive=False):
                    raise serializers.ValidationError("Job Title ID Does not exist!!") 
                if not EmpLevel.objects.filter(id=data['EMP_TYPEid'].id,level_isactive=True):
                    raise serializers.ValidationError("Job Title ID Does not exist!!")   
              
        return data       

    def create(self, validated_data):
        fmspw = Fmspw.objects.filter(user=self.context['request'].user,pw_isactive=True).first()
        Site_Codeid = fmspw.loginsite
        siteobj = ItemSitelist.objects.filter(pk=validated_data.get('defaultSiteCodeid').pk,itemsite_isactive=True).first()
        employee = Employee.objects.create(emp_name=validated_data.get('emp_name'),
        emp_phone1=validated_data.get('emp_phone1'),display_name=validated_data.get('emp_name'),
        emp_address=validated_data.get('emp_address'),Emp_sexesid=validated_data.get('Emp_sexesid'),emp_dob=validated_data.get('emp_dob'),
        emp_joindate=validated_data.get('emp_joindate'),shift=validated_data.get('shift'),defaultSiteCodeid=validated_data.get('defaultSiteCodeid'),
        defaultsitecode=siteobj.itemsite_code,emp_pic=validated_data.get('emp_pic'),is_login=validated_data.get('is_login'),
        EMP_TYPEid=validated_data.get('EMP_TYPEid'),Site_Codeid=Site_Codeid,site_code=Site_Codeid.itemsite_code)
        
        skills_data = validated_data.pop('skills_list')
        if ',' in skills_data:
            res = skills_data.split(',')
        else:
            res = skills_data.split(' ')
        for skill in res:
            employee.skills.add(skill)
        return employee 

    def update(self, instance, validated_data):
        instance.emp_name = validated_data.get("emp_name", instance.emp_name)
        instance.emp_phone1 = validated_data.get("emp_phone1", instance.emp_phone1)
        instance.emp_address = validated_data.get("emp_address", instance.emp_address)
        instance.Emp_sexesid = validated_data.get("Emp_sexesid", instance.Emp_sexesid)
        instance.emp_dob = validated_data.get("emp_dob", instance.emp_dob)
        instance.emp_joindate = validated_data.get("emp_joindate", instance.emp_joindate)
        instance.shift = validated_data.get("shift", instance.shift)
        instance.emp_pic = validated_data.get("emp_pic", instance.emp_pic)
        instance.EMP_TYPEid = validated_data.get("EMP_TYPEid", instance.EMP_TYPEid)
        instance.defaultSiteCodeid = validated_data.get("defaultSiteCodeid", instance.defaultSiteCodeid)
        instance.defaultsitecode = instance.defaultSiteCodeid.itemsite_code
        instance.Site_Codeid = validated_data.get("Site_Codeid", instance.Site_Codeid)
        instance.site_code = instance.Site_Codeid.itemsite_code

        if 'emp_email' in validated_data:
            if validated_data['emp_email'] is not None:
                instance.emp_email = validated_data.get("emp_email", instance.emp_email)

        skills_data = validated_data.pop('skills_list')
        if ',' in skills_data:
            res = skills_data.split(',')
        else:
            res = skills_data.split(' ')

        if skills_data:
            for existing in instance.skills.all():
                instance.skills.remove(existing) 

            for skill in res:
                instance.skills.add(skill)
        instance.save()    
        return instance    

class Attendance2Serializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    emp_name = serializers.CharField(source='Attn_Emp_codeid.emp_name',required=False)
    emp_img = serializers.ImageField(source='Attn_Emp_codeid.emp_pic',required=False)
    sitecode_name = serializers.CharField(source='Attn_Site_Codeid.itemsite_desc',required=False)
    shift_name = serializers.SerializerMethodField()

    def get_shift_name(self, obj):
        if obj:
            att = obj
            return str(att.attn_time) +" "+ "to" +" "+str(att.attn_mov_in) 
        else:
            return None  

    class Meta:
        model = Attendance2
        fields = ['id','shift_name','Attn_Emp_codeid','emp_name','emp_img','attn_date',
        'Attn_Site_Codeid','sitecode_name','attn_site_code','attn_time','attn_mov_in']
        read_only_fields = ('Create_date','Create_time', 'updated_at','emp_name','emp_img','attn_site_code')

    def validate(self, data):
        request = self.context['request']
        if not 'Attn_Emp_codeid' in request.data:
            raise serializers.ValidationError("Attn_Emp_codeid Field is required.")
        else:
            if request.data['Attn_Emp_codeid'] is None:
                raise serializers.ValidationError("Attn_Emp_codeid Field is required.")
        if not 'attn_date' in request.data:
            raise serializers.ValidationError("attn_date Field is required.")
        else:
            if request.data['attn_date'] is None:
                raise serializers.ValidationError("attn_date Field is required.")
        if not 'attn_time' in request.data:
            raise serializers.ValidationError("attn_time Field is required.")
        else:
            if request.data['attn_time'] is None:
                raise serializers.ValidationError("attn_time Field is required.")
        if not 'attn_mov_in' in request.data:
            raise serializers.ValidationError("attn_mov_in Field is required.")
        else:
            if request.data['attn_mov_in'] is None:
                raise serializers.ValidationError("attn_mov_in Field is required.")
        
        if 'Attn_Emp_codeid' in data:
            if data['Attn_Emp_codeid'] is not None:
                if Employee.objects.filter(pk=data['Attn_Emp_codeid'].pk,emp_isactive=False):
                    raise serializers.ValidationError("Employee ID Does not exist!!")
                if not Employee.objects.filter(pk=data['Attn_Emp_codeid'].pk,emp_isactive=True):
                        raise serializers.ValidationError("Employee ID Does not exist!!")


        if 'Attn_Site_Codeid' in data: 
            if data['Attn_Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Attn_Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Site ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Attn_Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Site ID Does not exist!!")

        return data
    
class AppointmentSerializer(serializers.ModelSerializer):   
    id = serializers.IntegerField(source='pk',required=False)
    cust_name = serializers.CharField(source='cust_noid.cust_name',required=False)
    source_name = serializers.CharField(source='Source_Codeid.source_desc',required=False)
    site_name = serializers.CharField(source='ItemSite_Codeid.itemsite_desc',required=False)


    class Meta:
        model = Appointment
        fields = ['id','appt_date','appt_code','appt_fr_time','appt_to_time','Appt_typeid','appt_type','cust_noid',
        'cust_name','appt_phone','new_remark','appt_created_by','Source_Codeid','source_name','Room_Codeid',
        'room_code','appt_status','emp_noid','emp_name','requesttherapist','ItemSite_Codeid','itemsite_code',
        'site_name','cust_refer','sec_status','walkin']
        read_only_fields = ('cust_name','appt_code')

    def validate(self, data):
        if 'cust_noid' in data:
            if data['cust_noid'] is not None:
                if Customer.objects.filter(pk=data['cust_noid'].pk,cust_isactive=False):
                    raise serializers.ValidationError("Customer ID Does not exist!!")
                if not Customer.objects.filter(pk=data['cust_noid'].pk,cust_isactive=True):
                    raise serializers.ValidationError("Customer ID Does not exist!!")
        
        if 'ItemSite_Codeid' in data:
            if data['ItemSite_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['ItemSite_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['ItemSite_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")

        if 'Source_Codeid' in data:
            if data['Source_Codeid'] is not None:
                if Source.objects.filter(id=data['Source_Codeid'].id,source_isactive=False):
                    raise serializers.ValidationError("Source ID Does not exist!!")
                if not Source.objects.filter(id=data['Source_Codeid'].id,source_isactive=True):
                    raise serializers.ValidationError("Source ID Does not exist!!")
                
        return data      
               
class AppointmentCalendarSerializer(serializers.ModelSerializer):   

    id = serializers.IntegerField(source='pk',required=False)
    Cust_phone = serializers.CharField(source='cust_noid.cust_phone2',required=False)
    job_title = serializers.CharField(source='emp_noid.EMP_TYPEid.level_desc',required=False)
    start = serializers.SerializerMethodField() 
    end = serializers.SerializerMethodField() 
    emp_img =  serializers.SerializerMethodField() 

    def get_emp_img(self, obj):
        ip = get_client_ip(self.context['request'])
        pic = None

        if obj.emp_noid.emp_pic:
            pic = str(ip)+str(obj.emp_noid.emp_pic.url)
        return pic

    def get_start(self, obj):
        if obj.appt_date and obj.appt_fr_time:
            appt_date = obj.appt_date
            appt_time = obj.appt_fr_time
            #.lstrip("0").replace(" 0", " ")
            mytime = dt.datetime.strptime(str(appt_time),'%H:%M:%S').strftime("%H:%M")
            # mydatetime = dt.datetime.combine(appt_date, fr_time)
            mydatetime = str(appt_date) +" "+ str(mytime)
            return str(mydatetime)
        else:
            return []  

    def get_end(self, obj):
        if obj.appt_date and obj.appt_fr_time:
            appt_date = obj.appt_date
            appt_time = obj.appt_to_time
            # .lstrip("0").replace(" 0", " ")
            mytime = dt.datetime.strptime(str(appt_time),'%H:%M:%S').strftime("%H:%M")
            mydatetime = str(appt_date) +" "+ str(mytime)
            return str(mydatetime)
        else:
            return []          

    class Meta:
        model = Appointment
        fields = ['id','start','end','emp_img','emp_noid','emp_name','job_title','cust_noid','cust_name',
        'cust_refer', 'Cust_phone','new_remark','appt_status','appt_date','appt_fr_time','appt_to_time']



  
class AppointmentCalSerializer(serializers.ModelSerializer):   

    id = serializers.IntegerField(source='emp_noid.pk',required=False)
    # text = serializers.CharField(source='appt_remark',required=False)
    # startDate = serializers.SerializerMethodField() 
    # endDate = serializers.SerializerMethodField() 
    # cust_name = serializers.CharField(source='cust_noid.cust_name',required=False)
    # cust_phone = serializers.CharField(source='cust_noid.cust_phone2',required=False)
    # status = serializers.CharField(source='appt_status',required=False)
    # color = serializers.SerializerMethodField() 
    # border_color = serializers.SerializerMethodField()
    # inital = serializers.SerializerMethodField()
    # req_therapist = serializers.BooleanField(source='requesttherapist',required=False)
    # balance = serializers.SerializerMethodField()
    # birthday = serializers.SerializerMethodField()
    # outstanding = serializers.SerializerMethodField()
    # remark = serializers.SerializerMethodField()
    # walkin = serializers.SerializerMethodField()
    # remark_val = serializers.SerializerMethodField()
    # appt_id = serializers.IntegerField(source='pk',required=False)
    # staff = serializers.CharField(source='emp_noid.display_name',required=False)
    # reason = serializers.CharField(source='appt_remark',required=False)
    # cust_code = serializers.CharField(source='cust_noid.cust_code',required=False)
    # gender = serializers.SerializerMethodField()
    # cust_phone1 = serializers.CharField(source='cust_noid.cust_phone1',required=False)
    # permanent_remark = serializers.CharField(source='cust_noid.cust_remark',required=False)
    # age = serializers.SerializerMethodField()
    # room = serializers.CharField(source='Room_Codeid.displayname',required=False)
    # cust_id = serializers.IntegerField(source='cust_noid.pk',required=False)
    # cust_refer = serializers.CharField(source='cust_noid.cust_refer',required=False)

    # def get_startDate(self, obj):
    #     print(obj.appt_fr_time,"print(obj.appt_fr_time)")
    #     return str(obj.appt_date)+"T"+str(obj.appt_fr_time)
    
    # def get_endDate(self, obj):
    #     return str(obj.appt_date)+"T"+str(obj.appt_to_time)

    # def get_color(self, obj):
    #     global primary_lst
    #     statusval = primary_lst[obj.appt_status]

    #     return statusval['color'] if statusval['color'] else ""

    # def get_border_color(self, obj):
    #     global primary_lst
    #     statusval = primary_lst[obj.appt_status]

    #     return statusval['border_color'] if statusval['border_color'] else "",
     
    # def get_inital(self, obj):
    #     return True

    # def get_balance(self, obj):
    #     site = self.context['site']
    #     treat_ids = Treatment.objects.filter(site_code=site.itemsite_code,
    #     status="Open",cust_code=obj.cust_no).order_by('pk')[:2]
        
    #     return True if treat_ids else False  

    # def get_birthday(self, obj):
    #     birthday = False
    #     if obj.cust_noid and obj.cust_noid.cust_dob:
    #         custdob = datetime.datetime.strptime(str(obj.cust_noid.cust_dob), "%Y-%m-%d")
    #         if custdob.month == date.month:
    #             birthday = True

    #     return birthday 
       
    # def get_outstanding(self, obj):
    #     outstanding = False
    #     tre_accids = TreatmentAccount.objects.filter(cust_code=obj.cust_no, 
    #     outstanding__gt = 0).order_by('pk')[:2]
    #     if tre_accids:
    #         outstanding = True

    #     deposit_accids = DepositAccount.objects.filter(cust_code=obj.cust_no, 
    #     outstanding__gt=0).order_by('pk')[:2]
    #     if deposit_accids:
    #         outstanding = True

    #     pre_acc_ids = PrepaidAccount.objects.filter(cust_code=obj.cust_no,
    #     outstanding__gt=0).order_by('pk')[:2]
    #     if pre_acc_ids:
    #         outstanding = True

    #     return outstanding    
    
    # def get_remark(self, obj):
    #     return True if obj.new_remark else False
    
    # def get_walkin(self, obj):
    #     return True if obj.walkin == True else False

    # def get_remark_val(self, obj):
    #     remark_val = ""
    #     if obj.new_remark:
    #         apptdate = datetime.datetime.strptime(str(obj.appt_date), "%Y-%m-%d").strftime("%d/%m/%Y")
    #         remark_val = "["+str(obj.new_remark)+" - "+"Remark By: "+str(obj.appt_created_by)+" - "+str(apptdate)+"]"
             
    #     return remark_val

    # def get_gender(self, obj):
    #     gender = ""
    #     if obj.cust_noid and obj.cust_noid.cust_sexes:
    #         gendr = Gender.objects.filter(itm_code=obj.cust_noid.cust_sexes).first()
    #         if gendr.itm_code == "1":
    #             gender = "M"
    #         elif gendr.itm_code == "2":
    #             gender = "F"     
        
    #     return gender

    # def get_age(self, obj):
    #     age = ""
    #     if obj.cust_noid and obj.cust_noid.cust_dob:
    #         custdob = datetime.datetime.strptime(str(obj.cust_noid.cust_dob), "%Y-%m-%d")
    #         age = calculate(custdob)

    #     return age      


    # class Meta:
    #     model = Appointment
    #     fields = ['id','text','startDate','endDate','cust_name','cust_phone','status','color',
    #     'border_color','inital','req_therapist','balance','birthday','outstanding',
    #     'remark','walkin','remark_val','appt_id','staff','appt_remark','reason',
    #     'linkcode','cust_code','gender','cust_phone1','permanent_remark','age','room',
    #     'link_flag','cust_id','cust_refer','sec_status']

  
    # def to_representation(self, obj):
    #     site = self.context['site']
    #     date = self.context['date']

    #     primary_lst = {
    #     "Booking": {"color":"#f0b5ec","border_color":"#ec40e1"},
    #     "Waiting": {"color":"#c928f3","border_color":"#49035a"},
    #     "Confirmed": {"color":"#ebef8b","border_color":"#9ba006"},
    #     "Cancelled": {"color":"#ff531a","border_color":"#7a2306"},
    #     "Arrived": {"color":"#42e2c7","border_color":"#076858"},
    #     "Done": {"color":"#80c4f8","border_color":"#05508a"},
    #     "LastMinCancel": {"color":"#e1920b","border_color":"#724903"},
    #     "Late": {"color":"#66d9ff","border_color":"#097396"},
    #     "No Show": {"color":"#c56903","border_color":"#6e3e06"},
    #     "Block": {"color":"#b2b2b2","border_color":"#000000"}
    #     }
    #     statusval = primary_lst[obj.appt_status]

    #     startdate =  str(obj.appt_date)+"T"+str(obj.appt_fr_time)
    #     enddate =  str(obj.appt_date)+"T"+str(obj.appt_to_time)
    #     apptdate = datetime.datetime.strptime(str(obj.appt_date), "%Y-%m-%d").strftime("%d/%m/%Y")
        
        
    #     cust_name = ""; custphone2 = ""; custrefer = ""; balance = False;birthday = False
    #     outstanding = False;remark_val = ""; custcode = ""; gender = ""
    #     custphone1 = ""; custremark = "";age = "";custobjpk = ""
    #     # remark=False

    #     custobj = Customer.objects.filter(cust_code=obj.cust_no,cust_isactive=True).order_by('-pk').first() 
    #     if custobj:
    #         # cust_name = custobj.cust_name
    #         # custphone2 = custobj.cust_phone2
    #         # custphone1 = custobj.cust_phone1
    #         # custcode = custobj.cust_code
    #         # custobjpk = custobj.pk
    #         # custremark = custobj.cust_remark
    #         # custrefer = custobj.cust_refer


    #         if custobj.cust_dob:
    #             custdob = datetime.datetime.strptime(str(custobj.cust_dob), "%Y-%m-%d")
    #             if custdob.month == date.month:
    #                 birthday = True

    #             age = calculate(custdob)    

    #         if custobj.cust_sexes:
    #             gendr = Gender.objects.filter(itm_code=custobj.cust_sexes).first()
    #             if gendr.itm_code == "1":
    #                 gender = "M"
    #             elif gendr.itm_code == "2":
    #                 gender = "F"         


    #         treat_ids = Treatment.objects.filter(site_code=site.itemsite_code,
    #         status="Open",cust_code=obj.cust_no).order_by('pk')[:2]
        
    #         if treat_ids:
    #             balance = True    

    #         tre_accids = TreatmentAccount.objects.filter(cust_code=custobj.cust_code, 
    #         outstanding__gt = 0).order_by('pk')[:2]
    #         if tre_accids:
    #             outstanding = True

    #         deposit_accids = DepositAccount.objects.filter(cust_code=custobj.cust_code, 
    #         outstanding__gt=0).order_by('pk')[:2]
    #         if deposit_accids:
    #             outstanding = True

    #         pre_acc_ids = PrepaidAccount.objects.filter(cust_code=custobj.cust_code,
    #         outstanding__gt=0).order_by('pk')[:2]
    #         if pre_acc_ids:
    #             outstanding = True

    #     if obj.new_remark:
    #         # remark = True
    #         remark_val = "["+str(obj.new_remark)+" - "+"Remark By: "+str(obj.appt_created_by)+" - "+str(apptdate)+"]"
                                        


    #     mapped_object = {'id': obj.emp_noid.pk,'text':obj.appt_remark,'startDate':startdate,
    #     'endDate': enddate,'cust_name': obj.cust_noid.cust_name if obj.cust_noid and obj.cust_noid.cust_name else "",
    #     'cust_phone': obj.cust_noid.cust_phone2 if obj.cust_noid and obj.cust_noid.cust_phone2 else "",
    #     'status': obj.appt_status,'color': statusval['color'] if statusval['color'] else "",
    #     'border_color': statusval['border_color'] if statusval['border_color'] else "",
    #     'inital':True, 'req_therapist' : True if obj.requesttherapist == True else False,
    #     'balance' : balance,'birthday':birthday,'outstanding':outstanding,'remark': True if obj.new_remark else False,
    #     'walkin': True if obj.walkin == True else False, 'remark_val':remark_val,
    #     'appt_id':obj.pk,'staff': obj.emp_noid.display_name if obj.emp_noid and obj.emp_noid.display_name else "",
    #     'appt_remark':obj.appt_remark if obj.appt_remark else "",
    #     'reason':obj.appt_remark if obj.appt_remark else "",
    #     'linkcode': obj.linkcode if obj.linkcode else "",
    #     'cust_code' : obj.cust_noid.cust_code if obj.cust_noid and obj.cust_noid.cust_code else "",
    #     'gender' : gender,'cust_phone1' :obj.cust_noid.cust_phone1 if obj.cust_noid and obj.cust_noid.cust_phone1 else "",
    #     'permanent_remark' : obj.cust_noid.cust_remark if obj.cust_noid and obj.cust_noid.cust_remark else "",
    #     'age' : age,
    #     'room':obj.Room_Codeid.displayname if obj.Room_Codeid and obj.Room_Codeid.displayname else "",
    #     'link_flag': obj.link_flag,'cust_id' : obj.cust_noid.pk if obj.cust_noid else "",
    #     'cust_refer': obj.cust_noid.cust_refer if obj.cust_noid and obj.cust_noid.cust_refer else "",
    #     'sec_status': obj.sec_status if obj.sec_status else ""
    #     }
    #     return mapped_object

    #     # mapped_object = {'id': obj.emp_noid.pk,'text':obj.appt_remark,'startDate':startdate,
    #     # 'endDate': enddate,
    #     # 'status': obj.appt_status,'color': statusval['color'] if statusval['color'] else "",
    #     # 'border_color': statusval['border_color'] if statusval['border_color'] else "",
    #     # 'appt_id':obj.pk,'linkcode': obj.linkcode if obj.linkcode else "",
    #     # 'link_flag': obj.link_flag,'cust_id' : obj.cust_noid.pk if obj.cust_noid else ""
    #     # }
    #     # return mapped_object


class Item_DeptSerializer(serializers.ModelSerializer):  
    id = serializers.IntegerField(source='pk',required=False)
  
    class Meta:
        model = ItemDept
        fields = ['id','itm_desc','deptpic']

class StockListSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
    Item_Class = serializers.CharField(source='Item_Classid.itm_desc',required=False)
  
    class Meta:
        model = Stock
        fields = ['id','item_desc','item_name','item_price','Stock_PIC','Item_Classid','Item_Class','srv_duration']
        read_only_fields = ('item_code',)


class TreatmentMasterSerializer(serializers.ModelSerializer): 
    item_class = serializers.CharField(source='Item_Class.itm_desc',required=False)
    emp_name = serializers.SerializerMethodField() 
    room_name = serializers.CharField(source='Trmt_Room_Codeid.displayname',required=False)
    room_img = serializers.CharField(source='Trmt_Room_Codeid.Room_PIC.url',required=False)
    emp_img =  serializers.SerializerMethodField() 
    stock_name = serializers.CharField(source='Item_Codeid.item_desc',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)
    recur_days = serializers.SerializerMethodField() 
    recur_qty = serializers.SerializerMethodField() 
    item_text = serializers.SerializerMethodField() 


    def get_recur_days(self, obj):
        return None

    def get_recur_qty(self, obj):
        return None    
    
    def get_item_text(self, obj):
        return None 

    def get_emp_img(self, obj):
        ip = get_client_ip(self.context['request'])
        pic_lst = []
        if obj.emp_no:
            for e in obj.emp_no.all():
                if e.emp_pic:
                    pic = str(ip)+str(e.emp_pic.url)
                    pic_lst.append(pic)
        return pic_lst
    
    def get_emp_name(self, obj):
        if obj.emp_no:
            string = ""
            for i in obj.emp_no.all():
                if string == "":
                    string = string + i.display_name
                elif not string == "":
                    string = string +","+ i.display_name
            return string
        else:
            return None 

    class Meta:
        model = Treatment_Master
        fields = ['id','PIC','course','item_class','Item_Class','Item_Codeid','stock_name','treatment_date',
        'start_time','end_time','add_duration','duration','site_name','Site_Codeid','site_code','price','treatment_no','times','status',
        'emp_no','emp_name','Trmt_Room_Codeid','room_name','cus_requests','treatment_details','requesttherapist',
        'procedure','products_used','recurring_appointment','room_img','emp_img','sa_transacno','appt_time',
        'recur_days','recur_qty','item_text','checktype','treat_parentcode']

   
    def validate(self, data):
        if 'treatment_no' in data:
            if data['treatment_no'] is None:
                raise serializers.ValidationError("treatment_no Field is required.")
        if 'emp_no' in data:
            if data['emp_no'] is None:
                raise serializers.ValidationError("emp_no Field is required.")

        if 'Trmt_Room_Codeid' in data:
            if data['Trmt_Room_Codeid'] is None:
                raise serializers.ValidationError("Trmt_Room_Code Field is required.")  

        if 'cus_requests' in data:
            if data['cus_requests'] is None:
                raise serializers.ValidationError("cus_requests Field is required.") 

        if 'products_used' in data:
            if data['products_used'] is None:
                raise serializers.ValidationError("products_used Field is required.")

        if 'recurring_appointment' in data:
            if data['recurring_appointment'] is None:
                raise serializers.ValidationError("recurring_appointment Field is required.")
            
        return data

    # def update(self, instance, validated_data):
    #     instance.save()    
    #     return instance      


class StaffsAvailableSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    job_title = serializers.CharField(source='EMP_TYPEid.level_desc',required=False)
    emp_img =  serializers.SerializerMethodField() 
    services =  serializers.SerializerMethodField()
    emp_name =  serializers.SerializerMethodField() 

    def get_emp_name(self, obj):
        return obj.display_name

    def get_emp_img(self, obj):
        ip = get_client_ip(self.context['request'])
        if obj.emp_pic:
            pic = str(ip)+str(obj.emp_pic.url)
        else:
            pic = None    
        return pic

    def get_services(self, obj):
        if obj.skills.all():
            string = ""
            for i in obj.skills.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None        

    class Meta:
        model = Employee
        fields = ['id','emp_name','display_name','emp_img','job_title','services']

  

class StaffsAppointmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    def to_representation(self, obj):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True).order_by('-pk')
        site = fmspw[0].loginsite

        ip = get_client_ip(self.context['request'])
        pic = ""
        if obj.emp_pic:
            pic = str(ip)+str(obj.emp_pic.url)
        
        emp_siteids = EmpSitelist.objects.filter(Site_Codeid__pk=site.pk,isactive=True,
        Emp_Codeid__pk=obj.pk).first() 
        emp_order = emp_siteids.emp_seq_webappt if emp_siteids and emp_siteids.emp_seq_webappt else ""    
          
        mapped_object = {'emp_pic':pic,'staff_name':obj.display_name,
        'id': obj.pk,'clock_in' : False,'emp_order':emp_order}
        return mapped_object
    

class PayGroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PayGroup
        fields = ['id','pay_group_code','picturelocation']        

class PaytableSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    pay_group_name = serializers.CharField(source='pay_groupid.pay_group_code',required=False)

    class Meta:
        model = Paytable
        fields = ['id','pay_code','pay_description','pay_groupid','pay_group_name','gt_group','qr_code']

class PostaudSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    billed_by_name = serializers.CharField(source='billed_by.pw_userlogin',required=False)
    pay_type_name = serializers.CharField(source='pay_typeid.pay_description',required=False)
    pay_group_name = serializers.CharField(source='pay_groupid.pay_group_code',required=False)

    class Meta:
        model = PosTaud
        fields = ['id','sa_date','sa_time','billed_by','billed_by_name','sa_transacno','pay_groupid','pay_group_name',
        'pay_typeid','pay_type_name','pay_desc','pay_tendamt','pay_amt','pay_actamt','ItemSIte_Codeid','itemsite_code','subtotal','tax','discount_amt',
        'sa_transacno','billable_amount','pay_premise','credit_debit','points','prepaid','is_voucher','pay_rem1',
        'pay_rem2','pay_rem3','pay_rem4']

class PoshaudSerializer(serializers.ModelSerializer):
    # billed_by_name = serializers.CharField(source='trans_user_loginid.pw_userlogin',required=False)

    class Meta:
        model = PosHaud
        fields = ['id','sa_custno','sa_custname','sa_date','sa_time']

class PosdaudSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = PosDaud
        fields = ['id','dt_itemdesc','dt_qty','dt_deposit','record_detail_type','dt_price',
        'dt_status','itemcart','staffs','isfoc','holditemqty','trmt_done_staff_name','dt_combocode',]

class PostaudprintSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    pay_type_name = serializers.CharField(source='pay_typeid.pay_description',required=False)

    class Meta:
        model = PosTaud
        fields = ['id','pay_rem1','pay_type_name','pay_amt','pay_gst']

class ItemStatusSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    class Meta:
        model = ItemStatus
        fields = ['id','status_code','status_desc','status_short_desc'] 

class SourceSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Source
        fields = ['id','source_code','source_desc']

class AppointmentPopupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    contact_no = serializers.CharField(source='cust_noid.cust_phone2',required=False)
    cust_dob = serializers.CharField(source='cust_noid.cust_dob',required=False)
   

    class Meta:
        model = Appointment
        fields = ['id','appt_fr_time','appt_to_time','cust_name','cust_refer','cust_noid',
        'contact_no','cust_dob','appt_remark','appt_status',]

class AppointmentResourcesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    room_name = serializers.CharField(source='Room_Codeid.displayname',required=False)
    edit_remark = serializers.SerializerMethodField()
    emp_id = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    add_duration = serializers.SerializerMethodField()
    item_id = serializers.SerializerMethodField()
    recur_days = serializers.SerializerMethodField() 
    recur_qty = serializers.SerializerMethodField() 
    item_text = serializers.SerializerMethodField() 
    recur_ids = serializers.SerializerMethodField()


    def get_recur_days(self, obj):
        return None

    def get_recur_qty(self, obj):
        return None    

    def get_edit_remark(self, obj):
        return None 

    def get_emp_id(self, obj):
        return None

    def get_start_time(self, obj):
        return None  

    def get_end_time(self, obj):
        return None 

    def get_add_duration(self, obj):
        return None   

    def get_item_id(self, obj):
        return None 

    def get_item_text(self, obj):
        return None 

    def get_recur_ids(self, obj):
        return None                     


    class Meta:
        model = Appointment
        fields = ['id','appt_date','cust_name','cust_noid','appt_status','new_remark',
        'sec_status','Room_Codeid','room_name','requesttherapist','edit_remark','emp_id',
        'start_time','end_time','add_duration','item_id','recur_days','recur_qty','item_text',
        'recur_ids',]
        extra_kwargs = {'edit_remark': {'required': True},'emp_id': {'required': True}}

    # def validate(self, data):
    #     request = self.context['request']
    #     if not 'edit_remark' in request.data:
    #         raise serializers.ValidationError("edit_remark Field is required.")
    #     else:
    #         if request.data['edit_remark'] is None: 
    #             raise serializers.ValidationError("edit_remark Field is required!!")
        
    #     return data 

class AppointmentEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False) 

    class Meta:
        model = Appointment
        fields = ['id']
 


class AppointmentRecurrSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    emp_id = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    add_duration = serializers.SerializerMethodField()
    item_id = serializers.SerializerMethodField()
    item_text = serializers.SerializerMethodField() 
    recur_ids = serializers.SerializerMethodField()


    def get_emp_id(self, obj):
        return None

    def get_start_time(self, obj):
        return None  

    def get_end_time(self, obj):
        return None 

    def get_add_duration(self, obj):
        return None   

    def get_item_id(self, obj):
        return None 

    def get_item_text(self, obj):
        return None 

    def get_recur_ids(self, obj):
        return None                     


    class Meta:
        model = Appointment
        fields = ['id','appt_status','sec_status','Room_Codeid','requesttherapist',
        'emp_id','start_time','end_time','add_duration','item_id''item_text',
        'recur_ids']
        extra_kwargs = {'edit_remark': {'required': True},'emp_id': {'required': True}}

  
class SecuritiesSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    class Meta:
        model = Securities
        fields = ['id', 'level_name', 'level_description', 'level_code']
    
class CustTransferSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    site_id = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'Site_Codeid', 'site_id']
        extra_kwargs = {'site_id': {'required': True}}

    def validate(self, data):
        request = self.context['request']
        if not 'site_id' in request.data:
            raise serializers.ValidationError("site_id Field is required.")
        else:
            if request.data['site_id'] is None: 
                raise serializers.ValidationError("site_id Field is required!!")
        
        return data     

    
class EmpTransferPerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    site_id = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'emp_code', 'emp_name','site_id'] 
        extra_kwargs = {'site_id': {'required': True}}

    def validate(self, data):
        request = self.context['request']
        if not 'site_id' in request.data:
            raise serializers.ValidationError("site_id Field is required.")
        else:
            if request.data['site_id'] is None: 
                raise serializers.ValidationError("site_id Field is required!!")
        
        return data    

class EmpTransferTempSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    site_id = serializers.SerializerMethodField()
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    hour_id = serializers.SerializerMethodField()


    class Meta:
        model = Employee
        fields = ['id', 'emp_code', 'emp_name','site_id','start_date','end_date','hour_id'] 
        extra_kwargs = {'site_id': {'required': True},'hour_id': {'required': True}}

    def validate(self, data):
        request = self.context['request']
        if not 'site_id' in request.data:
            raise serializers.ValidationError("site_id Field is required.")
        else:
            if request.data['site_id'] is None: 
                raise serializers.ValidationError("site_id Field is required!!")
        
        if not 'hour_id' in request.data:
            raise serializers.ValidationError("hour_id Field is required.")
        else:
            if request.data['hour_id'] is not None:
                if ScheduleHour.objects.filter(id=request.data['hour_id'],itm_isactive=False):
                    raise serializers.ValidationError("ScheduleHour ID Does not exist!!")
                if not ScheduleHour.objects.filter(id=request.data['hour_id'],itm_isactive=True):
                    raise serializers.ValidationError("ScheduleHour ID Does not exist!!")
        
        return data        
        
        
class EmpSitelistSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmpSitelist
        fields = ['id','site_code']

class ScheduleHourSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ScheduleHour
        fields = ['id','itm_code','itm_desc','offday']


class CustApptSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_name','cust_email','cust_code','cust_nric','cust_remark','site_code']


    def to_representation(self, instance):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True).order_by('-pk')
        site = fmspw[0].loginsite

        iscurrent = ""
        if instance.site_code == site.itemsite_code:
            iscurrent = True
        elif instance.site_code != site.itemsite_code:
            iscurrent = False
        contactperson = []

        if instance.cust_corporate == True:
            contactperson = list(ContactPerson.objects.filter(isactive=True,customer_id=instance
            ).values('name','mobile_phone')) 
            # print(contactperson,"contactperson")    
       
        mapped_object = {'id':instance.pk,'cust_name':instance.cust_name if instance.cust_name else "",
        'cust_phone1': instance.cust_phone2 if instance.cust_phone2 else "",
        'cust_email': instance.cust_email if instance.cust_email else "",
        'cust_code': instance.cust_code if instance.cust_code else "",
        'cust_nric': instance.cust_nric if instance.cust_nric else "",
        'custphone2': instance.cust_phone1 if instance.cust_phone1 else "",
        'site_code': instance.site_code,
        'cust_remark': instance.cust_remark if instance.cust_remark else "",
        'cust_refer': instance.cust_refer if instance.cust_refer else "",'iscurrent':iscurrent,
        'cust_corporate': instance.cust_corporate,
        'contactperson': contactperson}
        return mapped_object    

   
           
class ApptTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ApptType
        fields = ['id','appt_type_desc','appt_type_code']

# class ApptChannelSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source='pk',required=False)

#     class Meta:
#         model = ApptChannel
#         fields = ['id','channel_code','channel_desc']

class TmpItemHelperSerializer(serializers.ModelSerializer):

    class Meta:
        model = TmpItemHelper
        fields = ['id','helper_id','helper_name','wp1','appt_fr_time','appt_to_time','add_duration','session']

class FocReasonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FocReason
        fields = ['id','foc_reason_ldesc']

class LanguageSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Language
        fields = ['itm_id','itm_desc','itm_code']

class CountrySerializer(serializers.ModelSerializer):    
    class Meta:
        model = Country
        fields = ['itm_id','itm_desc','itm_code']

class StateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = State
        fields = ['itm_id','itm_desc','itm_code']

class TreatmentApptSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id']

class AppointmentSortSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    emp_ids = serializers.SerializerMethodField()

    def get_emp_ids(self, obj):
        return None 

    class Meta:
        model = Employee
        fields = ['id', 'display_name','emp_code','emp_ids'] 
        extra_kwargs = {'emp_ids': {'required': True}}

class ApptTreatmentDoneHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Appointment
        fields = ['id']

class UpcomingAppointmentSerializer(serializers.ModelSerializer):   

    id = serializers.IntegerField(source='pk',required=False)
  

    class Meta:
        model = Appointment
        fields = ['id','appt_date','appt_fr_time','appt_remark','emp_name','appt_status','sec_status','itemsite_code']


class AppointmentBlockSerializer(serializers.ModelSerializer):   

    id = serializers.IntegerField(source='pk',required=False)
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    reason_id = serializers.SerializerMethodField()
    emp_ids = serializers.SerializerMethodField()
    emp_name = serializers.SerializerMethodField() 

    def get_emp_name(self, obj):
        return obj.emp_noid.display_name

    def get_start_date(self, obj):
        return None 

    def get_end_date(self, obj):
        return None 

    def get_reason_id(self, obj):
        return None      

    def get_emp_ids(self, obj):
        return None 

      
    class Meta:
        model = Appointment
        fields = ['id','appt_date','start_date','end_date','appt_fr_time','appt_to_time','reason',
        'reason_id','duration','appt_remark','emp_noid','emp_no','emp_name','emp_ids','appt_isactive']

    def validate(self, data):
        request = self.context['request']
        if request.method == "POST":
            if not 'start_date' in request.data:
                raise serializers.ValidationError("start date Field is required.")
            else:
                if request.data['start_date'] is None: 
                    raise serializers.ValidationError("start date Field is required!!")
            
            if not 'end_date' in request.data:
                raise serializers.ValidationError("end date Field is required.")
            else:
                if request.data['end_date'] is None:
                    raise serializers.ValidationError("end date Field is required.")
                if not request.data['end_date']: 
                    raise serializers.ValidationError("end date Field is required.")

            if not 'reason_id' in request.data:
                raise serializers.ValidationError("Block Reason Field is required.")
            else:
                if request.data['reason_id'] is None: 
                    raise serializers.ValidationError("Block Reason Field is required!!")
                if not request.data['reason_id']: 
                    raise serializers.ValidationError("Reason id Field is required.")

            if not 'emp_ids' in request.data:
                raise serializers.ValidationError("emp ids Field is required.")
            else:
                if request.data['emp_ids'] is not None:
                    if Employee.objects.filter(pk__in=request.data['emp_ids'],emp_isactive=False):
                        raise serializers.ValidationError("Employee ID Does not exist!!")
                    if not Employee.objects.filter(pk__in=request.data['emp_ids'],emp_isactive=True):
                        raise serializers.ValidationError("Employee ID Does not exist!!")
                elif request.data['emp_ids'] is None or request.data['emp_ids'] == []: 
                    raise serializers.ValidationError("Employee ID Should not be empty/null!!")
        
        return data       

class BlockReasonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BlockReason
        fields = ['id','b_reason']

class EmployeeBranchSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Employee
        fields = ['id', 'display_name','emp_code'] 


class AppointmentLogSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AppointmentLog
        fields = ['id','appt_id','username','appt_date','appt_fr_time','appt_to_time',
        'add_duration','emp_code','appt_status','sec_status','appt_remark','requesttherapist',
        'created_at']


class RoomAppointmentSerializer(serializers.ModelSerializer):
    
    room_img = serializers.SerializerMethodField() 
    
    def get_room_img(self, obj):
        ip = get_client_ip(self.context['request'])
        if obj.Room_PIC:
            pic = ip+str(obj.Room_PIC.url)
        else:
            pic = None    
        return pic

    class Meta:
        model = Room
        fields = ['id','displayname','room_img']

class DeptAppointmentSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(source='pk',required=False)
    dept_img = serializers.SerializerMethodField() 
    
    def get_dept_img(self, obj):
        ip = get_client_ip(self.context['request'])
        if obj.deptpic:
            pic = ip+str(obj.deptpic.url)
        else:
            pic = None    
        return pic

    class Meta:
        model = ItemDept
        fields = ['id','itm_desc','dept_img']


class TitleSerializer(serializers.ModelSerializer):

    site_id = serializers.SerializerMethodField() 
    
    def get_site_id(self, obj):
        if obj.product_license:
            siteobj = ItemSitelist.objects.filter(itemsite_code=obj.product_license,itemsite_isactive=True).first() 
            return siteobj.pk if siteobj.pk else None
        else:
            return None    
    
    class Meta:
        model = Title
        fields = ['id','title','trans_h1','trans_h2','trans_footer1','trans_footer2',
        'trans_footer3','trans_footer4','logo_pic','site_id','gst_reg_no','product_license']

def get_in_val(self, time):
    if time:
        value = str(time).split(':')
        hr = value[0]
        mins = value[1]
        in_time = str(hr)+":"+str(mins)
        return str(in_time)
    else:
        return None 

class CustApptUpcomingSerializer(serializers.ModelSerializer):   
    id = serializers.IntegerField(source='pk',required=False)
   


    class Meta:
        model = Appointment
        fields = ['id','appt_date','appt_fr_time','appt_to_time','appt_remark','itemsite_code','emp_name',
        'appt_status','sec_status']


    def to_representation(self, instance):
        if instance.appt_date:
            splt = str(instance.appt_date).split(" ")
            appt_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

        mapped_object = {'id': instance.pk,'appt_date': appt_date,'appt_fr_time': get_in_val(self, instance.appt_fr_time), 
        'appt_to_time': get_in_val(self, instance.appt_to_time),
        'appt_remark': instance.appt_remark,'itemsite_code' : instance.itemsite_code,'emp_name':instance.emp_name,
        'appt_status': instance.appt_status,'sec_status': instance.sec_status if instance.sec_status else ""}
      
        return mapped_object    
        

class AttendanceStaffsSerializer(serializers.ModelSerializer):   
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Attendance2
        fields = ['id','attn_date','attn_emp_code','attn_site_code','attn_type']


    def to_representation(self, instance):
        enable = False
        emp_obj = Employee.objects.filter(emp_code=instance.attn_emp_code,emp_isactive=True).first()
        # print(emp_obj.pk,"emp_obj")
        mapped_object = {'id': instance.pk,'emp_img': "",
        'emp_name': "", 'attn_type': instance.attn_type, 'enable': enable} 
        
        if emp_obj:
            ip = get_client_ip(self.context['request'])
            pic = ""
            if emp_obj.emp_pic:
                pic = str(ip)+str(emp_obj.emp_pic.url) 

            if instance.attn_type == '00':
                enable = True

            mapped_object = {'id': instance.pk,'emp_img': pic,
            'emp_name': emp_obj.display_name, 'attn_type': instance.attn_type, 'enable': enable} 
        
        return mapped_object


class EmpWorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workschedule
        fields = ['id','monday','tuesday','wednesday','thursday','friday','saturday','sunday','emp_code']
        read_only_fields = ('updated_at', 'created_at', 'emp_code')

    def validate(self, data):
        request = self.context['request']
        # print("req",data)
        return data


    # def update(self, validated_data):

        # work_schedule = Workschedule.objects.create(emp_code=self.emp.emp_code,
        #                                             monday=validated_data.get('monday'),
        #                                             tuesday=validated_data.get('tuesday'),
        #                                             wednesday=validated_data.get('wednesday'),
        #                                             thursday=validated_data.get('thursday'),
        #                                             friday=validated_data.get('friday'),
        #                                             saturday=validated_data.get('saturday'),
        #                                             sunday=validated_data.get('sunday'),
        #                                             name=self.emp.emp_name,
        #                                             )
    def update(self, instance, validated_data):
        # print(validated_data)
        instance.monday = validated_data.get('monday',instance.monday)
        instance.tuesday = validated_data.get('tuesday',instance.tuesday)
        instance.wednesday = validated_data.get('wednesday',instance.tuesday)
        instance.thursday = validated_data.get('thursday',instance.tuesday)
        instance.friday = validated_data.get('friday',instance.tuesday)
        instance.saturday = validated_data.get('saturday',instance.tuesday)
        instance.sunday = validated_data.get('sunday',instance.tuesday)

        instance.save()
        return instance

class CustomerFormControlSerializer(serializers.ModelSerializer):

    # def to_representation(self, instance):
    #     data = super(CustomerFormControlSerializer, self).to_representation(instance)
    #     layout = json.loads(data.get('layout'))
    #     print(layout,type(layout),data.get('layout'))
    #     data['layout'] = data.get('layout')
    #     data["x"] = {'c':2 }
    #     return data
    #
    # def get_layout_json(self):
    #     pass

    class Meta:
        model = CustomerFormControl
        fields = ['id','field_name','display_field_name','visible_in_registration', 'visible_in_listing','visible_in_profile','mandatory','order','col_width','layout','showLabel']
        read_only_fields = ('field_name','display_field_name')

class MGMSerializer(serializers.ModelSerializer):
    reference = serializers.SerializerMethodField()

    def get_reference(self,obj):
        ref_list = Customer.objects.filter(cust_referby_code=obj.cust_code)
        # print(obj.cust_code,ref_list)
        if ref_list.exists():
            mgm_serializer = MGMSerializer(ref_list,many=True)
            return mgm_serializer.data
        else:
            return []

    class Meta:
        model = Customer
        fields = ['cust_no','cust_code','cust_name','reference']


class RewardPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardPolicy
        fields = '__all__'
        read_only_fields = ('reward_code',)

    def to_representation(self, instance):
        data = super(RewardPolicySerializer, self).to_representation(instance)
        try:
            cust_type = CustomerClass.objects.get(class_code=data['cust_type'])
            data['cust_type_desc'] = cust_type.class_desc
        except Exception as e:
            data['cust_type_desc'] = ""
            # print(e)
        try:
            itm_type = MrRewardItemType.objects.get(itemtype_code=data['reward_item_type'])
            data['reward_item_type_desc'] = itm_type.itemtype_desc
        except Exception as e:
            data['reward_item_type_desc'] = ""
            # print(e)
        
        #item_divids = instance.item_divids.all()
        item_divids = instance.item_divids.filter(issellable=True)
        data['item_div_desc'] = ""  
        data['Item_Divid'] = ""
        if item_divids.exists():
            data['Item_Divid'] =  [{'label': i.itm_desc ,'value': i.pk} for i in item_divids if i.itm_desc]
            data['item_div_desc'] = ','.join([v.itm_desc for v in item_divids if v.itm_desc])

        data['dept_ids_desc'] = "";data['dept_id'] = ''
        if instance.dept_ids.all().exists():
            data['dept_ids_desc'] = ','.join([i.itm_desc for i in instance.dept_ids.all() if i.itm_desc])
            data['dept_id'] = [{'label': i.itm_desc ,'value': i.pk} for i in instance.dept_ids.all() if i.itm_desc]
        
        data['brand_ids_desc'] = "";data['brand_id'] = ''
        if instance.brand_ids.all().exists():
            data['brand_ids_desc'] = ','.join([i.itm_desc for i in instance.brand_ids.all() if i.itm_desc]) 
            data['brand_id'] = [{'label': i.itm_desc ,'value': i.pk} for i in instance.brand_ids.all() if i.itm_desc]

        return data

    def create(self, validated_data):
        reward = RewardPolicy(**validated_data)
        reward.reward_code = code_generator(size=6)
        reward.save()

        return reward




class RedeemPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RedeemPolicy
        fields = '__all__'
        read_only_fields = ('redeem_code',)

    def to_representation(self, instance):
        data = super(RedeemPolicySerializer, self).to_representation(instance)
        try:
            cust_type = CustomerClass.objects.get(class_code=data['cust_type'])
            data['cust_type_desc'] = cust_type.class_desc
        except Exception as e:
            data['cust_type_desc'] = "" 

        item_divids = instance.item_divids.filter(issellable=True)
        data['item_div_desc'] = ""  
        data['Item_Divid'] = ""
        if item_divids.exists():
            data['Item_Divid'] =  [{'label': i.itm_desc ,'value': i.pk} for i in item_divids if i.itm_desc]
            data['item_div_desc'] = ','.join([v.itm_desc for v in item_divids if v.itm_desc])

        data['dept_ids_desc'] = "";data['dept_id'] = ''
        if instance.dept_ids.all().exists():
            data['dept_ids_desc'] = ','.join([i.itm_desc for i in instance.dept_ids.all() if i.itm_desc])
            data['dept_id'] =  [{'label': i.itm_desc ,'value': i.pk} for i in instance.dept_ids.all() if i.itm_desc]
        
        data['brand_ids_desc'] = "";data['brand_id'] = ""
        if instance.brand_ids.all().exists():
            data['brand_ids_desc'] = ','.join([i.itm_desc for i in instance.brand_ids.all() if i.itm_desc]) 
            data['brand_id'] = [{'label': i.itm_desc ,'value': i.pk} for i in instance.brand_ids.all() if i.itm_desc]  

        return data

    def create(self, validated_data):
        redeem = RedeemPolicy(**validated_data)
        redeem.redeem_code = code_generator(size=6)
        redeem.save()
        return redeem


class DiagnosisSerializer(serializers.ModelSerializer):
    # pic_abs_path = serializers.SerializerMethodField()

    # def get_pic_abs_path(self, obj):
    #     request = self.context.get('request')
    #     print(obj.sys_code,print(obj.pic_path))
    #     try:
    #         photo_url = obj.pic_path.url
    #         return request.build_absolute_uri(photo_url)
    #     except:
    #         return None

    def to_representation(self, data):
        data = super(DiagnosisSerializer,self).to_representation(data)
        # data['cust_nric'] = data.get("masked_nric")
        request = self.context.get('request')
        try:
            photo_url = data.get('pic_path')
            data['pic_path'] = request.build_absolute_uri(photo_url)
        except Exception as e:
            print("url ",e)

        try:
            pic_data = data.get('pic_data1')
            data['pic_data1'] = json.loads(pic_data)
        except Exception as e:
            print("json err: ",e)

        return data

    class Meta:
        model = Diagnosis
        fields = ['sys_code','diagnosis_date','remarks','date_pic_take','cust_name','cust_code','diagnosis_code','pic_path','cust_no','pic_data','pic_data1']
        read_only_fields = ("diagnosis_code","cust_code",)
        extra_kwargs = {'diagnosis_code': {'required': False},
                        'cust_code': {'required': False},
                        'pic_path': {'required': True},
                        'pic_data': {'required': False},
                        'remark1': {'required': True},
                        }

    # def validate(self, attrs):
    #     return attrs

class DiagnosisCompareSerializer(serializers.ModelSerializer):
    # diagnosis1 = DiagnosisSerializer(source='diagnosis1_id')
    # diagnosis2 = DiagnosisSerializer(source='diagnosis2_id')
    diagnosis_list = DiagnosisSerializer(source='diagnosis',many=True,read_only=True)

    # def get_diagnosis_list(self,obj):
    #     print(self.context)
    #     diag_serializer = DiagnosisSerializer(obj.diagnosis.all(),many=True,read_only=True,context=self.context)
    #     return diag_serializer.data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['diagnosis_list'].context.update(self.context)

    class Meta:
        model = DiagnosisCompare
        # fields = '__all__'
        fields = ['id','compare_code','compare_remark','compare_datetime','compare_user',
                  'cust_code','diagnosis','diagnosis_list']
        extra_kwargs = {'compare_isactive': {'required': False}
                        }

    # def validate(self, attrs):
    #     if attrs['diagnosis1_id'].cust_no != attrs['diagnosis2_id'].cust_no or attrs['diagnosis1_id'].site_code != attrs['diagnosis2_id'].site_code:
    #         raise serializers.ValidationError("diagnosis1_id and diagnosis2_id mismatch")
    #
    #     if attrs['cust_code'] != attrs['diagnosis1_id'].cust_no.cust_code:
    #         raise serializers.ValidationError("cust_code mismatch")
    #
    #     return attrs



class SecuritylevellistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Securitylevellist
        fields = ['id','controlname','controldesc','controlstatus','controlparent']
        read_only_fields = ('id','controlname','controldesc','controlparent')


class StaffPlusSerializer(serializers.ModelSerializer):
    """
    most parts are identical to EmployeeSerializer. validation little bit different.
    use for StaffPlus APIs.
    TODO:   should be figure out a way to use same serializer (EmployeeSerializer) to both old stadd apis and
            staff plus apis without any conflicts.
    """
    id = serializers.IntegerField(source='pk',required=False)
    services =  serializers.SerializerMethodField()
    gender = serializers.CharField(source='Emp_sexesid.itm_name',required=False)
    jobtitle_name = serializers.CharField(source='EMP_TYPEid.level_desc',required=False)
    shift_name = serializers.SerializerMethodField()
    level_desc = serializers.CharField(source='LEVEL_ItmIDid.level_description',required=False)
    site_name = serializers.CharField(source='defaultSiteCodeid.itemsite_desc',required=False)

    emp_epf_employee = serializers.IntegerField(source='EMP_EPFid.emp_epf_employee',required=False)
    emp_epf_employer = serializers.IntegerField(source='EMP_EPFid.emp_epf_employer',required=False)

    # fmspw fields
    flgsales =  serializers.SerializerMethodField()
    flgappt =  serializers.SerializerMethodField()
    site_list = serializers.SerializerMethodField()

    def get_shift_name(self, obj):
        if obj.shift:
            att = obj.shift
            return str(att.attn_time) +" "+ "to" +" "+str(att.attn_mov_in)
        else:
            return None

    def get_services(self, obj):
        if obj.skills.all():
            string = ""
            for i in obj.skills.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None

    def get_flgsales(self,obj):
        try:
            fmspw = Fmspw.objects.filter(Emp_Codeid=obj).first()
            return fmspw.flgsales
        except:
            return False

    def get_flgappt(self,obj):
        try:
            fmspw = Fmspw.objects.filter(Emp_Codeid=obj).first()
            return fmspw.flgappt
        except:
            return False

    def get_site_list(self,obj):
        return EmpSitelist.objects.filter(Emp_Codeid=obj,isactive=True).values('Site_Codeid','site_code')

    class Meta:
        model = Employee
        fields = ['id','skills_list','emp_name','display_name','emp_phone1','emp_code','skills','services','flgsales','flgappt','site_list',
                  'emp_address', 'Emp_sexesid','gender','defaultSiteCodeid','defaultsitecode','site_name','emp_epf','emphoursalary',
                  'Site_Codeid','site_code', 'emp_dob','emp_joindate','shift','shift_name','emp_email','emp_pic','emp_salary','EMP_EPFid',
                  'EMP_TYPEid','jobtitle_name', 'is_login','pw_password','LEVEL_ItmIDid','level_desc','emp_isactive','flghourly',
                  "emp_nric","max_disc", 'emp_race', 'Emp_nationalityid', 'Emp_maritalid', 'Emp_religionid', 'emp_emer','emp_epf_employee',
                  'emp_emerno', 'emp_country', 'emp_remarks','show_in_trmt','show_in_appt','show_in_sales','emp_epf_employer']
        read_only_fields = ('updated_at','created_at','emp_code','branch')
        extra_kwargs = {
            'emp_email': {'required': False},
            'Site_Codeid': {'required': False},
            'emp_name': {'required': True},
        }


    def validate(self, data):
        """ validation for StaffPlusSerializer"""
        request = self.context['request']
        mandatory_list = ['emp_name','emp_isactive','display_name','max_disc','emp_joindate']
        for _field in mandatory_list:
            if not request.data.get(_field):
                raise serializers.ValidationError(f"{_field} Field is required.")


        # if 'skills_list' in data:
        #     if data['skills_list'] is not None:
        #         if ',' in data['skills_list']:
        #             res = data['skills_list'].split(',')
        #         else:
        #             res = data['skills_list'].split(' ')
        #         for t in res:
        #             id_val = int(t)
        #             if Stock.objects.filter(pk=id_val,item_isactive=False):
        #                 raise serializers.ValidationError("Services ID Does not exist!!")
        #
        #             if not Stock.objects.filter(pk=id_val,item_isactive=True):
        #                 raise serializers.ValidationError("Services ID Does not exist!!")


        # if 'Emp_sexesid' in data:
        #     if data['Emp_sexesid'] is not None:
        #         if Gender.objects.filter(pk=data['Emp_sexesid'].pk,itm_isactive=False):
        #             raise serializers.ValidationError("Gender ID Does not exist!!")
        #         if not Gender.objects.filter(pk=data['Emp_sexesid'].pk,itm_isactive=True):
        #             raise serializers.ValidationError("Gender ID Does not exist!!")


        if 'shift' in data:
            if data['shift'] is not None:
                if Attendance2.objects.filter(pk=data['shift'].pk):
                    raise serializers.ValidationError("Shift ID Does not exist!!")
                if not Attendance2.objects.filter(pk=data['shift'].pk):
                    raise serializers.ValidationError("Shift ID Does not exist!!")


        if 'Site_Codeid' in data:
            if data['Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Branch ID Does not exist!!")



        if 'defaultSiteCodeid' in data:
            if data['defaultSiteCodeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['defaultSiteCodeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['defaultSiteCodeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
        else:
            data['defaultSiteCodeid'] = data.get('Site_Codeid')


        if 'EMP_TYPEid' in data:
            if data['EMP_TYPEid'] is not None:
                if EmpLevel.objects.filter(id=data['EMP_TYPEid'].id,level_isactive=False):
                    raise serializers.ValidationError("Job Title ID Does not exist!!")
                if not EmpLevel.objects.filter(id=data['EMP_TYPEid'].id,level_isactive=True):
                    raise serializers.ValidationError("Job Title ID Does not exist!!")

        return data

    def create(self, validated_data):
        request = self.context['request']
        site_list = request.data.get('site_list', "").split(",")


        # fmspw = Fmspw.objects.filter(user=self.context['request'].user,pw_isactive=True).first()
        # Site_Codeid = fmspw.loginsite
        # site_code_str = str(Site_Codeid.itemsite_code)


        employee = Employee.objects.create(emp_name=validated_data.get('emp_name'),
                                           emp_phone1=validated_data.get('emp_phone1'),
                                           display_name=validated_data.get('display_name'),
                                           emp_address=validated_data.get('emp_address'),
                                           Emp_sexesid=validated_data.get('Emp_sexesid'),
                                           emp_dob=validated_data.get('emp_dob'),
                                           emp_joindate=validated_data.get('emp_joindate'),
                                           shift=validated_data.get('shift'),
                                           defaultSiteCodeid=validated_data.get('defaultSiteCodeid'),
                                           emp_pic=validated_data.get('emp_pic'),
                                           is_login=validated_data.get('is_login'),
                                           EMP_TYPEid=validated_data.get('EMP_TYPEid'),
                                           emp_isactive=validated_data.get('emp_isactive'),
                                           emp_nric=validated_data.get('emp_nric'),
                                           max_disc=validated_data.get('max_disc'),
                                           show_in_sales=validated_data.get('show_in_sales'),
                                           show_in_appt=validated_data.get('show_in_appt'),
                                           show_in_trmt=validated_data.get('show_in_trmt'),
                                           Site_Codeid=validated_data.get('Site_Codeid'),
                                           EMP_EPFid=validated_data.get('EMP_EPFid'),
                                           )

        # for s in site_list:
        #     try:
        #         _obj = EmpSitelist(Emp_Codeid=employee,Site_Codeid_id=int(s))
        #         _obj.save()
        #     except Exception as e:
        #         pass

        try:
            if not employee.Site_Codeid:
                employee.Site_Codeid_id = int(site_list[0])
                employee.save()
        except:
            pass
        # skills_data = validated_data.pop('skills_list')
        # if ',' in skills_data:
        #     res = skills_data.split(',')
        # else:
        #     res = skills_data.split(' ')
        # for skill in res:
        #     employee.skills.add(skill)
        return employee

    def update(self, instance, validated_data):
        request = self.context['request']
        site_list = request.data.get('site_list',"").split(",")

        instance.emp_name = validated_data.get("emp_name", instance.emp_name)
        instance.display_name = validated_data.get("display_name", instance.display_name)
        instance.emp_phone1 = validated_data.get("emp_phone1", instance.emp_phone1)
        instance.emp_address = validated_data.get("emp_address", instance.emp_address)
        instance.Emp_sexesid = validated_data.get("Emp_sexesid", instance.Emp_sexesid)
        instance.emp_dob = validated_data.get("emp_dob", instance.emp_dob)
        instance.emp_joindate = validated_data.get("emp_joindate", instance.emp_joindate)
        instance.shift = validated_data.get("shift", instance.shift)
        instance.emp_pic = validated_data.get("emp_pic", instance.emp_pic)
        instance.EMP_TYPEid = validated_data.get("EMP_TYPEid", instance.EMP_TYPEid)
        instance.defaultSiteCodeid = validated_data.get("defaultSiteCodeid", instance.defaultSiteCodeid)
        instance.defaultsitecode = instance.defaultSiteCodeid.itemsite_code if instance.defaultSiteCodeid else None
        instance.Site_Codeid = validated_data.get("Site_Codeid", instance.Site_Codeid)
        instance.emp_nric = validated_data.get("emp_nric", instance.emp_nric)
        instance.max_disc = validated_data.get("max_disc", instance.max_disc)
        instance.site_code = instance.Site_Codeid.itemsite_code,
        # fields that have defaults value in model, are returning default val in validated_data
        # ether request does or doesn't have it.
        instance.emp_isactive = request.data.get("emp_isactive", instance.emp_isactive)
        instance.show_in_sales = request.data.get("show_in_sales",instance.show_in_sales)
        instance.show_in_appt = request.data.get("show_in_appt", instance.show_in_appt)
        instance.show_in_trmt = request.data.get("show_in_trmt", instance.show_in_trmt)
        instance.EMP_EPFid = validated_data.get("EMP_EPFid", instance.EMP_EPFid)
        instance.emp_epf = validated_data.get("emp_epf", instance.emp_epf)
        instance.flghourly = validated_data.get("flghourly", instance.flghourly)
        instance.emp_salary = validated_data.get("emp_salary", instance.emp_salary)
        instance.emphoursalary = validated_data.get("emphoursalary", instance.emphoursalary)

        if 'emp_email' in validated_data:
            if validated_data['emp_email'] is not None:
                instance.emp_email = validated_data.get("emp_email", instance.emp_email)

        try:
            if not instance.Site_Codeid:
                instance.Site_Codeid_id = int(site_list[0])
        except:
            pass

        instance.save()

        # update site list
        old_sites = EmpSitelist.objects.filter(Emp_Codeid=instance)
        for o in old_sites:
            o.delete()

        for s in site_list:
            try:
                _obj = EmpSitelist(Emp_Codeid=instance,Site_Codeid_id=int(s))
                _obj.save()
            except Exception as e:
                pass

        # _Fmspw = Fmspw.objects.filter(Emp_Codeid=instance).first()
        # if _Fmspw:
        #     _Fmspw.flgsales =  instance.show_in_sales
        #     _Fmspw.flgappt =  instance.show_in_appt
        #     _Fmspw.save()

        return instance

class EmpInfoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', required=False)
    # site_id = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'emp_code', 'emp_name',
                  'emp_phone1','emp_address','Emp_sexesid','emp_race','Emp_nationalityid','Emp_maritalid','Emp_religionid',
                  'emp_emer','emp_emerno','emp_country','emp_remarks','show_in_sales','show_in_appt','show_in_trmt']
        # extra_kwargs = {'site_id': {'required': False}}

    def validate(self, data):
        request = self.context['request']
        # if not 'site_id' in request.data:
        #     raise serializers.ValidationError("site_id Field is required.")
        # else:
        #     if request.data['site_id'] is None:
        #         raise serializers.ValidationError("site_id Field is required!!")

        return data

    def update(self, instance, validated_data):
        instance.emp_phone1 = validated_data.get("emp_phone1", instance.emp_phone1)
        instance.emp_address = validated_data.get("emp_address", instance.emp_address)
        instance.Emp_sexesid = validated_data.get("Emp_sexesid", instance.Emp_sexesid)
        instance.Emp_nationalityid = validated_data.get("Emp_nationalityid", instance.Emp_nationalityid)
        instance.Emp_maritalid = validated_data.get("Emp_maritalid", instance.Emp_maritalid)
        instance.Emp_religionid = validated_data.get("Emp_religionid", instance.Emp_religionid)
        instance.emp_emer = validated_data.get("emp_emer", instance.emp_emer)
        instance.emp_emerno = validated_data.get("emp_emerno", instance.emp_emerno)
        instance.emp_remarks = validated_data.get("emp_remarks", instance.emp_remarks)
        instance.emp_country = validated_data.get("emp_country", instance.emp_country)
        instance.emp_race = validated_data.get("emp_race", instance.emp_race)


        # todo:
        #   country, emergancy person, emergncy contact number
        instance.save()
        return instance

class CustomerClassSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomerClass
        fields = ["id","class_desc","class_code"]

class CustomerPlusnewSerializer(serializers.ModelSerializer):   

    id = serializers.IntegerField(source='pk',required=False)  
    gender = serializers.CharField(source='Cust_sexesid.itm_name',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)
    class_name = serializers.CharField(source='Cust_Classid.class_desc',required=False)
    custClass = CustomerClassSerializer(source="Cust_Classid",read_only=True)


    class Meta:
        model = Customer
        fields = ['id','cust_code','cust_name','cust_address','Site_Codeid','site_name','site_code','last_visit',
                  'custClass', 'class_name', 'Cust_Classid', 'cust_joindate','Cust_Sourceid','cust_nric',
                  'upcoming_appointments','cust_dob','cust_phone2','cust_phone1','Cust_sexesid',
                  'gender', 'cust_postcode','sgn_unitno','sgn_block','sgn_street', 'Cust_titleid',
                  'cust_remark','cust_source',
                  'cust_email', 'cardno1','cardno2','cardno3','cardno4','cardno5','phone4','cust_phoneo','cust_therapist_id',
                  'cust_consultant_id','cust_address1','cust_address2','cust_address3',
                  'prepaid_card','cust_occupation', 'creditnote','voucher_available','oustanding_payment','cust_refer',
                  'custallowsendsms','cust_maillist','cust_title','cust_sexes','cust_class','cust_corporate']
        read_only_fields = ('cust_isactive','created_at', 'updated_at','last_visit','upcoming_appointments',
        'Site_Code','cust_code','ProneToComplain')
        extra_kwargs = {'cust_name': {'required': True},'cust_phone2': {'required': False},}
   


class CustomerPlusSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    gender = serializers.CharField(source='Cust_sexesid.itm_name',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)
    class_name = serializers.CharField(source='Cust_Classid.class_desc',required=False)
    custClass = CustomerClassSerializer(source="Cust_Classid",read_only=True)
    masked_nric = serializers.SerializerMethodField()

    

    def get_masked_nric(self,obj):
        _nric = obj.cust_nric if obj.cust_nric else ""
        if len(_nric) > 4:
            _str = '*' * (len(_nric) - 4)
            _nric = _str + _nric[-4:]
        return _nric

    def to_representation(self, data):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True).order_by('-pk')
        site = fmspw[0].loginsite
        
        data = super(CustomerPlusSerializer,self).to_representation(data)
        data['cust_nric'] = data.get("masked_nric")
        data['Cust_sexesid'] = ""; data['Cust_Classid'] = ""
        if data['cust_sexes']:
            gender = Gender.objects.filter(itm_code=data['cust_sexes'],itm_isactive=True).first()
            if gender:
                data['Cust_sexesid'] = gender.itm_name if gender.itm_name else ""

        data['Cust_titleid'] = "" 
        if data['cust_title']: 
            title_obj = CustomerTitle.objects.filter(itm_code=data['cust_title'],isactive=True).first()
            if title_obj:
                data['Cust_titleid'] = title_obj.itm_desc if title_obj.itm_desc else ""
        
        data['Cust_Sourceid'] = "" 
        if data['cust_source']: 
            source_obj = Source.objects.filter(source_code=data['cust_source'],source_isactive=True).first()
            if source_obj:
                data['Cust_Sourceid'] = source_obj.source_desc if source_obj.source_desc else ""


        if data['cust_class']:
            classobj = CustomerClass.objects.filter(class_code=data['cust_class'],class_isactive=True).first()
            if classobj:
                data['Cust_Classid'] = classobj.class_desc if classobj.class_desc else ""

        data['iscurrent'] = ""
        if data['site_code'] == site.itemsite_code:
            data['iscurrent'] = True
        elif data['site_code'] != site.itemsite_code:
            data['iscurrent'] = False

        system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
        value_name='Other Outlet Customer Listings',isactive=True).first()

        system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Void',
        value_name='Other Outlet Customer Void',isactive=True).first()  

        data['is_allow']  = False
        if data['site_code']:
            if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                if data['site_code'] != site.itemsite_code or data['site_code'] == site.itemsite_code:
                    data['is_allow'] = True
            else:
                if data['site_code'] == site.itemsite_code:
                    data['is_allow'] = True    
    
        # print(data.get("cust_joindate"),type(data.get("cust_joindate")))

        try:
            join_date = data.get("cust_joindate")
            data['cust_joindate'] = join_date.split("T")[0]
        except:
            pass

        return data

    class Meta:
        model = Customer
        fields = ['id','cust_code','cust_name','cust_address','Site_Codeid','site_name','site_code','last_visit',
                  'custClass', 'class_name', 'Cust_Classid', 'cust_joindate','Cust_Sourceid','cust_nric',
                  'upcoming_appointments','cust_dob','cust_phone2','cust_phone1','Cust_sexesid',
                  'gender', 'cust_postcode','sgn_unitno','sgn_block','sgn_street', 'Cust_titleid',
                  'masked_nric','cust_remark','cust_source',
                  'cust_email', 'cardno1','cardno2','cardno3','cardno4','cardno5','phone4','cust_phoneo','cust_therapist_id',
                  'cust_consultant_id','cust_address1','cust_address2','cust_address3',
                  'prepaid_card','cust_occupation', 'creditnote','voucher_available','oustanding_payment','cust_refer',
                  'custallowsendsms','cust_maillist','cust_title','cust_sexes','cust_class','cust_corporate']
        read_only_fields = ('cust_isactive','created_at', 'updated_at','last_visit','upcoming_appointments',
        'Site_Code','cust_code','ProneToComplain')
        extra_kwargs = {'cust_name': {'required': True},'cust_phone2': {'required': False},}


    def validate(self, data):
        request = self.context['request']

        action = self.context.get('action')

        # customer form settings validation
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
        site = fmspw[0].loginsite
        form_control_qs = CustomerFormControl.objects.filter(isActive=True,Site_Codeid=site)
        allowed_fields = []

        # if action == "list":
        #     allowed_fields = form_control_qs.filter(visible_in_listing=True).values_list("field_name",flat=True)
        # elif action == "retrieve":
        #     allowed_fields = form_control_qs.filter(visible_in_profile=True).values_list("field_name",flat=True)
        # if action == "create":
        #     allowed_fields = form_control_qs.filter(visible_in_registration=True) #.values_list("field_name",flat=True)
        #
        validate_data = {}
        if action == "update":
            allowed_fields = form_control_qs.filter(visible_in_registration=True).values_list("field_name",flat=True)
        elif action == 'create':
            allowed_fields = form_control_qs.filter(visible_in_registration=True).values_list("field_name",flat=True)

        for f in allowed_fields:
            if hasattr(Customer,f) and f in data:
                validate_data[f] = data[f]


        mandatory_fields = form_control_qs.filter(visible_in_registration=True,mandatory=True).values_list("field_name", flat=True)
        for _field in mandatory_fields:
            # if request.data.get(_field) is None:
            if validate_data.get(_field) is None:
                raise serializers.ValidationError(f"{_field} Field is required.")


        # if not 'cust_name' in request.data:
        #     raise serializers.ValidationError("cust_name Field is required.")
        # else:
        #     if request.data['cust_name'] is None:
        #         raise serializers.ValidationError("cust_name Field is required.")
        # # if not 'cust_address' in request.data:
        # #     raise serializers.ValidationError("cust_address Field is required.")
        # # else:
        # #     if request.data['cust_address'] is None:
        # #         raise serializers.ValidationError("cust_address Field is required.")
        # # if not 'cust_dob' in request.data:
        # #     raise serializers.ValidationError("cust_dob Field is required.")
        # # else:
        # #     if request.data['cust_dob'] is None:
        # #         raise serializers.ValidationError("cust_dob Field is required.")
        # if not 'cust_phone2' in request.data:
        #     raise serializers.ValidationError("cust_phone2 Field is required.")
        # else:
        #     if request.data['cust_phone2'] is None:
        #         raise serializers.ValidationError("cust_phone2 Field is required.")
        # if not 'Cust_sexesid' in request.data:
        #     raise serializers.ValidationError("Cust_sexesid Field is required.")
        # else:
        #     if request.data['Cust_sexesid'] is None:
        #         raise serializers.ValidationError("Cust_sexesid Field is required.")
        # if not 'Site_Codeid' in request.data:
        #     raise serializers.ValidationError("Site_Codeid Field is required.")
        # else:
        #     if request.data['Site_Codeid'] is None:
        #         raise serializers.ValidationError("Site_Codeid Field is required.")

        if 'Cust_sexesid' in data:
            if data['Cust_sexesid'] is not None:
                if Gender.objects.filter(pk=data['Cust_sexesid'].pk,itm_isactive=False):
                    raise serializers.ValidationError("Gender ID Does not exist!!")

                if not Gender.objects.filter(pk=data['Cust_sexesid'].pk,itm_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Gender Id does not exist!!",'error': True}
                    raise serializers.ValidationError(result)
        if 'Site_Codeid' in data:
            if data['Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")

        # if not 'cust_maillist' in request.data:
        #     raise serializers.ValidationError("cust_maillist Field is required.")
        # else:
        #     if request.data['cust_maillist'] is None:
        #         raise serializers.ValidationError("cust_maillist Field is required.")
        # if not 'custallowsendsms' in request.data:
        #     raise serializers.ValidationError("custallowsendsms Field is required.")
        # else:
        #     if request.data['custallowsendsms'] is None:
        #         raise serializers.ValidationError("custallowsendsms Field is required.")
        # Email and Mobile number validation
        # if request.data['cust_email']:
        #     customer_mail =  Customer.objects.filter(cust_email=request.data['cust_email'])
        #     if len(customer_mail) > 0:
        #         raise serializers.ValidationError("Email id is already associated with another account")
        # customer =  Customer.objects.filter(cust_phone2=request.data['cust_phone2'])
        # if len(customer) > 0:
        #     raise serializers.ValidationError("Mobile number is already associated with another account")
        return validate_data

    # def update(self, instance, validated_data):
    #     update_fields = form_control_qs.filter(mandatory=True).values_list("field_name",flat=True)

class SkillSerializer(serializers.ModelSerializer):
    # Item_Class = serializers.CharField(source='Item_Classid.itm_desc',required=False)

    class Meta:
        model = Stock
        fields = ['item_no','item_desc','item_name','item_price','item_code']
        read_only_fields = ('item_code','item_no')


class DailysalesdataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailysalesdataDetail
        fields = '__all__'

class DailysalesdataSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailysalesdataSummary
        fields = '__all__'

class CustomerPointSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super(CustomerPointSerializer, self).to_representation(instance)
        if data['total_point'] < 0:
            data['total_point'] *= -1
            data['lp_type'] = "Redeem"
        else:
            data['lp_type'] = "Reward"

        return data


    class Meta:
        model = CustomerPoint
        # fields = '__all__'
        fields = ['id','transacno','username','cust_name','cust_code','locid','type','sa_status','postransactionno','total_point','now_point','remarks','date']
        read_only_fields = ('id',)



    # def to_representation(self, data):
    #     data = super(DailysalesdataSummarySerializer,self).to_representation(data)
    #
    #     data['total'] = data.get("masked_nric")
    #
    #     return data

class DepartmentReport(serializers.Serializer):
    # 'sa_date', 'itemsite_code', 'sa_transacno_ref', 'deposit', 'discount',
    # 'item_code', 'itemDesc', 'Qty', 'record_detail_type', 'GT1_actamt', 'GT2_actamt', 'Ttl_actamt', 'Pay_OldBill'
    sa_date = serializers.DateTimeField()
            

class AboutSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Title
        fields = ['id','title','company_reg_no','license_key','valid_date','version_no']

    def to_representation(self, obj):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
        site = fmspw[0].loginsite
       
        mapped_object = {'id':obj.id,'company_name':obj.title if obj.title else "",
        'uen_number': obj.company_reg_no if obj.company_reg_no else "",
        'license_key': obj.license_key if obj.license_key else "",
        'valid_date': datetime.datetime.strptime(str(obj.valid_date), "%Y-%m-%d").strftime("%d-%m-%Y") if obj.valid_date else "",
        'version_no': obj.version_no if obj.version_no else "",
        'sitecode': site.itemsite_code,'version_type':obj.version_type if obj.version_type else ""}
        return mapped_object    


class SMSReplySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Smsreceivelog
        fields = ['id','handledby']

    def to_representation(self, obj):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
        site = fmspw[0].loginsite
        cust_obj = Customer.objects.filter(cust_code=obj.customercode,cust_isactive=True).order_by('-pk').first()
        appt_obj = Appointment.objects.filter(appt_isactive=True,pk=obj.appointmentcode).order_by('-pk').first()
        appt_date = "";starttime = ""
        if appt_obj and appt_obj.appt_date:
            appt_date = datetime.datetime.strptime(str(appt_obj.appt_date), "%Y-%m-%d").strftime("%d-%b-%Y %H:%M")
        
        if appt_obj and appt_obj.appt_fr_time:
            starttime = datetime.datetime.strptime(str(appt_obj.appt_fr_time), "%H:%M:%S").strftime("%H:%M")    

        date = datetime.datetime.strptime(str(obj.receivedtime), "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M")
        mapped_object = {'id':obj.id,'date':date,'cust_name':obj.customername,
        'cust_refer' : cust_obj.cust_refer if cust_obj and cust_obj.cust_refer else "",
        'site_code': appt_obj.itemsite_code if appt_obj and appt_obj.itemsite_code else "",
        'phone':obj.sender, 'reply': obj.message,'appt_date':appt_date+" "+starttime,
        'service_name': appt_obj.appt_remark if appt_obj and appt_obj.appt_remark else "",
        'staff_name': appt_obj.emp_name if appt_obj and appt_obj.emp_name else "", 
        'appt_status': appt_obj.appt_status if appt_obj and appt_obj.appt_status else "",}
        return mapped_object     


class ConfirmBookingApptSerializer(serializers.ModelSerializer):   

    id = serializers.IntegerField(source='pk',required=False)
    appt_date = serializers.DateField(format="%d-%b-%Y")
    appt_fr_time = serializers.TimeField(format='%H:%M:%S')
    is_del = serializers.SerializerMethodField()
    is_book = serializers.SerializerMethodField()

    def get_is_del(self, obj):
        return None  
    
    def get_is_book(self, obj):
        return None  

    class Meta:
        model = Appointment
        fields = ['id','appt_date','appt_fr_time','emp_name','appt_status',
        'appt_phone','cust_name','itemsite_code','is_del','is_book']
    
    def to_representation(self, obj):
        data = super(ConfirmBookingApptSerializer, self).to_representation(obj)
        cust_obj = Customer.objects.filter(cust_code=obj.cust_no,cust_isactive=True).order_by('-pk').first()
        
        data['appt_phone'] = cust_obj.cust_phone2 if cust_obj and cust_obj.cust_phone2 else "" 
        data['date_time'] = ""
        if data['appt_date'] and data['appt_fr_time']:
            time = datetime.datetime.strptime(str(data['appt_fr_time']),"%H:%M:%S").strftime("%I:%M:%S %p")
            data['date_time'] = data['appt_date'] +" "+time
        data['appt_fr_time'] = datetime.datetime.strptime(str(data['appt_fr_time']),"%H:%M:%S").strftime("%I:%M %p")
        return data


class ItemDescSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TreatmentProtocol
        fields = ['id','protocol_detail','line_no']

class TempcustsignSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tempcustsign
        fields = ['id','cust_code','transaction_no','cust_sig','site_code']  

class CustomerDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerDocument
        fields = ['id','customer_id','filename','document_name','file']  
            
    def to_representation(self, obj):
        request = self.context['request']
        data = super(CustomerDocumentSerializer, self).to_representation(obj)
        
        ip = "http://"+request.META['HTTP_HOST']
        file = ""
        if obj.file:
            file = ip+str(obj.file.url)

        data['file'] = file
        return data        


class TreatmentPackageSerializer(serializers.ModelSerializer): 

    class Meta:
        model = TreatmentPackage
        fields = ['id','treatment_parentcode','course','treatment_no','open_session','done_session',
        'cancel_session','unit_amount','cust_name']  
            
    def to_representation(self, obj):
        data = super(TreatmentPackageSerializer, self).to_representation(obj)
        
        data['unit_amount'] = "{:.2f}".format(data['unit_amount'])
        return data  
        
class ItemSitelistIntialSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemSitelist
        fields = ['id','itemsite_code','itemsite_desc']  
                            

class StaffInsertSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Employee
        fields = ['id','emp_name']  
                                  
class FmspwSerializernew(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Fmspw
        fields = ['id','pw_userlogin']  
     
class GenderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    
    class Meta:
        model = Gender
        fields = ['id','itm_name','itm_code']        

class ContactPersonSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ContactPerson
        fields = '__all__'


class ItemFlexiserviceSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemFlexiservice
        fields = ['id','item_srvdesc','item_srvid']          