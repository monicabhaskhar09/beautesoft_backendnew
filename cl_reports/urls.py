from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'reportmaster', views.ReportmasterViewset, basename='reportmaster')



urlpatterns = [
    path('be/api/', include(router.urls)),
    path('be/api/listpaytable/', views.PaymentPaytableListAPIView.as_view(), name='listpaytable'),
    path('be/api/sitelisting/', views.siteListingAPIView.as_view(), name='sitelisting'),
    # path('be/api/report-title/', views.ReportTitleAPIView.as_view(), name='report-title'),
    path('be/api/collectionbyoutlet/', views.CollectionbyOutletReportAPIView.as_view(), name='collectionbyoutlet'),
    path('be/api/treatmentdonereport/', views.TreatmentDoneReportAPIView.as_view(), name='treatmentdonereport'),




   

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)