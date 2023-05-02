from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'reportmaster', views.ReportmasterViewset, basename='reportmaster')
router.register(r'collectionbyoutlet', views.CollectionbyOutletViewset, basename='collectionbyoutlet')



urlpatterns = [
    path('api/', include(router.urls)),
    path('api/listpaytable/', views.PaymentPaytableListAPIView.as_view(), name='listpaytable'),
    path('api/sitelisting/', views.siteListingAPIView.as_view(), name='sitelisting'),
    path('api/report-title/', views.ReportTitleListAPIView.as_view(), name='report-title'),



   

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)