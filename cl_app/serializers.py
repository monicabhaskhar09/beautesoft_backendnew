from rest_framework import serializers
from .models import (SiteGroup,ItemSitelist,ReverseTrmtReason,VoidReason,TreatmentUsage,UsageMemo,
Treatmentface)
from cl_table.models import (ItemDept, ItemRange, Stktrn, Stock, TreatmentAccount, Treatment,DepositAccount,
PrepaidAccount,PosHaud,PosDaud, Customer, PosTaud,CreditNote,PrepaidAccountCondition,Fmspw,Holditemdetail,
ItemLink,Systemsetup,Employee,Multistaff,ItemDiv,TreatmentPackage)
from django.utils import timezone
from django.db.models import Sum
from custom.views import round_calc
from custom.models import ItemCart,VoucherRecord,ManualInvoiceModel
from datetime import date, timedelta, datetime
import datetime

class SiteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteGroup
        fields = ['id','description','is_active','created_at']
        read_only_fields = ('created_at','is_active') 

class CatalogItemDeptSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemDept
        fields = ['id','itm_code','itm_desc','itm_seq']

class ItemRangeSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
   
    class Meta:
        model = ItemRange
        fields = ['id','itm_code','itm_desc']

class ItemDivSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
   
    class Meta:
        model = ItemDiv
        fields = ['id','itm_code','itm_desc']

    def to_representation(self, instance):
        data = super(ItemDivSerializer, self).to_representation(instance)
        data['desc'] = ""
        if instance.itm_desc:
            # data['desc'] = instance.itm_desc +" "+"-"+" "+ instance.itm_code
            data['desc'] = instance.itm_desc            
        return data    
    

class StockSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','item_name','item_desc','item_div','item_type','Stock_PIC','item_price','prepaid_value','redeempoints']
    
    def to_representation(self, instance):
        data = super(StockSerializer, self).to_representation(instance)
        data['item_price'] = ""
        if instance.item_price:
            data['item_price'] = "{:.2f}".format(float(instance.item_price)) 
        return data 

class StockRetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','item_name','item_desc','item_div','item_type','Stock_PIC','item_code','item_price']
    
    def to_representation(self, instance):
        data = super(StockRetailSerializer, self).to_representation(instance)
        data['item_price'] = ""
        if instance.item_price:
            data['item_price'] = "{:.2f}".format(float(instance.item_price)) 
        return data 

class StockIdSerializer(serializers.Serializer): 
    stock_id = serializers.IntegerField(required=True)

class OtpRequestSerializer(serializers.Serializer):
    emp_name = serializers.CharField(required=True)

class OtpValidationSerializer(serializers.Serializer):
    emp_name = serializers.CharField(required=False)
    otp = serializers.CharField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    emp_name = serializers.CharField(required=False)
    new_password = serializers.CharField(required=True)

class CustomerSignSerializer(serializers.Serializer):
    customersign = serializers.CharField()

class TreatmentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentAccount
        fields = ['id','sa_date','qty','sa_transacno','treatment_parentcode','description','balance','outstanding','sa_staffname']

class TopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentAccount
        fields = ['id','sa_date','description','type','amount','balance','outstanding']

class TreatmentDoneSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id','treatment_date','treatment_code','sa_transacno','course','type',
        'expiry','unit_amount','status','times','isfoc','treatment_parentcode','treatment_no','site_code']

class TopupproductSerializer(serializers.ModelSerializer):

    description = serializers.CharField(source='item_description',required=False)

    class Meta:
        model = DepositAccount
        fields = ['id','sa_date','qty','description','sa_transacno','balance','outstanding','sa_staffname']

class TopupprepaidSerializer(serializers.ModelSerializer):
    
    description = serializers.CharField(source='pp_desc',required=False)
    sa_staffname = serializers.CharField(source='staff_name',required=False)
    class Meta:
        model = PrepaidAccount
        fields = ['id','pp_desc','sa_date','description','exp_date','remain','outstanding','staff_name','sa_staffname']

class TreatmentReversalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id','treatment_code','course','unit_amount']

class ShowBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentAccount
        fields = ['id','treatment_parentcode','balance','outstanding']

class ReverseTrmtReasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReverseTrmtReason
        fields = ['id','rev_desc']

class VoidSerializer(serializers.ModelSerializer):
   
    is_current = serializers.SerializerMethodField() 
    is_allow = serializers.SerializerMethodField() 

    def get_is_current(self, obj):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True).order_by('-pk')
        site = fmspw[0].loginsite

        iscurrent = ""
        if obj.itemsite_code == site.itemsite_code:
            iscurrent = True
        elif obj.itemsite_code != site.itemsite_code:
            iscurrent = False
 
        return iscurrent  

    def get_is_allow(self, obj): 
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True).order_by('-pk')
        site = fmspw[0].loginsite
        system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
        value_name='Other Outlet Customer Listings',isactive=True).first()

        system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Void',
        value_name='Other Outlet Customer Void',isactive=True).first()  

        is_allow  = False
        if obj.itemsite_code:
            if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                if obj.itemsite_code != site.itemsite_code or obj.itemsite_code == site.itemsite_code:
                    is_allow = True
            else:
                if obj.itemsite_code == site.itemsite_code:
                    is_allow = True

        return is_allow         

    class Meta:
        model = PosHaud
        fields = ['id','sa_transacno_ref','sa_custno','sa_custname','sa_date','sa_status',
        'void_refno','payment_remarks','sa_reason','is_current','itemsite_code','is_allow']
    
    

class VoidListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosHaud
        fields = ['cart_id']

class VoidCancelSerializer(serializers.Serializer):

    cart_id = serializers.CharField(required=True)



class PosDaudDetailsSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
    desc = serializers.SerializerMethodField() 

    def get_desc(self, obj):
        if obj:
            desc = str(obj.dt_itemdesc)+" "+"$$"+" "+str("{:.2f}".format(float(obj.dt_promoprice)))
        else:
            desc = None  
        return desc      
    
    class Meta:
        model = PosDaud
        fields = ['id','dt_itemdesc','dt_amt','desc','dt_qty']


class VoidReasonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VoidReason
        fields = ['id','reason_desc']

class TreatmentAccSerializer(serializers.ModelSerializer):

    payment = serializers.FloatField(source='amount',required=False)

    class Meta:
        model = TreatmentAccount
        fields = ['id','sa_date','treatment_parentcode','description','payment','balance','outstanding']
    
    # def to_representation(self, instance):
    #     fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
    #     site = fmspw.loginsite  
    #     trobj = instance
    #     print(trobj.pk,"trobj") 
    #     cust_obj = Customer.objects.filter(cust_code=trobj.cust_code,cust_isactive=True).only('cust_code','cust_isactive').first()
    #     pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
    #     sa_transacno=trobj.sa_transacno,sa_transacno_type='Receipt',
    #     ItemSite_Codeid__pk=site.pk).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
    #     if pos_haud:
    #         sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #         treatment_parentcode=trobj.treatment_parentcode,site_code=trobj.site_code,
    #         type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').aggregate(Sum('balance'))
            
    #         acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #         treatment_parentcode=trobj.treatment_parentcode,site_code=trobj.site_code).only('ref_transacno','treatment_parentcode','site_code').last()
    #         # if data["balance"]:
    #         # data["balance"] = 
    #         # # if data["outstanding"]:
    #         # data["outstanding"] = 
    #         # outstanding += acc_ids.outstanding
    #         # if data["amount"]:
            
    #         mapped_object = {'id': instance.pk,'sa_date':pos_haud.sa_date if pos_haud.sa_date else None,
    #         'transaction':pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else None,
    #         'description': trobj.description,'payment':"{:.2f}".format(float(sumacc_ids['balance__sum'])) if sumacc_ids else 0.0,
    #         'balance': "{:.2f}".format(float(acc_ids.balance)) if acc_ids else 0.0,
    #         'outstanding': "{:.2f}".format(float(acc_ids.outstanding)) if acc_ids else 0.0}
    #         return mapped_object

class CreditNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNote
        fields = ['id','credit_code','sa_date','amount','balance','status']

class CreditNoteAdjustSerializer(serializers.ModelSerializer):
    new_balance = serializers.FloatField(source='balance',required=True)
    refund_amt = serializers.SerializerMethodField()

    class Meta:
        model = CreditNote
        fields = ['id','credit_code','balance','new_balance','refund_amt']
        extra_kwargs = {'refund_amt': {'required': True}}
    
    def get_refund_amt(self, obj):
        return "{:.2f}".format(float(0.00))
    

    def validate(self, data):
        request = self.context['request']
        if not 'new_balance' in request.data:
            raise serializers.ValidationError("new_balance Field is required.")
        else:
            if request.data['new_balance'] is None: 
                raise serializers.ValidationError("new_balance Field is required!!")
        if not 'refund_amt' in request.data:
            raise serializers.ValidationError("refund_amt Field is required.")
        else:
            if request.data['refund_amt'] is None: 
                raise serializers.ValidationError("refund_amt Field is required!!")
        return data      


class ProductAccSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositAccount
        fields = ['id','sa_date','package_code','qty','item_description','balance','outstanding']

class PrepaidAccSerializer(serializers.ModelSerializer):
    last_update = serializers.DateTimeField(source='sa_date',required=False)

    class Meta:
        model = PrepaidAccount
        fields = ['id','pp_no','pp_desc','last_update','sa_date','exp_date','exp_status',
        'pp_amt','pp_bonus','pp_total','use_amt','remain','voucher_no','topup_amt','outstanding',
        'condition_type1','line_no','cust_code']

class PrepaidacSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrepaidAccount
        fields = ['id','item_no','use_amt','topup_amt','sa_date']        

class DashboardSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemSitelist
        fields = ['id']

    def to_representation(self, instance):
        repeat_cust = [];cust_repeat = 0;pay_amount = 0
        today = timezone.now().date()
        month = today.month
        sitecust_cnt = Customer.objects.filter(site_code=instance.itemsite_code).only('site_code').count()
        sitenewcust_cnt = Customer.objects.filter(site_code=instance.itemsite_code,created_at__date__month=month).only('site_code','created_at').count()
        products_ids = PosDaud.objects.filter(ItemSite_Codeid__pk=instance.pk,created_at__date__month=month,
        dt_itemnoid__item_div=1,record_detail_type='PRODUCT',dt_qty__gt = 0).only('itemsite_code','created_at','dt_itemnoid','record_detail_type','dt_qty').aggregate(Sum('dt_qty'))
        products_cnt = "{:.2f}".format(float(products_ids['dt_qty__sum'])) if products_ids['dt_qty__sum'] else 0   
        service_ids = PosDaud.objects.filter(ItemSite_Codeid__pk=instance.pk,created_at__date__month=month,
        dt_itemnoid__item_div=3,record_detail_type='SERVICE',dt_qty__gt = 0).only('itemsite_code','created_at','dt_itemnoid','record_detail_type','dt_qty').aggregate(Sum('dt_qty'))
        service_cnt = "{:.2f}".format(float(service_ids['dt_qty__sum'])) if service_ids['dt_qty__sum'] else 0
        custids = Customer.objects.filter(site_code=instance.itemsite_code).only('site_code','cust_code').values_list('cust_code', flat=True)
        recustids = PosHaud.objects.filter(ItemSite_Codeid__pk=instance.pk,created_at__date__month=month,
        sa_custno__in=custids).only('itemsite_code','created_at','sa_custno').values_list('sa_custno', flat=True)
       
        recust =list(recustids)
        for c in custids:
            if c in recust:
                cusid = recust.count(c)
                if cusid > 1 and c not in repeat_cust:
                    repeat_cust.append(c)
        
        if repeat_cust !=[]:
            cust_repeat = len(repeat_cust)
       
        payids = PosTaud.objects.filter(ItemSIte_Codeid__pk=instance.pk,created_at__date__month=month,pay_amt__gt = 0).only('itemsite_code','created_at').aggregate(Sum('pay_amt'))
        
        round_val = float(round_calc(payids['pay_amt__sum'],instance)[0]) if payids['pay_amt__sum'] else 0 # round()
        if payids['pay_amt__sum']:
            # pay_amount = float(payids['pay_amt__sum']) + round_val 
            pay_amount = round_val 

        mapped_object = {'id': instance.pk,'customer_site':sitecust_cnt,'new_customer':sitenewcust_cnt,
        'product':int(float(products_cnt)),'services':int(float(service_cnt)),'repeat_customer':cust_repeat if cust_repeat else 0,
        'monthly_earnigs':"{:.2f}".format(float(pay_amount)) if pay_amount else "0.00"}
        return mapped_object


class TransactionInvoiceSerializer(serializers.ModelSerializer):
    flag = serializers.BooleanField(default=True)
    cust_name = serializers.CharField(source='sa_custnoid.cust_name',required=False)

    
    class Meta:
        model = PosHaud
        fields = ['id','sa_transacno_ref','flag','cust_name'] 

class TransactionManualInvoiceSerializer(serializers.ModelSerializer):

    sa_transacno_ref = serializers.CharField(source='manualinv_number',required=False)
    flag = serializers.BooleanField(default=False)


    
    class Meta:
        model = ManualInvoiceModel
        fields = ['id','sa_transacno_ref','flag'] 

    def to_representation(self, instance):
       
        data = super(TransactionManualInvoiceSerializer, self).to_representation(instance)

        data['cust_name'] = instance.cust_id.cust_name if instance.cust_id and instance.cust_id.cust_name else ""
 
        return data      


class BillingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PosHaud
        fields = ['id','sa_custno','sa_custname','sa_date','sa_totamt','sa_transacno_ref','void_refno',
        'sa_staffname','sa_status','sa_transacno','sa_transacno_type','isvoid','itemsite_code'] 


    def to_representation(self, instance):
        request = self.context['request']
        sales_staffs = request.GET.get('sales_staffs',None)
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        sa_date = ""
        if instance.sa_date:
            splt = str(instance.sa_date).split(".")
            dtime = str(instance.sa_time).split(" ")
            time = dtime[1].split(":")

            time_data = time[0]+":"+time[1]
    
            sa_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%y")+" "+str(time_data)

        if instance.isvoid == False:
            void_refno = ""
        else:
            sa_ids = PosHaud.objects.filter(void_refno=instance.sa_transacno,
            ItemSite_Codeid__pk=site.pk,sa_custno=instance.sa_custno).order_by('pk').first()
            if sa_ids:
                void_refno = sa_ids.sa_transacno_ref
            else:
                void_refno = ""

        taud = PosTaud.objects.filter(sa_transacno=instance.sa_transacno,ItemSIte_Codeid__pk=site.pk)

        payment_remarks = ','.join([v.pay_rem4 for v in taud if v.pay_rem4]) 

        daud = PosDaud.objects.filter(sa_transacno=instance.sa_transacno).order_by('pk') 
        item = ''.join([v.dt_itemdesc for v in daud if v.dt_itemdesc]) 

        is_current = ""
        if instance.itemsite_code == site.itemsite_code:
            is_current = True 
        elif instance.itemsite_code != site.itemsite_code:
            is_current = False 

        system_setup = Systemsetup.objects.filter(title='Multistaff Salestaff Amount',
        value_name='Multistaff Salestaff Amount',isactive=True).first() 

        
        sales_amt = 0.0
        if sales_staffs:
            salesstaff = str(sales_staffs).split(',') 
            emp_ids = Employee.objects.filter(emp_isactive=True,pk__in=salesstaff,show_in_sales=True).order_by('-pk')
            # print(emp_ids,"emp_ids")
            if emp_ids:
                for d in daud:
                    amount = d.dt_transacamt
                    if system_setup and system_setup.value_data == 'TransacAmt':
                        amount = d.dt_transacamt
                    elif system_setup and system_setup.value_data == 'DepositAmt': 
                        amount = d.dt_deposit

                    salestaff_cnt = Multistaff.objects.filter(dt_lineno=d.dt_lineno,sa_transacno=d.sa_transacno).order_by('-pk').count()
                    # print(sales_multi,"sales_multi")
                    for h in emp_ids:
                        sales_multi = Multistaff.objects.filter(emp_code=h.emp_code,dt_lineno=d.dt_lineno,sa_transacno=d.sa_transacno).order_by('-pk')
                        if sales_multi:
                            sales_amt += amount / salestaff_cnt

                    
        mapped_object = {'id': instance.pk,'sa_custno': instance.sa_custno,'sa_custname': instance.sa_custname, 
        'sa_date': sa_date if sa_date else '','sa_totamt': str("{:.2f}".format(float(instance.sa_totamt))) if instance.sa_totamt else "0.00",
        'void_refno': void_refno if void_refno else "",'sa_staffname': instance.sa_staffname,'sa_status': instance.sa_status,
        'sa_transacno': instance.sa_transacno,'sa_transacno_ref': instance.sa_transacno_ref,'sa_transacno_type':instance.sa_transacno_type,
        'isvoid': instance.isvoid,'payment_remarks':payment_remarks,
        'total_amount': str("{:.2f}".format(float(instance.sa_transacamt))) if instance.sa_transacamt else "0.00",
        'paid_amount': str("{:.2f}".format(float(instance.sa_depositamt))) if instance.sa_depositamt else "0.00",
        'no_of_qty': instance.sa_totqty,'item':item,'no_of_lines': len(daud) if daud else 0,
        'new_date': "",'or':"NP15",'isvoid': instance.isvoid,'is_current':is_current,
        'sales_amt': sales_amt}
       
        return mapped_object


class PodhaudSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PosHaud
        fields = ['id'] 

    def to_representation(self, obj):
        sa_date = ""
        if obj.sa_date:
            splt = str(obj.sa_date).split(".")
            dtime = str(obj.sa_time).split(" ")
            time = dtime[1].split(":")

            time_data = time[0]+":"+time[1]
    
            sa_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")+" "+str(time_data)
        
        daud = PosDaud.objects.filter(sa_transacno=obj.sa_transacno).order_by('pk')
        daud_lines = []

        for i in daud:
            if i.record_detail_type in ['SERVICE','PRODUCT']:
                daud_lines.append({'id': i.pk,'record_detail_type': i.record_detail_type ,'item_code': i.dt_itemno,
                'item_desc': i.dt_itemdesc,'dt_price': "{:.2f}".format(float(i.dt_price)),
                'dt_discamt': "{:.2f}".format(float(i.dt_discamt)),'dt_promoprice' : "{:.2f}".format(float(i.dt_promoprice)), 
                'dt_qty': i.dt_qty,'dt_transacamt':"{:.2f}".format(float(i.dt_transacamt)),
                'dt_deposit': "{:.2f}".format(float(i.dt_deposit)),
                'staff_name': i.dt_staffname,'line_no': i.dt_lineno,'is_edit':True})
            else:
                daud_lines.append({'id': i.pk,'record_detail_type': i.record_detail_type ,'item_code': i.dt_itemno,
                'item_desc': i.dt_itemdesc,'dt_price': "{:.2f}".format(float(i.dt_price)),
                'dt_discamt': "{:.2f}".format(float(i.dt_discamt)),'dt_promoprice' : "{:.2f}".format(float(i.dt_promoprice)), 
                'dt_qty': i.dt_qty,'dt_transacamt':"{:.2f}".format(float(i.dt_transacamt)),
                'dt_deposit': "{:.2f}".format(float(i.dt_deposit)),
                'staff_name': i.dt_staffname,'line_no': i.dt_lineno,'is_edit':False})

            


        mapped_object = {'id': obj.pk,'transaction_no': obj.sa_transacno_ref,
        'date': sa_date if sa_date else '','customer_name': obj.sa_custname if obj.sa_custname else '',
        'total_amount': str("{:.2f}".format(float(obj.sa_transacamt))) if obj.sa_transacamt else "0.00",
        'paid_amount': str("{:.2f}".format(float(obj.sa_depositamt))) if obj.sa_depositamt else "0.00",
        'daud_lines': daud_lines}
       
        return mapped_object

        


class CreditNotePaySerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNote
        # fields = ['id','credit_code','sa_date','sa_transacno','amount','balance']
        fields = ['id']

    def to_representation(self, instance):
        if instance.sa_date:
            splt = str(instance.sa_date).split(" ")
            reversal_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

        mapped_object = {'id':instance.pk,'credit_code':instance.credit_code if instance.credit_code else '',
        'reversal_date':reversal_date if reversal_date else '','invoice':instance.sa_transacno if instance.sa_transacno else '',
        'credit': str("{:.2f}".format(float(instance.amount))) if instance.amount else "0.00",
        'balance': str("{:.2f}".format(float(instance.balance))) if instance.balance else "0.00"}
        return mapped_object


class PrepaidPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepaidAccount
        # fields = ['id','pp_desc','exp_date','pp_amt,'use_amt','remain']
        fields = ['id','pp_desc','exp_date',]

    def to_representation(self, instance):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        # print(instance.sa_date,"sa_date")
        if instance.exp_date:
            splt_ex = str(instance.exp_date).split(" ")
            exp_date = datetime.datetime.strptime(str(splt_ex[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        
        open_ids = PrepaidAccountCondition.objects.filter(pp_no=instance.pp_no,
        pos_daud_lineno=instance.line_no).only('pp_no','pos_daud_lineno').first()
        product = 0.00; service = 0.00; allval = 0.00
        if open_ids.conditiontype1 == "Product Only":
            product = "{:.2f}".format(float(instance.remain))
        elif open_ids.conditiontype1 == "Service Only":
            service = "{:.2f}".format(float(instance.remain))
        elif open_ids.conditiontype1 == "All":
            allval = "{:.2f}".format(float(instance.remain))

        pac_ids = PrepaidAccount.objects.filter(pp_no=instance.pp_no,line_no=instance.line_no,
        cust_code=instance.cust_code,site_code=site.itemsite_code).only('pp_no','line_no').order_by('pk').aggregate(Sum('use_amt'))
        accumulate = str("{:.2f}".format(float(pac_ids['use_amt__sum'])))  

        pay_rem1 = str(instance.pp_no)+""+"-"+" "+str(instance.line_no)+" "+"-"+""+str(instance.pp_desc)     

        mapped_object = {'id':instance.pk,'pp_desc':instance.pp_desc if instance.pp_desc else '',
        'exp_date': exp_date if exp_date else '','amount': str("{:.2f}".format(float(instance.pp_total))) if instance.pp_total else "0.00",
        'accumulate': accumulate if accumulate else "0.00",
        'current_use': "0.00",'remain' : str("{:.2f}".format(float(instance.remain))) if instance.remain else "0.00",
        'type': "PREPAID",'remark1': instance.ref1 if instance.ref1 else '','remark2': instance.ref2 if instance.ref2 else '',
        'supplementary':'','product': product if product else "0.00",
        'service': service if service else "0.00",'all': allval if allval else "0.00",
        'item_code': '','pay_rem1':pay_rem1 if pay_rem1 else ''}

        return mapped_object


class CartPrepaidSerializer(serializers.ModelSerializer): 

    class Meta:
        model = ItemCart
        fields = ['id','itemcode']

    def to_representation(self, instance):
        if instance.itemcodeid:
            ctype = False
            if instance.itemcodeid.item_div == '3':
                ctype = "Service"
            elif instance.itemcodeid.item_div == '1':
                ctype = "Product" 

        if instance.itemcodeid:
            description = instance.itemcodeid.item_name if instance.itemcodeid.item_name else ''

        mapped_object = {'id': instance.pk ,'no':instance.lineno if instance.lineno else '',
        'itemcode': instance.itemcode,'type': ctype if ctype else '',
        'description':description if description else '','transac_amount': str("{:.2f}".format(float(instance.deposit))) if instance.deposit else "0.00",
        'use':"0.00",'outstanding':str("{:.2f}".format(float(instance.deposit))) if instance.deposit else "0.00"}
        return mapped_object



class HolditemdetailSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Holditemdetail
        fields = ['id','sa_date','hi_itemdesc','itemno','holditemqty']

class HolditemSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Holditemdetail
        fields = ['id','hi_itemdesc','holditemqty']

class HolditemupdateSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
    issued_qty = serializers.SerializerMethodField()
    emp_id = serializers.SerializerMethodField()


    class Meta:
        model = Holditemdetail
        fields = ['id','issued_qty','emp_id']


class TreatmentHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    is_current = serializers.SerializerMethodField() 

    def get_is_current(self, obj):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True).order_by('-pk')
        site = fmspw[0].loginsite

        iscurrent = ""
        if obj.site_code == site.itemsite_code:
            iscurrent = True
        elif obj.site_code != site.itemsite_code:
            iscurrent = False
 
        return iscurrent  

    class Meta:
        model = Treatment
        fields = ['id','treatment_code','course','status','record_status','remarks','type',
        'is_current','site_code']

class StockUsageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id','treatment_code','course']

class StockUsageProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','item_desc','item_code','rpt_code','Stock_PIC']


class TreatmentUsageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    link_code = serializers.SerializerMethodField()
    stock_id = serializers.SerializerMethodField()


    def get_link_code(self, obj):
        return None 

    def get_stock_id(self, obj):
        return None    


    class Meta:
        model = TreatmentUsage
        fields = ['id','item_code','link_code','item_desc','qty','uom','stock_id']


class StockUsageMemoSerializer(serializers.ModelSerializer):
    stock_id = serializers.SerializerMethodField()
    emp_id = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()


    def get_stock_id(self, obj):
        return None   

    def get_emp_id(self, obj):
        return None 

    def get_quantity(self, obj):
        return None 

    def get_date(self, obj):
        return None          
     
    class Meta:
        model = UsageMemo
        fields = ['id','item_name','date_out','memo_no','staff_name','uom','qty','memo_remarks','stock_id','emp_id',
        'quantity','date']


class TreatmentfaceSerializer(serializers.ModelSerializer):

    room_id = serializers.SerializerMethodField()
    treat_remarks = serializers.SerializerMethodField()


    def get_room_id(self, obj):
        return None 

    def get_treat_remarks(self, obj):
        return None          
         
    class Meta:
        model = Treatmentface
        fields = ['id','treatment_code','str1','str2','str3','str4','str5','room_id','treat_remarks']


class SiteApptSettingSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemSitelist
        fields = ['id','startday_hour','endday_hour','cell_duration','resource_count']        

class HolditemAccListSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Holditemdetail
        fields = ['id']

    def to_representation(self, obj):
        splt = str(obj.sa_date).split(" ")
        sa_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

        esplit = str(obj.sa_time).split(" ")
        Time = str(esplit[1]).split(":")
        time = Time[0]+":"+Time[1]

        issued_qty = obj.hi_qty - obj.holditemqty
        balance = obj.holditemqty - issued_qty

        mapped_object = {'id':obj.pk,'sa_date':sa_date,'sa_time':time,
        'product_issues_no':obj.product_issues_no,'hi_itemdesc':obj.hi_itemdesc,
        'holditemqty':obj.holditemqty,'issued_qty':issued_qty,'balance':balance,
        'hi_uom':obj.hi_uom,'hi_staffname':obj.hi_staffname,'itemsite_code':obj.itemsite_code,
        'status':obj.status}
        return mapped_object    


class CustomerAccountSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(source='pk',required=False)
   
    class Meta:
        model = Customer
        fields = ['id','cust_code','cust_name']

class TreatmentUsageListSerializer(serializers.ModelSerializer):

    class Meta:
        model = TreatmentUsage
        fields = ['id','treatment_code','item_desc','qty','uom','item_code','sa_transacno','site_code']

    def to_representation(self, instance):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True).order_by('-pk')
        site = fmspw[0].loginsite

        data = super(TreatmentUsageListSerializer, self).to_representation(instance)
        treat_obj = Treatment.objects.filter(treatment_code=data['treatment_code']).order_by('-pk').first()
        data['service_stock'] = treat_obj.course if treat_obj and treat_obj.course else ""
    
        link_obj = ItemLink.objects.filter(item_code=data['item_code'],link_type='L',itm_isactive=True).order_by('-pk').first()
        data['link_code'] = link_obj.link_code if link_obj and link_obj.link_code else ""


        data['iscurrent'] = ""
        if instance.site_code == site.itemsite_code:
            data['iscurrent'] = True
        elif instance.site_code != site.itemsite_code:
            data['iscurrent'] = False
 
        return data    

class TreatmentUsageStockSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','item_desc','item_name','item_code']


class ProductPurchaseSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = PosDaud
        fields = ['id','sa_date','dt_qty','dt_staffname','dt_promoprice','dt_transacamt','item_remarks','dt_itemdesc']

    
    def to_representation(self, instance):
       
        data = super(ProductPurchaseSerializer, self).to_representation(instance)
        splt = str(data['sa_date']).split("T")
        data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
        haud_ids = PosHaud.objects.filter(sa_transacno=instance.sa_transacno).first()
        data['transaction'] = haud_ids.sa_transacno_ref if haud_ids and haud_ids.sa_transacno_ref else ""           
        data['dt_promoprice'] = "{:.2f}".format(float(data['dt_promoprice']))
        data['dt_transacamt'] = "{:.2f}".format(float(data['dt_transacamt']))

        stktrn_ids = Stktrn.objects.filter(itemcode=instance.dt_itemno,
        store_no=instance.itemsite_code,trn_type="GRN").order_by('-trn_date').first()
        data['replenish_date'] = ""
        if stktrn_ids:
            if stktrn_ids.trn_date:
                rep_date = datetime.datetime.strptime(str(stktrn_ids.trn_date), "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%y")
                data['replenish_date'] = rep_date
           
        return data   

class TreatmentPackageDoneListSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = TreatmentPackage
        fields = ['id']
