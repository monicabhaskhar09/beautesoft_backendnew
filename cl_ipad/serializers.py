from rest_framework import serializers
from .models import (WebConsultation_Hdr,WebConsultation_Dtl,WebConsultation_Question,
WebConsultation_AnalysisResult,WebConsultation_Referral,WebConsultation_Referral_Hdr,TNC_Master,
WebConsultation_QuestionMultichoice,TNC_Detail,TNC_Header,WebConsultation_Questionsub_questions)
from cl_table.models import (Customer, PosDaud,PosHaud)
import datetime
from Cl_beautesoft.settings import SITE_ROOT

class WebConsultationHdrSerializer(serializers.ModelSerializer):
    
    doc_date = serializers.DateTimeField(format="%d-%m-%Y",required=False)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S",required=False)
    consultant_name = serializers.CharField(source='emp_codeid.display_name',required=False)

    class Meta:
        model = WebConsultation_Hdr
        fields = '__all__'

    def to_representation(self, obj):
        data = super(WebConsultationHdrSerializer, self).to_representation(obj)

        signature = ""
        if obj.signature:
            signature = str(SITE_ROOT)+str(obj.signature)
         
        data['signature'] = signature

        return data     

class WebConsultationDtlSerializer(serializers.ModelSerializer):
    
   
    class Meta:
        model = WebConsultation_Dtl
        fields = '__all__'

    def to_representation(self, obj):
        data = super(WebConsultationDtlSerializer, self).to_representation(obj)

        image = ""
        if obj.image:
            image = str(SITE_ROOT)+str(obj.image)
         
        data['image'] = image

        return data      


class WebConsultationQuestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WebConsultation_Question
        fields = ['id','question_group','question_number','page_number','isactive',
        'question_type','image','question_english','question_chinese','question_others',
        'site_ids','question_text','option_type','mandatory']

    def to_representation(self, obj):
        data = super(WebConsultationQuestionSerializer, self).to_representation(obj)
       

        data['item_site_desc'] = ""  
        data['item_site_ids'] = ""
        if obj.site_ids.filter().exists():
            site_ids = obj.site_ids.filter()
 
            data['item_site_ids'] =  [{'label': i.itemsite_code ,'value': i.pk} for i in site_ids if i.itemsite_code]
            data['item_site_desc'] = ','.join([v.itemsite_code for v in site_ids if v.itemsite_code])
        
        cho_ids = WebConsultation_QuestionMultichoice.objects.filter(questionid__pk=obj.pk).values('id','questionid','choice')
        data['multichoices'] = cho_ids

        qcho_ids = WebConsultation_Questionsub_questions.objects.filter(questionid__pk=obj.pk).values('id','questionid',
        'options','sub_question_english','sub_question_chinese')
        data['sub_questions'] = qcho_ids

        image = ""
        if obj.image:
            image = str(SITE_ROOT)+str(obj.image)
         
        data['image'] = image

        return data               

class WebConsultationQuestionMultichoiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WebConsultation_QuestionMultichoice
        fields = '__all__'

class WebConsultationQuestionsub_questionsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WebConsultation_Questionsub_questions
        fields = '__all__'        

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

    def to_representation(self, obj):
        data = super(WebConsultation_Referral_HdrSerializer, self).to_representation(obj)

        signature_img = ""
        if obj.signature_img:
            signature_img = str(SITE_ROOT)+str(obj.signature_img)
         
        data['signature_img'] = signature_img

        welcomedoor_signatureimg = ""
        if obj.welcomedoor_signatureimg:
            welcomedoor_signatureimg = str(SITE_ROOT)+str(obj.welcomedoor_signatureimg)
         
        data['welcomedoor_signatureimg'] = welcomedoor_signatureimg 

        return data      
                

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
        fields = ['id','sa_date','dt_itemdesc','dt_transacamt',
        'dt_qty','dt_staffno','dt_staffname','sa_transacno'] 
    
    def to_representation(self, instance):
       
        data = super(TransactionPosDaudSerializer, self).to_representation(instance)
        haud_ids = PosHaud.objects.filter(sa_transacno=instance.sa_transacno).first()
        data['sa_transacno_ref'] = haud_ids.sa_transacno_ref if haud_ids and haud_ids.sa_transacno_ref else ""
        data['dt_transacamt'] = "{:.2f}".format(float(instance.dt_transacamt))
        return data 

class TNCMasterSerializer(serializers.ModelSerializer):
    
 
    class Meta:
        model = TNC_Master
        fields = ['id','sno','isactive','english','otherlanguage','tnctext1','tnctext2','is_declaration'] 

class TNC_DetailSerializer(serializers.ModelSerializer):
    
 
    class Meta:
        model = TNC_Detail
        fields = ['id','receiptno','package'] 


class TNC_HeaderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    
    class Meta:
        model = TNC_Header
        fields = ['id','tncno'] 

    def to_representation(self, instance):
       
        data = super(TNC_HeaderSerializer, self).to_representation(instance)
        
        data['tncno'] = instance.tncno if instance and instance.tncno else ""
        sign_date = ""
        if instance and instance.sign_date:
            splt = str(instance.sign_date).split(" ") 
            sign_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")

        data['sign_date'] = sign_date
        d_ids = TNC_Detail.objects.filter(tncno=instance.tncno)
        serializer = TNC_DetailSerializer(d_ids, many=True) 
        data['tnc_detail'] =  serializer.data

        return data 

class TNC_DetailformSerializer(serializers.ModelSerializer):
    receipt_date = serializers.DateTimeField(format="%d-%m-%Y",required=False)

    
 
    class Meta:
        model = TNC_Detail
        fields = ['id','receipt_date','receiptno','package'] 

    def to_representation(self, instance):
       
        data = super(TNC_DetailformSerializer, self).to_representation(instance)
        
       
        data['amount'] =  "{:.2f}".format(float(instance.amount)) if instance.amount else "0.00"
        haud_ids = PosHaud.objects.filter(sa_transacno_ref=instance.receiptno).first()
        data['invoice_no'] = haud_ids.sa_transacno if haud_ids and haud_ids.sa_transacno else ""

        return data 


class WebConsultationQuestionprintSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WebConsultation_Question
        fields = ['id','question_group','question_number','page_number','isactive',
        'question_type','image','question_english','question_chinese','question_others',
        'site_ids','question_text','option_type','mandatory']

    def to_representation(self, obj):
        data = super(WebConsultationQuestionprintSerializer, self).to_representation(obj)

        data['item_site_desc'] = ""  
        data['item_site_ids'] = ""
        if obj.site_ids.filter().exists():
            site_ids = obj.site_ids.filter()
 
            data['item_site_ids'] =  [{'label': i.itemsite_code ,'value': i.pk} for i in site_ids if i.itemsite_code]
            data['item_site_desc'] = ','.join([v.itemsite_code for v in site_ids if v.itemsite_code])
        
       
        cho_ids = WebConsultation_QuestionMultichoice.objects.filter(questionid__pk=obj.pk).values('id','questionid','choice')
        data['multichoices'] = cho_ids

        qcho_ids = WebConsultation_Questionsub_questions.objects.filter(questionid__pk=obj.pk).values('id','questionid',
        'options','sub_question_english','sub_question_chinese')
        data['sub_questions'] = qcho_ids


        return data           


class WebConsultation_AnalysisResultprintSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = WebConsultation_AnalysisResult
        fields = '__all__' 

class WebConsultation_ReferralprintSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = WebConsultation_Referral
        fields = ['id','referral_name','referral_age','referral_contactno']         


class WebConsultation_Referral_HdrprintSerializer(serializers.ModelSerializer):
    
   
    class Meta:
        model = WebConsultation_Referral_Hdr
        fields = ['id','signature_img','welcomedoor_signatureimg']    

    def to_representation(self, obj):
        data = super(WebConsultation_Referral_HdrprintSerializer, self).to_representation(obj)
        signature_img = ""
        if obj and obj.signature_img:
            signature_img = str(SITE_ROOT)+str(obj.signature_img)

        data['signature_img'] = signature_img

        welcomedoor_signatureimg = ""
        if obj and obj.welcomedoor_signatureimg:
            welcomedoor_signatureimg = str(SITE_ROOT)+str(obj.welcomedoor_signatureimg)

        data['welcomedoor_signatureimg'] = welcomedoor_signatureimg


        return data           
                              
