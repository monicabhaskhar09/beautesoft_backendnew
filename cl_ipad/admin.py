from django.contrib import admin

# Register your models here.
from .models import (WebConsultation_Hdr,WebConsultation_Question)
admin.site.register(WebConsultation_Hdr)
admin.site.register(WebConsultation_Question)
