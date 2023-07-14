from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from . import views



# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'employeesalary', views.EmployeeSalaryViewset)


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('be/api/', include(router.urls)),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 