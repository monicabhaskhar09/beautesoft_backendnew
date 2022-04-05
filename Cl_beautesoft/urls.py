from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from cl_table import views


router = DefaultRouter()
router.register(r'customer', views.CustomerViewset, basename='customer')
router.register(r'services', views.ServicesViewset, basename='services')
router.register(r'branch', views.ItemSiteListViewset, basename='branch')
router.register(r'staffs', views.EmployeeViewset, basename='staffs')
router.register(r'shift', views.ShiftViewset)
router.register(r'shiftdatewise', views.ShiftDateWiseViewset)
router.register(r'FMSPW', views.FMSPWViewset, basename='FMSPW')
router.register(r'appointment', views.AppointmentViewset, basename='appointment')
router.register(r'itemdept', views.ItemDeptViewset, basename='itemdept')
router.register(r'stocklist', views.StockListViewset, basename='stocklist')
router.register(r'treatment', views.TreatmentMasterViewset, basename='treatment')
router.register(r'treatmentdetails', views.TreatmentdetailsViewset, basename='treatmentdetails')
router.register(r'postaud', views.postaudViewset, basename='postaud')
router.register(r'paytable', views.PaytableViewset, basename='paytable')
router.register(r'paygroup', views.PayGroupViewset, basename='paygroup')
router.register(r'paytablenew', views.PaytableNewViewset, basename='paytablenew')
router.register(r'itemstatus', views.ItemStatusViewset, basename='itemstatus')
router.register(r'appointmentpopup', views.AppointmentPopup, basename='appointmentpopup')
router.register(r'appointmentcalender', views.AppointmentCalender, basename='appointmentcalender')
router.register(r'tmpitemhelper', views.TmpItemHelperViewset, basename='tmpitemhelper')
# router.register(r'empappointmentview', views.EmployeeAppointmentView, basename='empappointmentview')
router.register(r'empappointmentview', views.EmployeeAppointmentViewNew, basename='empappointmentview')
router.register(r'appointmentresources', views.AppointmentResourcesViewset, basename='appointmentresources')
router.register(r'appointmentblock', views.AppointmentBlockViewset, basename='appointmentblock')
router.register(r'appointmentrecur', views.AppointmentRecurViewset, basename='appointmentrecur')
router.register(r'title', views.TitleViewset, basename='title')
router.register(r'appointmentedit', views.AppointmentEditViewset, basename='appointmentedit')

router.register(r'staffPlus', views.StaffPlusViewSet, basename='staffPlus')
router.register(r'CustomerPlus', views.CustomerPlusViewset, basename='CustomerPlus')
router.register(r'RewardPolicy', views.RewardPolicyViewSet, basename='RewardPolicy')
router.register(r'RedeemPolicy', views.RedeemPolicyViewSet, basename='RedeemPolicy')
router.register(r'smsreply', views.SMSReplyViewset, basename='smsreply')
router.register(r'itemdescapiviewset', views.ItemDescAPIViewset, basename='itemdesc')
router.register(r'customerpoints', views.CustomerPointsViewsets, basename='customerpoints')
router.register(r'tempcustsigninvoice', views.TempcustsignInvoiceViewset, basename='tempcustsigninvoice')
router.register(r'customerdocument', views.CustomerDocumentViewset, basename='customerdocument')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('', include('cl_table.urls')),
    path('', include('custom.urls')),
    path('', include('cl_app.urls')),
    path('', include('clpayroll.urls')),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

