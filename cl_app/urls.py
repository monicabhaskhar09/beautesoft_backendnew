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



# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/otp/', views.ForgotPswdRequestOtpAPIView.as_view(), name='otp'),
    path('api/otpvalidate/', views.ForgotPswdOtpValidationAPIView.as_view(), name='otpvalidate'),
    path('api/passwordreset/', views.ResetPasswordAPIView.as_view(), name='passwordreset'),
    # path('api/updatestock/', views.UpdateStockAPIView.as_view(), name='updatestock'),
    path('api/receiptpdfsendsms/', views.ReceiptPdfSendSMSAPIView.as_view(), name='receiptpdfsendsms'),
    path('api/custsign/', views.CustomerSignatureAPIView.as_view(), name='custsign'),
    path('api/dashboardcust/', views.DashboardCustAPIView.as_view(), name='dashboardcust'),
    path('api/dashboardvoucher/', views.DashboardVoucherAPIView.as_view(), name='dashboardvoucher'),
    path('api/dashboardtd/', views.DashboardTDAPIView.as_view(), name='dashboardtd'),
    path('api/dashboardtopproduct/', views.DashboardTopProductAPIView.as_view(), name='dashboardtopproduct'),
    path('api/dashboardchart/', views.DashboardChartAPIView.as_view(), name='dashboardchart'),
    path('api/creditnotepay/', views.CreditNotePayAPIView.as_view(), name='creditnotepay'),
    path('api/voidcheck/', views.VoidCheck.as_view(), name='voidcheck'),
    path('api/voidcancel/', views.VoidCancel.as_view(), name='voidcancel'),
    # path('api/deleteapi/', views.DeleteAPIView.as_view(), name='deleteapi'),
    # path('api/controlno/', views.ControlAPIView.as_view(), name='controlno'),
    path('api/treatmenthistory/', views.TreatmentHistoryAPIView.as_view(), name='treatmenthistory'),
    path('api/stockusageproduct/', views.StockUsageProductAPIView.as_view(), name='stockusageproduct'),
    # path('getpdfPage',views.getPdfPage,name='getpdfpage'),
    path('api/servicelist/', views.ServiceListAPIView.as_view(), name='servicelist'),
    path('api/productlist/', views.ProductListAPIView.as_view(), name='productlist'),
    path('api/prepaidaccpage/', views.PrepaidAccountListAPIView.as_view(), name='prepaidaccpage'),
    path('api/treatmentopenaccpage/', views.TreatmentOpenListAPIView.as_view(), name='treatmentopenaccpage'),
    path('api/treatmentdoneaccpage/', views.TreatmentDoneListAPIView.as_view(), name='treatmentdoneaccpage'),
    path('api/voucheraccpage/', views.VoucherAccListAPIView.as_view(), name='treatmentdoneaccpage'),
    path('api/holditemaccpage/', views.HoldItemListAPIView.as_view(), name='treatmentdoneaccpage'),
    path('api/creditnoteaccpage/', views.CreditNoteListAPIView.as_view(), name='creditnoteaccpage'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


