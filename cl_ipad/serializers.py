from rest_framework import serializers
from .models import (WebConsultation_Hdr,WebConsultation_Question,
WebConsultation_AnalysisResult,WebConsultation_Referral,WebConsultation_Referral_Hdr)


class WebConsultationHdrSerializer(serializers.ModelSerializer):
    
    doc_date = serializers.DateTimeField(format="%d-%m-%Y",required=False)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y",required=False)

    class Meta:
        model = WebConsultation_Hdr
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