from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'salon', views.SalonViewset, basename='salon')
router.register(r'catalogitemdept', views.CatalogItemDeptViewset, basename='catalogitemdept')
router.register(r'servicestock', views.ServiceStockViewset, basename='servicestock')
router.register(r'retailstock', views.RetailStockListViewset, basename='retailstock')
router.register(r'packagestock', views.PackageStockViewset, basename='packagestock')
router.register(r'packagedtl', views.PackageDtlViewset, basename='packagedtl')
router.register(r'prepaidstock', views.PrepaidStockViewset, basename='prepaidstock')
router.register(r'voucherstock', views.VoucherStockViewset, basename='voucherstock')
router.register(r'catalogitemrange', views.CatalogItemRangeViewset, basename='catalogitemrange')
router.register(r'catalogsearch', views.CatalogSearchViewset, basename='catalogsearch')
router.register(r'salonsearch', views.SalonProductSearchViewset, basename='salonsearch')
router.register(r'topuptreatment', views.TopupViewset, basename='topuptreatment')
router.register(r'catalogfavorites', views.CatalogFavoritesViewset, basename='catalogfavorites')
router.register(r'treatmentdone', views.TreatmentDoneViewset, basename='treatmentdone')
router.register(r'trmttmpitemhelper', views.TrmtTmpItemHelperViewset, basename='trmttmpitemhelper')
router.register(r'topupproduct', views.TopupproductViewset, basename='topupproduct')
router.register(r'topupprepaid', views.TopupprepaidViewset, basename='topupprepaid')
router.register(r'reversal', views.ReversalListViewset, basename='reversal')
router.register(r'showbalance', views.ShowBalanceViewset, basename='showbalance')
router.register(r'reversereason', views.ReverseTrmtReasonAPIView, basename='reversereason')
router.register(r'void', views.VoidViewset, basename='void')
router.register(r'voidreason', views.VoidReasonViewset, basename='voidreason')
router.register(r'treatmentacclist', views.TreatmentAccListViewset, basename='treatmentacclist')
router.register(r'creditnotelist', views.CreditNoteListViewset, basename='creditnotelist')
router.register(r'productacclist', views.ProductAccListViewset, basename='productacclist')
router.register(r'prepaidacclist', views.PrepaidAccListViewset, basename='prepaidacclist')
router.register(r'prepaidaccpaymentlist', views.PrepaidAccPaymentListViewset, basename='prepaidaccpaymentlist')
router.register(r'combo', views.ComboViewset, basename='combo')
router.register(r'billing', views.BillingViewset, basename='billing')
router.register(r'prepaidpay', views.PrepaidPayViewset, basename='prepaidpay'),
router.register(r'holditem', views.HolditemdetailViewset, basename='holditem'),
router.register(r'stockusage', views.StockUsageViewset, basename='stockusage'),
router.register(r'stockusagememo', views.StockUsageMemoViewset, basename='stockusagememo'),
router.register(r'treatmentface', views.TreatmentFaceViewset, basename='treatmentface'),
router.register(r'transactionhistory', views.TransactionHistoryViewset, basename='transactionhistory'),
router.register(r'siteappointsetting', views.SiteApptSettingViewset, basename='siteappointsetting'),
router.register(r'customeraccount', views.CustomerAccountViewset, basename='customeraccount'),
router.register(r'treatmentusagelist', views.TreatmentUsageListViewset, basename='treatmentusagelist'),
router.register(r'topupcombinedlist', views.TopupCombinedViewset, basename='topupcombinedlist'),
router.register(r'paymodepiedashboard', views.PayModePieDashboardViewset, basename='paymodepiedashboard'),
router.register(r'catalogitemdiv', views.CatalogItemDivViewset, basename='catalogitemdiv')
router.register(r'department', views.DepartmentViewset, basename='department')
router.register(r'brand', views.BrandViewset, basename='brand')
router.register(r'productpurchase', views.ProductPurchaseListViewset, basename='productpurchase')
router.register(r'flexiserviceslist', views.FlexiServicesListViewset, basename='flexiserviceslist')
router.register(r'transactioninvoices', views.TransactionInvoicesViewset, basename='transactioninvoices')
router.register(r'treatmentdonenew', views.TreatmentDoneNewViewset, basename='treatmentdonenew')
router.register(r'voucherpromo', views.VoucherPromoViewset, basename='voucherpromo')
# router.register(r'sessiontmpitemhelper', views.SessionTmpItemHelperViewset, basename='sessiontmpitemhelper')
router.register(r'ecomservicesdept', views.EcomServicesDeptViewset, basename='ecomservicesdept')
router.register(r'ecomservicestock', views.EcomServiceStockViewset, basename='ecomservicestock')



# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('be/api/', include(router.urls)),
    path('be/api/otp/', views.ForgotPswdRequestOtpAPIView.as_view(), name='otp'),
    path('be/api/otpvalidate/', views.ForgotPswdOtpValidationAPIView.as_view(), name='otpvalidate'),
    path('be/api/passwordreset/', views.ResetPasswordAPIView.as_view(), name='passwordreset'),
    # path('be/api/updatestock/', views.UpdateStockAPIView.as_view(), name='updatestock'),
    path('be/api/receiptpdfsendsms/', views.ReceiptPdfSendSMSAPIView.as_view(), name='receiptpdfsendsms'),
    path('be/api/custsign/', views.CustomerSignatureAPIView.as_view(), name='custsign'),
    path('be/api/dashboardcust/', views.DashboardCustAPIView.as_view(), name='dashboardcust'),
    path('be/api/dashboardvoucher/', views.DashboardVoucherAPIView.as_view(), name='dashboardvoucher'),
    path('be/api/dashboardtd/', views.DashboardTDAPIView.as_view(), name='dashboardtd'),
    path('be/api/dashboardtopproduct/', views.DashboardTopProductAPIView.as_view(), name='dashboardtopproduct'),
    path('be/api/dashboardchart/', views.DashboardChartAPIView.as_view(), name='dashboardchart'),
    path('be/api/creditnotepay/', views.CreditNotePayAPIView.as_view(), name='creditnotepay'),
    path('be/api/voidcheck/', views.VoidCheck.as_view(), name='voidcheck'),
    path('be/api/voidcancel/', views.VoidCancel.as_view(), name='voidcancel'),
    # path('be/api/deleteapi/', views.DeleteAPIView.as_view(), name='deleteapi'),
    # path('be/api/controlno/', views.ControlAPIView.as_view(), name='controlno'),
    path('be/api/treatmenthistory/', views.TreatmentHistoryAPIView.as_view(), name='treatmenthistory'),
    path('be/api/stockusageproduct/', views.StockUsageProductAPIView.as_view(), name='stockusageproduct'),
    # path('be/getpdfPage',views.getPdfPage,name='getpdfpage'),
    path('be/api/servicelist/', views.ServiceListAPIView.as_view(), name='servicelist'),
    path('be/api/productlist/', views.ProductListAPIView.as_view(), name='productlist'),
    path('be/api/prepaidaccpage/', views.PrepaidAccountListAPIView.as_view(), name='prepaidaccpage'),
    path('be/api/treatmentopenaccpage/', views.TreatmentOpenListAPIView.as_view(), name='treatmentopenaccpage'),
    path('be/api/treatmentdoneaccpage/', views.TreatmentDoneListAPIView.as_view(), name='treatmentdoneaccpage'),
    path('be/api/voucheraccpage/', views.VoucherAccListAPIView.as_view(), name='treatmentdoneaccpage'),
    path('be/api/holditemaccpage/', views.HoldItemListAPIView.as_view(), name='treatmentdoneaccpage'),
    path('be/api/creditnoteaccpage/', views.CreditNoteListAPIView.as_view(), name='creditnoteaccpage'),
    path('be/api/ecomlocationselect/', views.EcomLocationSelectAPIView.as_view(), name='ecomlocationselect'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


