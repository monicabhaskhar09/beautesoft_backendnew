from rest_framework import serializers
from .models import (WebConsultation_Hdr,WebConsultation_Question)


class WebConsultationHdrSerializer(serializers.ModelSerializer):
    
    doc_date = serializers.DateTimeField(format="%d-%m-%Y")
    updated_at = serializers.DateTimeField(format="%d-%m-%Y")

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