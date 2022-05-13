from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from . import views



# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'jobtitle', views.JobTitleViewset)
router.register(r'room', views.RoomViewset)
router.register(r'comboservices', views.ComboServicesViewset)
router.register(r'category', views.CategoryViewset)
router.register(r'type', views.TypeViewset)
router.register(r'itemcart', views.itemCartViewset)
router.register(r'voucher', views.VoucherRecordViewset)
router.register(r'empcartlist', views.EmployeeCartAPI)
router.register(r'pospackagedeposit', views.PosPackagedepositViewset)
router.register(r'smtpsettings', views.SmtpSettingsViewset)
router.register(r'cartpopup', views.CartPopupViewset)
router.register(r'cartservicecourse', views.CartServiceCourseViewset)
router.register(r'cartprepaid', views.CartPrepaidViewset)
router.register(r'coursetmpitemhelper', views.CourseTmpItemHelperViewset, basename='coursetmpitemhelper')
router.register(r'changestaffs', views.ChangeStaffViewset, basename='changestaffs')
router.register(r'changedate', views.ChangePaymentDateViewset, basename='changedate')
router.register(r'addremovestaff', views.AddRemoveSalesStaffViewset, basename='addremovestaff')
router.register(r'packagesertmpitemhelper', views.PackageServiceTmpItemHelperViewset, basename='packagesertmpitemhelper')
router.register(r'salarysubtype', views.SalarySubTypeLookupViewset)
router.register(r'modeofpayment', views.ModeOfPaymentViewset)
router.register(r'voucheraccount', views.VoucherRecordAccViewset)


# router.register(r'users', views.UserViewSet)

router.register(r'projectlist', views.ProjectListViewset, 'projectlist')
router.register(r'activitylist', views.ActivityListViewset, 'activitylist')
router.register(r'quotationlist', views.QuotationListViewset, 'quotationlist')
router.register(r'manualinvoicelist', views.ManualInvoiceListViewset, 'manualinvoicelist')
router.register(r'workorderinvoicelist', views.WorkOrderInvoiceListViewset, 'workorderinvoicelist')
router.register(r'deliveryorderlist', views.DeliveryOrderListViewset, 'deliveryorderlist')

router.register(r'polist', views.POListViewset, 'polist')
router.register(r'quotationaddr', views.QuotationAddrViewset, 'quotationaddr')
router.register(r'manualinvoiceaddr', views.ManualInvoiceAddrViewset, 'manualinvoiceaddr')
router.register(r'workorderinvoiceaddr', views.WorkOrderInvoiceAddrViewset, 'workorderinvoiceaddr')
router.register(r'deliveryorderaddr', views.DeliveryOrderAddrViewset, 'deliveryorderaddr')

router.register(r'poaddr', views.POAddrViewset, 'poaddr')
router.register(r'quotationdetail', views.QuotationDetailViewset, 'quotationdetail')
router.register(r'manualinvoicedetail', views.ManualInvoiceDetailViewset, 'manualinvoicedetail')
router.register(r'workorderinvoicedetail', views.WorkOrderInvoiceDetailViewset, 'workorderinvoicedetail')
router.register(r'deliveryorderdetail', views.DeliveryOrderDetailViewset, 'deliveryorderdetail')

router.register(r'podetail', views.PODetailViewset, 'podetail')
router.register(r'quotationitem', views.QuotationItemViewset, 'quotationitem')
router.register(r'manualinvoiceitem', views.ManualInvoiceItemViewset, 'manualinvoiceitem')
router.register(r'workorderinvoiceitem', views.WorkOrderInvoiceItemViewset, 'workorderinvoiceitem')
router.register(r'deliveryorderitem', views.DeliveryOrderItemViewset, 'deliveryorderitem')

router.register(r'poitem', views.POItemViewset, 'poitem')
router.register(r'dropdown', views.DropdownViewset, 'dropdown')
router.register(r'dropdownproject', views.DropdownProjectViewset, 'dropdownproject')
router.register(r'qpoitem', views.QPOItemViewset, 'qpoitem')
router.register(r'city', views.CityViewset, 'city')
router.register(r'state', views.StateViewset, 'state')
router.register(r'country', views.CountryViewset, 'country')
router.register(r'timelog', views.TimeLogViewset, 'timelog')
router.register(r'gstlist', views.GSTListViewset, 'gstlist')

router.register(r'fullstocklist', views.StockListViewset, 'fullstocklist')
router.register(r'allstocklist', views.AllStockListViewset, 'allstocklist')
router.register(r'itemuomprice', views.ItemUOMPriceListViewset, 'itemuomprice')
router.register(r'itembatch', views.ItemBatchListViewset, 'itembatch')
router.register(r'itembrand', views.ItemBrandListViewset, 'itembrand')
router.register(r'itemrange', views.ItemRangeListViewset, 'itemrange')
router.register(r'itemdeptdropdown', views.ItemDeptListViewset, 'itemdeptdropdown')
router.register(r'sitecode', views.SiteCodeListViewset, 'sitecode')
router.register(r'employeelist', views.EmployeeListViewset, 'employeelist')
router.register(r'itemsupply', views.ItemSupplyListViewset, 'itemsupply')
router.register(r'supplycontactinfo', views.SupplyContactInfoViewset, 'supplycontactinfo')
router.register(r'systemlog', views.SystemLogViewset, 'systemlog')
router.register(r'stktrn', views.StktrnListViewset, 'stktrn')
router.register(r'dolist', views.DOListViewset, 'dolist')
router.register(r'doitem', views.DOItemViewset, 'doitem')
router.register(r'stockinlist', views.StockInListViewset, 'stockinlist')
router.register(r'stockinitem', views.StockInItemViewset, 'stockinitem')
router.register(r'stockinhqonlylist', views.StockInHQonlyListViewset, 'stockinhqonlylist')
router.register(r'stockoutlist', views.StockOutListViewset, 'stockoutlist')
router.register(r'stockoutitem', views.StockOutItemViewset, 'stockoutitem')
router.register(r'stockouthqonlylist', views.StockOutHQonlyListViewset, 'stockouthqonlylist')
router.register(r'stockadjlist', views.StockAdjListViewset, 'stockadjlist')
router.register(r'stockadjitem', views.StockAdjItemViewset, 'stockadjitem')
router.register(r'stocksheetlist', views.StockSheetListViewset, 'stocksheetlist')
router.register(r'stocksheetitem', views.StockSheetItemViewset, 'stocksheetitem')
router.register(r'stocktakelist', views.StockTakeListViewset, 'stocktakelist')
router.register(r'stocktakeitem', views.StockTakeItemViewset, 'stocktakeitem')
router.register(r'stockusagelist', views.StockUsageListViewset, 'stockusagelist')
router.register(r'stockusageitem', views.StockUsageItemViewset, 'stockusageitem')
router.register(r'grnlist', views.GRNListViewset, 'grnlist')
router.register(r'grnitem', views.GRNItemViewset, 'grnitem')
router.register(r'vgrnlist', views.VGRNListViewset, 'vgrnlist')
router.register(r'vgrnitem', views.VGRNItemViewset, 'vgrnitem')
router.register(r'poapprovallist', views.POApprovalListViewset, 'poapprovallist')
router.register(r'poapprovalitem', views.POApprovalItemViewset, 'poapprovalitem')
router.register(r'poapprovalhqonlylist', views.POApprovalHQonlyListViewset, 'poapprovalhqonlylist')
router.register(r'authorise', views.AuthoriseViewset, 'authorise')
router.register(r'commissionprofile', views.CommissionProfiles, 'commissionprofile')
router.register(r'customerprojectlist', views.CustomerProjectListViewset)
router.register(r'deliveryordersign', views.DeliveryOrderSignViewset)


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/receiptpdf/', views.ReceiptPdfGeneration.as_view(), name='receiptpdf'),
    path('api/receiptpdfsend/', views.ReceiptPdfSend.as_view(), name='receiptpdfsend'),
    path('api/paymentremarks/', views.PaymentRemarksAPIView.as_view(), name='paymentremarks'),
    path('api/holditemsetup/', views.HolditemSetupAPIView.as_view(), name='holditemsetup'),
    path('api/exchangeproduct/', views.ExchangeProductAPIView.as_view(), name='exchangeproduct'),
    path('api/exchangeproductconfirm/', views.ExchangeProductConfirmAPIView.as_view(), name='exchangeproductconfirm'),
    path('api/coursetmp/', views.CourseTmpAPIView.as_view(), name='coursetmp'),
    path('api/cartdelete/', views.cart_delete, name='cartdelete'),
    path('api/cartitemdelete/', views.CartItemDeleteAPIView.as_view(), name='cartitemdelete'),
    path('api/userauthorizationpopup/', views.UserAuthorizationPopup.as_view(), name='userauthorizationpopup'),
    path('api/manualinvoicepdf/', views.ManualInvoiceFormatAPIView.as_view(), name='manualinvoicepdf'),
    path('api/workorderinvoicepdf/', views.WorkOrderInvoiceFormatAPIView.as_view(), name='workorderinvoicepdf'),
    path('api/quotationtocart/', views.QuotationToCartAPIView.as_view(), name='quotationtocart'),
    path('api/satransactomanualinvoice/', views.SatransacToManualInvoiceAPIView.as_view(), name='satransactomanualinvoice'),
    path('api/satransactoworkorderinvoice/', views.SatransacToWorkOrderInvoiceAPIView.as_view(), name='satransactoworkorderinvoice'),
    path('api/workordertodelivery/', views.WorkOrderITODeliveryAPIView.as_view(), name='workordertodelivery'),
    path('api/deliveryinvoicepdf/', views.DeliveryOrderFormatAPIView.as_view(), name='deliveryinvoicepdf'),
    path('api/employeestafflist/', views.EmployeeListAPI.as_view(), name='employeestafflist'),
    path('api/satransacnoreflist/', views.SaTransacnorefAPIView.as_view(), name='satransacnoreflist'),
    path('api/workorderinvno/', views.WorkOrderInvoiceNoAPIView.as_view(), name='workorderinvno'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 
