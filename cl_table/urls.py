from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views


router = DefaultRouter()
router.register(r'termsandcondition', views.TermsandconditionViewset, basename='termsandcondition')
router.register(r'participants', views.ParticipantsViewset, basename='participants')
router.register(r'dayendconfirmlog', views.DayendconfirmlogViewset, basename='dayendconfirmlog')
router.register(r'customerpointsaccount', views.CustomerPointsAccountViewset, basename='customerpointsaccount')
router.register(r'mgmpolicycloud', views.MGMPolicyCloudViewset, basename='mgmpolicycloud')
router.register(r'customerreferral', views.CustomerReferralViewset, basename='customerreferral')
router.register(r'sitelistip', views.SitelistipViewset, basename='sitelistip')
router.register(r'displaycatalog', views.DisplayCatalogViewset, basename='displaycatalog')
router.register(r'displayItems', views.DisplayItemViewset, basename='displayItems')
router.register(r'outletrequestcustomer', views.OutletRequestCustomerViewset, basename='outletrequestcustomer')
router.register(r'manualrewardpoint', views.ManualRewardPointCustomerViewset, basename='manualrewardpoint')
router.register(r'onlinebooking', views.OnlineBookingDateSlotsViewset, basename='onlinebooking')
router.register(r'invoicetemplateconfig', views.InvoiceTemplateConfigViewset, basename='invoicetemplateconfig')
router.register(r'appointbooking', views.AppointBookingDateSlotsViewset, basename='appointbooking')
router.register(r'ecomappointbooking', views.EcomAppointBookingViewset, basename='ecomappointbooking')


urlpatterns = [
    path('be/api/', include(router.urls)),
    path('be/api/login', views.UserLoginAPIView.as_view(), name='login'),
    path('be/api/logout', views.UserLogoutAPIView.as_view(), name='logout'),
    path('be/api/employeebranchwise', views.EmployeeList.as_view(), name='employee-branch'),
    path('be/api/skills', views.ServicesListAPIView.as_view(), name='skills'),
    path('be/api/shiftlist', views.ShiftListAPIView.as_view(), name='shiftlist'),
    path('be/api/customers/all/', views.CustomerListAPIView.as_view(), name='customer_all'),
    path('be/api/bookingstatus/', views.AppointmentBookingStatusList.as_view(), name='bookingstatus'),
    path('be/api/branchlist/', views.ItemSiteListAPIView.as_view(), name='branchlist'),
    path('be/api/branchlogin/', views.ItemSiteListAPIViewLogin.as_view(), name='branchlogin'),
    path('be/api/treatmentstock/<int:pk>/', views.StockDetail.as_view(), name='treatmentstock'),
    path('be/api/staffsavailable/', views.StaffsAvailable.as_view(), name='staffsavailable'),
    path('be/api/userlist/', views.UsersList.as_view(), name='userlist'),
    path('be/api/paytable/', views.PaytableListAPIView.as_view(), name='paytable'),
    path('be/api/customerreceiptprint/', views.CustomerReceiptPrintList.as_view(), name='customerreceiptprint'),
    path('be/api/source/', views.SourceAPI.as_view(), name='source'),
    path('be/api/state/', views.StateAPI.as_view(), name='state'),
    path('be/api/country/', views.CountryAPI.as_view(), name='country'),
    path('be/api/language/', views.LanguageAPI.as_view(), name='language'),
    path('be/api/securities/', views.SecuritiesAPIView.as_view(), name='securities'),
    path('be/api/schedulehour/', views.ScheduleHourAPIView.as_view(), name='schedulehour'),
    path('be/api/custappt/', views.CustApptAPI.as_view(), name='custappt'),
    path('be/api/appttype/', views.ApptTypeAPIView.as_view(), name='appttype'),
    path('be/api/focreason/', views.FocReasonAPIView.as_view(), name='focreason'),
    # path('be/api/updatetable/', views.UpdateTablesAPIView.as_view(), name='updatetable'),
    path('be/api/treatmentpackages/', views.TreatmentApptAPI.as_view(), name='treatmentpackages'),
    path('be/api/appointmentsort/', views.AppointmentSortAPIView.as_view(), name='appointmentsort'),
    path('be/api/appttreatmentdonehistory/', views.ApptTreatmentDoneHistoryAPI.as_view(), name='appttreatmentdonehistory'),
    path('be/api/upcomingappointment/', views.UpcomingAppointmentAPIView.as_view(), name='upcomingappointment'),
    path('be/api/blockreason/', views.BlockReasonAPIView.as_view(), name='blockreason'),
    path('be/api/appointmentlistpdf/', views.AppointmentListPdf.as_view(), name='appointmentlistpdf'),
    path('be/api/dayendlist/', views.DayEndListAPIView.as_view(), name='dayendlist'),
    path('be/api/appointmentlog/', views.AppointmentLogAPIView.as_view(), name='appointmentlog'),
    path('be/api/custapptupcoming/', views.CustApptUpcomingAPIView.as_view(), name='custapptupcoming'),
    path('be/api/attendancestaff/', views.AttendanceStaffsAPIView.as_view(), name='attendancestaff'),
    path('be/api/meta/race/', views.meta_race, name='meta_race'),
    path('be/api/meta/nationality/', views.meta_nationality, name='meta_nationality'),
    path('be/api/meta/religion/', views.meta_religious, name='meta_religious'),
    path('be/api/meta/country/', views.meta_country, name='meta_country'),
    path('be/api/RewardItemList/', views.RewardItemList, name='RewardItemList'),
    path('be/api/CustomerClassList/', views.CustomerClassList, name='CustomerClassList'),
    path('be/api/WorkScheduleMonth/', views.MonthlyWorkSchedule.as_view(), name='WorkScheduleMonth'),
    path('be/api/MonthlyAllSchedule/', views.MonthlyAllSchedule.as_view(), name='MonthlyAllSchedule'),
    path('be/api/WorkScheduleHours/', views.schedule_hours, name='WorkScheduleHours'),
    path('be/api/SkillsItemTypeList/', views.SkillsItemTypeList, name='SkillsItemTypeList'),
    path('be/api/SkillsView/', views.SkillsView.as_view(), name='SkillsView'),
    path('be/api/PhotoDiagnosis/', views.PhotoDiagnosis.as_view(), name='PhotoDiagnosis'),
    path('be/api/PhotoDiagnosis/<int:id>/', views.PhotoDiagnosisDetail.as_view(), name='PhotoDiagnosisDetail'),
    path('be/api/DiagnosisCompare/', views.DiagnosisCompareView.as_view(), name='DiagnosisCompare'),
    path('be/api/DiagnosisCompare/<int:id>/', views.DiagnosisCompareViewDetail.as_view(), name='DiagnosisCompareViewDetail'),

    path('be/api/EmployeeSkills/', views.EmployeeSkillView.as_view(), name='EmployeeSkillView'),
    path('be/api/CustomerFormSettings/', views.CustomerFormSettingsView.as_view(), name='CustomerFormSettingsView'),
    path('be/api/CustomerFormSettings/details', views.CustomerFormSettings, name='CustomerFormSettingsDetails'),
    # path('be/api/RewardPolicy/', views.RewardPolicyView.as_view(), name='RewardPolicyView'),
    # path('be/api/RedeemPolicy/', views.RedeemPolicyView.as_view(), name='RedeemPolicyView'),
    path('be/api/EmployeeSecuritySettings/', views.EmployeeSecuritySettings.as_view(), name='EmployeeSecuritySettings'),
    path('be/api/IndividualEmpSettings/<int:emp_no>', views.IndividualEmpSettings.as_view(), name='IndividualEmpSettings'),
    path('be/api/EmployeeLevelsSettings/', views.EmployeeLevelsSettings, name='EmployeeLevelsSettings'),
    path('be/api/MultiLanguage/', views.MultiLanguage.as_view(), name='MultiLanguage'),
    path('be/api/MultiLanguageList/', views.MultiLanguage_list, name='MultiLanguage_list'),
    path('be/api/EmployeeLevels/', views.EmployeeLevels, name='EmployeeLevels'),
    path('be/api/DailySales/', views.DailySalesView.as_view(), name='DailySales'),
    path('be/api/DailySalesSummery/', views.DailySalesSummeryView.as_view(), name='DailySalesSummeryView'),
    path('be/api/MonthlySalesSummery/', views.MonthlySalesSummeryView.as_view(), name='MonthlySalesSummeryView'),
    path('be/api/DailySalesBySite/', views.DailySalesSummeryBySiteView.as_view(), name='DailySalesSummeryBySiteView'),
    path('be/api/MonthlySalesBySite/', views.MonthlySalesSummeryBySiteView.as_view(), name='MonthlySalesSummeryBySiteView'),
    path('be/api/DailySalesByConsultant/', views.DailySalesSummeryByConsultantView.as_view(), name='DailySalesSummeryByConsultantView'),
    path('be/api/ServicesByOutlet/', views.ServicesByOutletView.as_view(), name='ServicesByOutletView'),
    path('be/api/ProductByOutlet/', views.ProductByOutletView.as_view(), name='ProductByOutletView'),
    path('be/api/RankingByOutlet/', views.RankingByOutletView.as_view(), name='RankingByOutletView'),
    path('be/api/ServicesByConsultant/', views.ServicesByConsultantView.as_view(), name='ServicesByConsultantView'),
    path('be/api/SalesByConsultant/', views.SalesByConsultantView.as_view(), name='SalesByConsultantView'),
    path('be/api/site_group_list/', views.site_group_list, name='site_group_list'),
    path('be/api/customeroutstanding/', views.CustomerOutstandingAPIView.as_view(), name='customeroutstanding'),
    path('be/api/currentuser/', views.CurrentUserAPIView.as_view(), name='currentuser'),
    path('be/api/about/', views.AboutListAPIView.as_view(), name='about'),
    path('be/api/confirmbooking/', views.ConfirmBookingApptView.as_view(), name='confirmbooking'),
    path('be/api/confirmbooking/<int:pk>/', views.ConfirmBookingApptView.as_view(), name='confirmbooking'),
    path('be/api/upload/', views.PdfSave.as_view(), name='upload'),
    path('be/api/getotp/', views.getTOTPAPIView.as_view(), name='getotp'),
    path('be/api/stripecheckoutview/', views.StripeCheckoutViewAPI.as_view(), name='stripecheckoutview'),
    path('be/api/testpayment', views.TestPaymentAPIView.as_view(), name='testpayment'),
    path('be/api/stripecustomercreate', views.StripeCustomerCreateAPIView.as_view(), name='stripecustomercreate'),
    path('be/api/stripepaymentintentcreate', views.StripePaymentIntentCreateAPIView.as_view(), name='stripepaymentintentcreate'),
    path('be/api/stripepaymentintentconfirm', views.StripePaymentIntentConfirmAPIView.as_view(), name='stripepaymentintentconfirm'),
    # path('be/api/securitylevellistpost', views.SecuritylevellistPostAPI.as_view(), name='securitylevellistpost'),
    path('be/api/schedulemonthappt/', views.ScheduleMonthAppointListAPIView.as_view(), name='schedulemonthappt'),
    # path('be/api/apptchannel/', views.ApptChannelAPIView.as_view(), name='apptchannel'),
    path('be/api/treatmentpackageinsert', views.TreatmentPackageInsertAPIView.as_view(), name='treatmentpackageinsert'),
    path('be/api/treatmentpackagelist', views.TreatmentPackageListAPIView.as_view(), name='treatmentpackagelist'),
    path('be/api/itemsitelistinitial/', views.ItemSitelistIntialAPIView.as_view(), name='itemsitelistinitial'),
    path('be/api/staffinsert/', views.StaffInsertAPIView.as_view(), name='staffinsert'),
    path('be/api/excelstaffinsert/', views.ExcelStaffInsertAPIView.as_view(), name='excelstaffinsert'),
    path('be/api/excelcustomerinsert/', views.ExcelCustomerInsertAPIView.as_view(), name='excelcustomerinsert'),
    path('be/api/fmspwuserlist/', views.FmspwListAPIView.as_view(), name='fmspwuserlist'),
    path('be/api/excelstockinsert/', views.ExcelStockInsertAPIView.as_view(), name='excelstockinsert'),
    path('be/api/tmptreatmentnewservice/', views.TmpTreatmentNewServiceAPIView.as_view(), name='tmptreatmentnewservice'),
    path('be/api/gender/', views.GenderListAPIView.as_view(), name='gender'),
    path('be/api/itemflexiservice/', views.ItemFlexiserviceListAPIView.as_view(), name='itemflexiservice'),
    path('be/api/staffperformance/', views.staffPerformanceAPIView.as_view(), name='staffperformance'),
    path('be/api/staffcustomerhistory/', views.staffCustomerHistoryAPIView.as_view(), name='staffcustomerhistory'),
    path('be/api/securitylevellistdupdel/', views.SecuritylevellistDuplicateDelete.as_view(), name='securitylevellistdupdel'),
    path('be/api/custsearchclass/', views.CustSearchClassAPI.as_view(), name='custsearchclass'),
    path('be/api/tmptreatmentnewservice/<int:pk>/', views.TmpTreatmentNewServiceAPIView.as_view(), name='tmptreatmentnewservice'),
    path('be/api/customerinvoicetemplateupload/', views.customerinvoicetemplateupload.as_view(), name='customerinvoicetemplateupload'),
    path('be/api/customerinvoicetemplatefiledownload/', views.customerinvoicetemplatefiledownload.as_view(), name='customerinvoicetemplatefiledownload'),
    path('be/api/prepaidvalidperiod/', views.PrepaidValidperiodAPIView.as_view(), name='prepaidvalidperiod'),
    path('be/api/customerreceiptprintbeforecheckout/', views.CustomerReceiptPrintBeforeCheckoutList.as_view(), name='customerreceiptprintbeforecheckout'),
    path('be/api/availableservicetimeslots/', views.AvailableTimeSlotsAPIView.as_view(), name='availableservicetimeslots'),
    path('be/api/treatmentbalanceimport/', views.TreatmentBalanceImportAPIView.as_view(), name='treatmentbalanceimport'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)