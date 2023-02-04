from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'webconsultationhdr', views.WebConsultationHdrViewset, basename='webconsultationhdr')
router.register(r'webconsultationdtl', views.WebConsultationDtlViewset, basename='webconsultationdtl')
router.register(r'webconsultationquestion', views.WebConsultationQuestionViewset, basename='webconsultationquestion')
router.register(r'webconsultationanalysisresult', views.WebConsultation_AnalysisResultViewset, basename='webconsultationanalysisresult')
router.register(r'webconsultationreferral', views.WebConsultation_ReferralViewset, basename='webconsultationreferral')
router.register(r'webconsultationreferralhdr', views.WebConsultation_Referral_HdrViewset, basename='webconsultationreferralhdr')
router.register(r'transactioncustomer', views.TransactionCustomerViewset, basename='transactioncustomer')
router.register(r'tncmaster', views.TNC_MasterViewset, basename='tncmaster')
router.register(r'webquestionmultichoice', views.WebConsultationQuestionMultichoiceViewset, basename='webquestionmultichoice')
router.register(r'webquestionsubquestions', views.WebConsultation_Questionsub_questionsViewset, basename='webquestionsubquestions')


urlpatterns = [
    path('api/', include(router.urls)),
    # path('api/login', views.UserLoginAPIView.as_view(), name='login'),
   

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)