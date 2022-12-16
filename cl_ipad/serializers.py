from rest_framework import serializers
from .models import (WebConsultation_Hdr,WebConsultation_Dtl,WebConsultation_Question,
WebConsultation_AnalysisResult,WebConsultation_Referral,WebConsultation_Referral_Hdr,TNC_Master)
from cl_table.models import (Customer, PosDaud,PosHaud)

class WebConsultationHdrSerializer(serializers.ModelSerializer):
    
    doc_date = serializers.DateTimeField(format="%d-%m-%Y",required=False)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S",required=False)
    consultant_name = serializers.CharField(source='emp_codeid.display_name',required=False)

    class Meta:
        model = WebConsultation_Hdr
        fields = '__all__'

class WebConsultationDtlSerializer(serializers.ModelSerializer):
    
   
    class Meta:
        model = WebConsultation_Dtl
        fields = '__all__'


class WebConsultationQuestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WebConsultation_Question
        fields = '__all__'

    def to_representation(self, obj):
        data = super(WebConsultationQuestionSerializer, self).to_representation(obj)
       

        data['item_site_desc'] = ""  
        data['item_site_ids'] = ""
        if obj.site_ids.filter().exists():
            site_ids = obj.site_ids.filter()
 
            data['item_site_ids'] =  [{'label': i.itemsite_code ,'value': i.pk} for i in site_ids if i.itemsite_code]
            data['item_site_desc'] = ','.join([v.itemsite_code for v in site_ids if v.itemsite_code])
        
      

        return data               


class WebConsultation_AnalysisResultSerializer(serializers.ModelSerializer):
    
    create_date = serializers.DateTimeField(format="%d-%m-%Y",required=False)
    last_updatedate = serializers.DateTimeField(format="%d-%m-%Y",required=False)

    class Meta:
        model = WebConsultation_AnalysisResult
        fields = '__all__'        

class WebConsultation_ReferralSerializer(serializers.ModelSerializer):
    
    create_date = serializers.DateTimeField(format="%d-%m-%Y",required=False)
    last_updatedate = serializers.DateTimeField(format="%d-%m-%Y",required=False)

    class Meta:
        model = WebConsultation_Referral
        fields = '__all__'                

class WebConsultation_Referral_HdrSerializer(serializers.ModelSerializer):
    
    create_date = serializers.DateTimeField(format="%d-%m-%Y",required=False)
    last_updatedate = serializers.DateTimeField(format="%d-%m-%Y",required=False)

    class Meta:
        model = WebConsultation_Referral_Hdr
        fields = '__all__'                        

class TransactionCustomerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    cust_joindate = serializers.DateTimeField(format="%d-%m-%Y",required=False)
    
    class Meta:
        model = Customer
        fields = ['id','cust_code','cust_name','cust_nric','cust_joindate'] 

class TransactionPosDaudSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    sa_date = serializers.DateTimeField(format="%d-%m-%Y",required=False)
    
    class Meta:
        model = PosDaud
        fields = ['id','sa_date','dt_itemdesc','dt_transacamt','dt_qty'] 
    
    def to_representation(self, instance):
       
        data = super(TransactionPosDaudSerializer, self).to_representation(instance)
        haud_ids = PosHaud.objects.filter(sa_transacno=instance.sa_transacno).first()
        data['sa_transacno_ref'] = haud_ids.sa_transacno_ref if haud_ids and haud_ids.sa_transacno_ref else ""
        data['dt_transacamt'] = "{:.2f}".format(float(instance.dt_transacamt))
        return data 

class TNCMasterSerializer(serializers.ModelSerializer):
    
 
    class Meta:
        model = TNC_Master
        fields = '__all__'
