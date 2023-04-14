from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'reportmaster', views.ReportmasterViewset, basename='reportmaster')

urlpatterns = [
    path('api/', include(router.urls)),
    # path('api/clientdetails/', views.ClientDetailsListAPIView.as_view(), name='clientdetails'),

   

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)