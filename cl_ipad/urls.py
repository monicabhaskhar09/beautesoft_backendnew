from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'webconsultationhdr', views.WebConsultationHdrViewset, basename='webconsultationhdr')
router.register(r'webconsultationquestion', views.WebConsultationQuestionViewset, basename='webconsultationquestion')


urlpatterns = [
    path('api/', include(router.urls)),
    # path('api/login', views.UserLoginAPIView.as_view(), name='login'),
   

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)