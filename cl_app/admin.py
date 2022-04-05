from django.contrib import admin
from .models import (ReverseTrmtReason,VoidReason,TreatmentUsage,UsageMemo,Treatmentface,
Usagelevel)

# Register your models here.
admin.site.register(ReverseTrmtReason)
admin.site.register(VoidReason)
admin.site.register(TreatmentUsage)
admin.site.register(UsageMemo)
admin.site.register(Treatmentface)
admin.site.register(Usagelevel)

