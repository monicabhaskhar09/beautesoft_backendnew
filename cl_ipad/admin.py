from django.contrib import admin

# Register your models here.
from .models import (WebConsultation_Hdr,WebConsultation_Question,
WebConsultation_AnalysisResult,WebConsultation_Referral,WebConsultation_Referral_Hdr)


admin.site.register(WebConsultation_Hdr)
admin.site.register(WebConsultation_Question)
admin.site.register(WebConsultation_AnalysisResult)
admin.site.register(WebConsultation_Referral)
admin.site.register(WebConsultation_Referral_Hdr)
