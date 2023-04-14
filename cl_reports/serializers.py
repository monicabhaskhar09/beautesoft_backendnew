from rest_framework import serializers
from .models import (Reportmaster)
from cl_table.models import (Customer, PosDaud,PosHaud)
import datetime
from Cl_beautesoft.settings import SITE_ROOT

class ReportmasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Reportmaster
        fields = '__all__'

    def to_representation(self, obj):
        data = super(ReportmasterSerializer, self).to_representation(obj)

        image = ""
        if obj.image:
            image = str(SITE_ROOT)+str(obj.image)
         
        data['image'] = image

        return data        