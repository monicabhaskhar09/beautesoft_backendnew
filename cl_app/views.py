from django.forms import Field
import pyotp
import time
from twilio.rest import Client
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import (SiteGroupSerializer, CatalogItemDeptSerializer, 
ItemRangeSerializer, StockSerializer, StockRetailSerializer, StockIdSerializer,
OtpRequestSerializer, OtpValidationSerializer, ResetPasswordSerializer, CustomerSignSerializer,
TreatmentAccountSerializer, TopupSerializer, TreatmentDoneSerializer, TopupproductSerializer,
TopupprepaidSerializer,TreatmentReversalSerializer,ShowBalanceSerializer,ReverseTrmtReasonSerializer,
VoidSerializer,PosDaudDetailsSerializer,VoidReasonSerializer,TreatmentAccSerializer,
DashboardSerializer,CreditNoteSerializer,ProductAccSerializer,PrepaidAccSerializer,PrepaidacSerializer,
CreditNoteAdjustSerializer,BillingSerializer,CreditNotePaySerializer,PrepaidPaySerializer,VoidListSerializer,
CartPrepaidSerializer, VoidCancelSerializer,HolditemdetailSerializer,HolditemSerializer,HolditemupdateSerializer,
TreatmentHistorySerializer,StockUsageSerializer,StockUsageProductSerializer,TreatmentUsageSerializer,
StockUsageMemoSerializer,TreatmentfaceSerializer,SiteApptSettingSerializer,HolditemAccListSerializer,
PodhaudSerializer,CustomerAccountSerializer,TreatmentUsageListSerializer,TreatmentUsageStockSerializer,
ItemDivSerializer,ProductPurchaseSerializer,TransactionInvoiceSerializer,TransactionManualInvoiceSerializer,
TreatmentPackageDoneListSerializer,VoucherPromoSerializer,SessionTmpItemHelperSerializer,
TreatmentPackgeSerializer)
from cl_table.serializers import PostaudSerializer, TmpItemHelperSerializer
from .models import (SiteGroup, ItemSitelist, ReverseTrmtReason, VoidReason,TreatmentUsage,UsageMemo,
Treatmentface,Usagelevel,priceChangeLog,TmpTreatmentSession,VoucherPromo,SmsProcessLog,
TmpItemHelperSession)
from cl_table.models import (Employee, Fmspw, ItemClass, ItemDept, ItemRange, Stock, ItemUomprice, 
PackageDtl, ItemDiv, PosDaud, PosTaud, Customer, GstSetting, ControlNo, TreatmentAccount, DepositAccount, 
PrepaidAccount, Treatment,PosHaud,TmpItemHelper,Appointment,Source,PosHaud,ReverseDtl,ReverseHdr,
CreditNote,Multistaff,ItemHelper,ItemUom,Treatment_Master,Holditemdetail,PrepaidAccountCondition,
CnRefund,ItemBrand,Title,ItemBatch,Stktrn,Paytable,ItemLink,Appointment,ItemStocklist,Systemsetup,
Tmpmultistaff,PosDisc,CustomerPoint,CustomerPointDtl,RewardPolicy,PackageAuditingLog,AuditLog,
ItemFlexiservice,TreatmentPackage,ItemBatchSno,Tmptreatment,Treatmentids)
from custom.models import (ItemCart, Room, Combo_Services,VoucherRecord,PosPackagedeposit,SmtpSettings,
ManualInvoiceModel)
from datetime import date, timedelta
from datetime import datetime
import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator,InvalidPage
from custom.views import response, get_client_ip
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from Cl_beautesoft.settings import SMS_SECRET_KEY, SMS_ACCOUNT_SID, SMS_AUTH_TOKEN, SMS_SENDER
from custom.services import GeneratePDF
from .permissions import authenticated_only
from rest_framework.decorators import action
from cl_table.views import get_in_val
from rest_framework import generics
from django.db.models import Sum
from rest_framework import exceptions
from django.shortcuts import get_object_or_404
from custom.serializers import ComboServicesSerializer
from .utils import general_error_response
from cl_table.authentication import TokenAuthentication,ExpiringTokenAuthentication
from django.template.loader import get_template
from Cl_beautesoft.settings import BASE_DIR, SITE_ROOT
from fpdf import FPDF 
from pyvirtualdisplay import Display
import pdfkit
import os
import math
import os.path
from Cl_beautesoft import settings
from django.template.defaulttags import register
from dateutil.relativedelta import relativedelta
import random
from django.db.models import Count
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.db.models.functions import Coalesce,Concat
from django.db import transaction, connection
from django.db.models import FloatField, ExpressionWrapper, F
from dateutil import parser
from itertools import chain 
from django.db.models import Case, When, Value, IntegerField,CharField, DateField,BooleanField
from django.contrib.auth import authenticate, login , logout, get_user_model
import json

type_ex = ['VT-Deposit','VT-Top Up','VT-Sales']
type_tx = ['Deposit','Top Up','Sales']
# Create your views here.
#sitegroup creation
class SalonViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = SiteGroup.objects.filter(is_active=True).order_by('-id')
    serializer_class = SiteGroupSerializer


    def get_queryset(self):
        queryset = SiteGroup.objects.filter(is_active=True).order_by('-id')
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = SiteGroup.objects.filter(is_active=True,description__icontains=q).order_by('-id')
        elif value and key is not None:
            if value == "asc":
                if key == 'description':
                    queryset = SiteGroup.objects.filter(is_active=True).order_by('description')
            elif value == "desc":
                if key == 'description':
                    queryset = SiteGroup.objects.filter(is_active=True).order_by('-description')

        return queryset

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Successfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                  
    
    # @authenticated_only
    def create(self, request):
        try:
            queryset = None
            serializer_class = None
            total = None
            serializer = self.get_serializer(data=request.data)
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            if serializer.is_valid():
                self.perform_create(serializer)
                control_obj = ControlNo.objects.filter(control_description__icontains="SiteGroup",Site_Codeid__id=site.id).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                code = str(control_obj.control_no)
                k = serializer.save(code=code)
                if k.id:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()

                state = status.HTTP_201_CREATED
                message = "Created Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_201_CREATED)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         
        
    def get_object(self, pk):
        try:
            return SiteGroup.objects.get(pk=pk,is_active=True)
        except SiteGroup.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            site_group = self.get_object(pk)
            serializer = SiteGroupSerializer(site_group)
            data = serializer.data
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         
            
    def update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            site_group = self.get_object(pk)
            serializer = SiteGroupSerializer(site_group, data=request.data)
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(serializer.errors, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         
        
    def destroy(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            data = None
            state = status.HTTP_204_NO_CONTENT
            try:
                instance = self.get_object(pk)
                self.perform_destroy(instance)
                message = "Deleted Succesfully"
                error = False
                result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result,status=status.HTTP_200_OK)    
            except Http404:
                pass

            message = "No Content"
            error = True
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
          
    def perform_destroy(self, instance):
        instance.is_active = False
        site = ItemSitelist.objects.filter(Site_Groupid=instance).update(Site_Groupid=None)
        instance.save()   

#ItemDept listing
class DepartmentViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:
            query = ItemDept.objects.filter(is_service=True, itm_status=True).values('pk','itm_desc','is_service','itm_status')
            if query:
                # serializer = DepartmentSerializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  query}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

 #ItemBrand listing            
class BrandViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:
            queryset = ItemBrand.objects.filter(itm_status=True).filter(
            Q(retail_product_brand=True) | Q(prepaid_brand=True) | Q(voucher_brand=True)).values(
            'pk','itm_desc','itm_status','retail_product_brand','prepaid_brand','voucher_brand')
                   
            if queryset:
                # serializer = ItemBrandSerializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  queryset}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
             

#ItemDept listing
class CatalogItemDeptViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CatalogItemDeptSerializer

    def list(self, request):
        try:
            queryset = ItemDept.objects.none()
            if request.GET.get('Item_Dept', None): 
                if not request.GET.get('Item_Dept', None) is None:
                    if request.GET.get('Item_Dept', None) == 'SERVICE':
                        queryset = ItemDept.objects.filter(is_service=True, itm_status=True).order_by('itm_seq')
                    elif request.GET.get('Item_Dept', None) == 'PACKAGE':
                        queryset = ItemDept.objects.filter(is_service=True, itm_status=True).order_by('itm_seq')
                    elif request.GET.get('Item_Dept', None) == 'RETAIL':
                        queryset = ItemBrand.objects.filter(retail_product_brand=True, itm_status=True).order_by('itm_seq')
                    elif request.GET.get('Item_Dept', None) == 'PREPAID':
                        queryset = ItemBrand.objects.filter(prepaid_brand=True, itm_status=True).order_by('itm_seq')
                    elif request.GET.get('Item_Dept', None) == 'VOUCHER':
                        queryset = ItemBrand.objects.filter(voucher_brand=True, itm_status=True).order_by('itm_seq')
                    else:
                        result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Dept id does not exist!!", 'error': True}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
           
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  serializer.data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
             

    def get_object(self, pk):
        try:
            return ItemDept.objects.get(pk=pk,itm_status=True)
        except ItemDept.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            itemdept = self.get_object(pk)
            serializer = CatalogItemDeptSerializer(itemdept)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         
#ItemRange listing
class CatalogItemRangeViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ItemRangeSerializer

    def list(self, request):
        try:
            queryset = ItemRange.objects.none()
            if request.GET.get('Item_Deptid',None):  
                if not request.GET.get('Item_Deptid',None) is None:
                    item_id = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), itm_status=True).first() 
                    if item_id:
                        queryset = ItemRange.objects.filter(itm_dept=item_id.itm_code, isservice=True,itm_status=True).order_by('pk')
                    if item_id is None:
                        branditem_id = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), itm_status=True).first()
                        if branditem_id:
                            queryset = ItemRange.objects.filter(itm_brand=branditem_id.itm_code,itm_status=True).order_by('pk')
                    if not item_id and not branditem_id:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
           
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

#ItemDiv listing
class CatalogItemDivViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ItemDiv.objects.filter(itm_isactive=True).order_by('-itm_seq')
    serializer_class = ItemDivSerializer

    def list(self, request):
        try:
            if self.request.GET.get('salon',None) == "0":
                #query = ItemDiv.objects.filter(itm_isactive=True).order_by('-itm_seq')
                query = ItemDiv.objects.filter(itm_isactive=True,issellable=True).order_by('-itm_seq')
                queryset = query.filter(~Q(itm_code=2)).order_by('-itm_seq')
            else:
                #queryset = ItemDiv.objects.filter(itm_isactive=True).order_by('-itm_seq')
                queryset = ItemDiv.objects.filter(itm_isactive=True,issellable=True).order_by('-itm_seq')

            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                var = [dict(i) for i in serializer.data]
                var.append({'id': 0,'itm_code': '','itm_desc': "All",'desc': "All"})
                
                if self.request.GET.get('salon',None) == "0":
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                    'data': var}
                else:
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                    'data': serializer.data}   
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

class FlexiServicesListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer 

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            system_setupids = Systemsetup.objects.filter(title='listDepartmentOnTreatmentForFlexi',value_name='listDepartmentOnTreatmentForFlexi').first()
            if system_setupids and system_setupids.value_data:
                depart = system_setupids.value_data.split(',')
                item_dept = list(set(ItemDept.objects.filter(pk__in=depart, is_service=True, itm_status=True).values_list('itm_code', flat=True).distinct()))
                queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_dept__in=item_dept).order_by('item_name')
                if queryset:
                    full_tot = queryset.count()
                    try:
                        limit = int(request.GET.get("limit",12))
                    except:
                        limit = 10
                    try:
                        page = int(request.GET.get("page",1))
                    except:
                        page = 1

                    paginator = Paginator(queryset, limit)
                    total_page = paginator.num_pages

                    try:
                        queryset = paginator.page(page)
                    except (EmptyPage, InvalidPage):
                        queryset = paginator.page(total_page) # last page

                    serializer = self.get_serializer(queryset, many=True)
                    resData = {
                        'dataList': serializer.data,
                        'pagination': {
                            "per_page":limit,
                            "current_page":page,
                            "total":full_tot,
                            "total_pages":total_page
                        }
                    }
                    result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  resData}
                else:
                    serializer = self.get_serializer()
                    result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}

            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            
            return Response(data=result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
    


                         
#services stock listing             
class ServiceStockViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def list(self, request):
        try:
            # now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            s_ids  = list(ItemStocklist.objects.filter(itemstocklist_status=True,
            itemsite_code=site.itemsite_code,item_code__startswith="3").values_list('item_code', flat=True).distinct())
            # print(s_ids,len(s_ids),"s_ids")
            queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_div="3",
            item_code__in=s_ids).order_by('item_name')
            # print(queryset,len(queryset),"queryset")

            
            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_dept = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), is_service=True, itm_status=True).first()
                    if not item_dept:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", 
                    item_dept=item_dept.itm_code,item_code__in=s_ids).order_by('item_name')
                # else:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            if request.GET.get('Item_Rangeid',None):
                if not request.GET.get('Item_Rangeid',None) is None:
                    if request.GET.get('Item_Rangeid',None):
                        itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isservice=True,itm_status=True).first()
                        if not itemrange:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE",
                         item_range=itemrange.itm_code,item_code__in=s_ids).order_by('item_name')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", 
                        item_dept=item_dept.itm_code,item_code__in=s_ids).order_by('item_name')
            
            if request.GET.get('search',None):
                if not request.GET.get('search',None) is None:
                    queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))
            
            # stock_lst = [i.pk for i in queryset if ItemStocklist.objects.filter(item_code=i.item_code,
            # itemsite_code=site.itemsite_code,itemstocklist_status=True).exists()]

            systemids = Systemsetup.objects.filter(title='stockOrderBy',
            value_name='stockOrderBy',isactive=True).first()

            if systemids and systemids.value_data == 'item_name':
                queryset = queryset.order_by('item_name') 
            elif systemids and systemids.value_data == 'item_seq':
                queryset = queryset.order_by('item_seq')
            elif systemids and systemids.value_data == 'item_desc':
                queryset = queryset.order_by('item_desc')
            elif systemids and systemids.value_data == 'item_code':
                queryset = queryset.order_by('item_code')
            else:
                queryset = queryset.order_by('item_name') 

                
            serializer_class =  StockSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            # v = result.get('data')
            # d = v.get("dataList")
            # for dat in d:
            #     dat["item_price"] = "{:.2f}".format(float(dat['item_price'])) if dat['item_price'] else "0.00"
        
            # now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            # totalh = now1.second - now.second
            # print(totalh,"total") 
            return Response(result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
          

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True, item_type="SINGLE")
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            # print(stock.Stock_PIC,"stock.Stock_PIC")
            if v['Stock_PIC']:
                # v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
                v['Stock_PIC'] = str(SITE_ROOT) + str(stock.Stock_PIC)
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         

#retail stock listing
class RetailStockListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockRetailSerializer

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            s_ids  = list(ItemStocklist.objects.filter(itemstocklist_status=True,
            itemsite_code=site.itemsite_code,item_code__startswith="1").values_list('item_code', flat=True).distinct())
           
            
            if request.GET.get('stock',None):
                queryset = Stock.objects.filter(item_isactive=True, item_div__in=["1","2"],
                item_code__in=s_ids).order_by('item_name')
            else:
                queryset = Stock.objects.filter(item_isactive=True, item_div="1",
                item_code__in=s_ids).order_by('item_name')

            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None),retail_product_brand=True,itm_status=True).first()
                    if not item_brand:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Brand id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True,item_div="1",item_brand=item_brand.itm_code,
                    item_code__in=s_ids).order_by('item_name')
                # else:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if request.GET.get('Item_Rangeid',None):
                if not request.GET.get('Item_Rangeid',None) is None:
                    if request.GET.get('Item_Rangeid',None):
                        itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isproduct=True,itm_status=True).first()
                        if not itemrange:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        queryset = Stock.objects.filter(item_isactive=True,item_div="1", item_range=itemrange.itm_code,
                        item_code__in=s_ids).order_by('item_name')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True,item_div="1", item_brand=item_brand.itm_code,
                        item_code__in=s_ids).order_by('item_name')

            if request.GET.get('search',None):
                if not request.GET.get('search',None) is None:
                    queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))

            systemids = Systemsetup.objects.filter(title='stockOrderBy',
            value_name='stockOrderBy',isactive=True).first()

            if systemids and systemids.value_data == 'item_name':
                queryset = queryset.order_by('item_name') 
            elif systemids and systemids.value_data == 'item_seq':
                queryset = queryset.order_by('item_seq')
            elif systemids and systemids.value_data == 'item_desc':
                queryset = queryset.order_by('item_desc')
            elif systemids and systemids.value_data == 'item_code':
                queryset = queryset.order_by('item_code')
            else:
                queryset = queryset.order_by('item_name') 
 
            limit = int(request.GET.get('limit',12)) if request.GET.get('limit',12) else 12
            page = int(request.GET.get('page',1)) if request.GET.get('page',1) else 1
            if page <= 0:
                raise Exception('Page less than one not allowed!!') 
            
            length = len(queryset)
            paginator = Paginator(queryset, limit) # chunks of 1000
            total_page = 1;total = len(queryset)
            if len(queryset) > int(limit):
                total_page = math.ceil(len(queryset)/int(limit))

           

            if queryset:
                if int(page) > total_page:
                    result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 
                    'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,"total_pages":total_page}}, 
                    'dataList': []}}
                    return Response(result, status=status.HTTP_200_OK) 
            
          
            lst = [] 
            for row in paginator.page(page).object_list:
                q = row
                stock = Stock.objects.filter(item_isactive=True, pk=q.pk).first()
              
                uomlst = []
                
                itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code).order_by('id')
                for i in itemuomprice:
                    itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=i.item_uom).order_by('id').first()
                    if itemuom:
                        itemuom_id = int(itemuom.id)
                        itemuom_desc = itemuom.uom_desc

                        batch = ItemBatch.objects.filter(item_code=stock.item_code,site_code=site.itemsite_code,
                        uom=itemuom.uom_code).order_by('-pk').last()

                        uom = {
                                "itemuomprice_id": int(i.id),
                                "item_uom": i.item_uom,
                                "uom_desc": i.uom_desc,
                                "item_price": "{:.2f}".format(float(i.item_price)),
                                "itemuom_id": itemuom_id, 
                                "itemuom_desc" : itemuom_desc,
                                "onhand_qty": int(batch.qty) if batch else 0
                                }
                        uomlst.append(uom)
                
            
                serializer = StockRetailSerializer(stock)
                dvl = serializer.data
                dvl.update({'uomprice': uomlst}) 
                if uomlst != []:
                    lst.append(dvl)
                    
                        
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
            "total_pages":total_page}}, 'dataList': lst}}  
            return Response(result, status=status.HTTP_200_OK)
          
                  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            ip = get_client_ip(request)
            stock = self.get_object(pk)
            serializer = StockRetailSerializer(stock)
            uomlst = []; uom = {}
            itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code)
            for i in itemuomprice:
                itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=i.item_uom).order_by('id').first()
                if itemuom:
                    uom = {
                            "itemuomprice_id": int(i.id),
                            "item_uom": i.item_uom,
                            "uom_desc": i.uom_desc,
                            "item_price": "{:.2f}".format(float(i.item_price)),
                            "itemuom_id": int(itemuom.id), 
                            "itemuom_desc" : itemuom.uom_desc}
                    uomlst.append(uom)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data, 'Item_Price': uomlst}
            v = result.get('data')
            q = dict(v)
            if q['Stock_PIC']:
                # q['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
                q['Stock_PIC'] = str(SITE_ROOT) + str(stock.Stock_PIC)
            val = {'uomprice': uomlst}  
            q.update(val) 
            result['data'] = q if uomlst != [] else []       
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         

    # def create(self, request):
    #     if self.request.GET.get('cust_id',None) is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer id!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
    #     cust_id = Customer.objects.filter(pk=self.request.GET.get('cust_id',None)).last()

    #     if self.request.GET.get('stock_id',None) is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Stock id!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 
    #     stock_id = Stock.objects.filter(pk=self.request.GET.get('stock_id',None)).last() 
    
    #     if self.request.GET.get('uom_id',None) is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give uom id!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
    #     uom_id = ItemUomprice.objects.filter(pk=self.request.GET.get('uom_id',None)).last()

    #     item_uom = self.request.GET.get('item_uom',None)
    #     if item_uom is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give item uom!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

    #     item_price = self.request.GET.get('item_price',None)
    #     if item_price is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give item price!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

    #     temp_uomprice = TempUomPrice.objects.create(Cust_Codeid=cust_id,Item_Codeid=stock_id,Item_UOMid=uom_id,
    #                         item_uom=item_uom,item_price=item_price)
    #     if temp_uomprice:
    #         result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False}
    #     else:
    #         result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed to create ", 'error': False}
    #     return Response(data=result, status=status.HTTP_200_OK)

#package stock listing
class PackageStockViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            s_ids  = list(ItemStocklist.objects.filter(itemstocklist_status=True,
            itemsite_code=site.itemsite_code,item_code__startswith="3").values_list('item_code', flat=True).distinct())
           
            queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_div="3",
            item_code__in=s_ids).order_by('item_name')
            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_dept = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), is_service=True, itm_status=True).first()
                    if not item_dept:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_dept=item_dept.itm_code,
                    item_code__in=s_ids).order_by('item_name')
                # else:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            if request.GET.get('Item_Rangeid',None):
                if not request.GET.get('Item_Rangeid',None) is None:
                    if request.GET.get('Item_Rangeid',None):
                        itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isservice=True,itm_status=True).first()
                        if not itemrange:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_range=itemrange.itm_code,
                        item_code__in=s_ids).order_by('item_name')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_dept=item_dept.itm_code,
                        item_code__in=s_ids).order_by('item_name')
            
            if request.GET.get('search',None):
                if not request.GET.get('search',None) is None:
                    queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))
            
            # stock_lst = [i.pk for i in queryset if ItemStocklist.objects.filter(item_code=i.item_code,itemsite_code=site.itemsite_code,
            # itemstocklist_status=True).exists()]
           
            

            systemids = Systemsetup.objects.filter(title='stockOrderBy',
            value_name='stockOrderBy',isactive=True).first()

            if systemids and systemids.value_data == 'item_name':
                queryset = queryset.order_by('item_name') 
            elif systemids and systemids.value_data == 'item_seq':
                queryset = queryset.order_by('item_seq')
            elif systemids and systemids.value_data == 'item_desc':
                queryset = queryset.order_by('item_desc')
            elif systemids and systemids.value_data == 'item_code':
                queryset = queryset.order_by('item_code')
            else:
                queryset = queryset.order_by('item_name') 


            serializer_class =  StockSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            # v = result.get('data')
            # d = v.get("dataList")
            # for dat in d:
            #     dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
            

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True, item_type="PACKAGE")
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                # v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
                v['Stock_PIC'] = str(SITE_ROOT) + str(stock.Stock_PIC)
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                
#PackageDtl listing
class PackageDtlViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockIdSerializer

    def list(self, request):
        try:
            stock = Stock.objects.filter(pk=request.GET.get('stock_id',None), item_isactive=True)
            if not stock:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock Id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            for s in stock:     
                if s.Stock_PIC: 
                    # image = {"STOCK_PIC" : str("http://"+request.META['HTTP_HOST'])+str(s.Stock_PIC.url)}
                    image = {"STOCK_PIC" : str(SITE_ROOT)+str(s.Stock_PIC)}
                else:
                    image = None
                detail = []; package = {}
                package_dtl = PackageDtl.objects.filter(package_code=s.item_code)
                if package_dtl:
                    for p in package_dtl:
                        if p:
                            package = {
                                "stock_id": s.pk,
                                "id": p.id,
                                "Description": p.description}
                            detail.append(package)
                    package_data = {"package_description": detail,
                                    "image" : image}
                    result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': package_data }
                else:
                    serializer = self.get_serializer()
                    result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                    
#prepaid stock listing
class PrepaidStockViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            s_ids  = list(ItemStocklist.objects.filter(itemstocklist_status=True,
            itemsite_code=site.itemsite_code,item_code__startswith="5").values_list('item_code', flat=True).distinct())
           
            queryset = Stock.objects.filter(item_isactive=True, item_div="5",
            item_code__in=s_ids).order_by('item_name')
            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), prepaid_brand=True).first()
                    if not item_brand:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code,
                    item_code__in=s_ids).order_by('item_name')
                # else:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            if request.GET.get('Item_Rangeid',None):
                if not request.GET.get('Item_Rangeid',None) is None:
                    if request.GET.get('Item_Rangeid',None):
                        itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isprepaid=True,itm_status=True).first()
                        if not itemrange:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code,
                        item_code__in=s_ids).order_by('item_name')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code,
                        item_code__in=s_ids).order_by('item_name')

            if request.GET.get('search',None):
                if not request.GET.get('search',None) is None:
                    queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))
            

            # stock_lst = [i.pk for i in queryset if ItemStocklist.objects.filter(item_code=i.item_code,itemsite_code=site.itemsite_code,
            # itemstocklist_status=True).exists()]
           
            
            systemids = Systemsetup.objects.filter(title='stockOrderBy',
            value_name='stockOrderBy',isactive=True).first()

            if systemids and systemids.value_data == 'item_name':
                queryset = queryset.order_by('item_name') 
            elif systemids and systemids.value_data == 'item_seq':
                queryset = queryset.order_by('item_seq')
            elif systemids and systemids.value_data == 'item_desc':
                queryset = queryset.order_by('item_desc')
            elif systemids and systemids.value_data == 'item_code':
                queryset = queryset.order_by('item_code')
            else:
                queryset = queryset.order_by('item_name')
 

            serializer_class =  StockSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            # v = result.get('data')
            # d = v.get("dataList")
            # for dat in d:
            #     dat["item_price"] = "{:.2f}".format(float(dat['item_price'])) if dat['item_price'] else "0.00" 
            #     dat["prepaid_value"] = "{:.2f}".format(float(dat['prepaid_value'])) if dat['prepaid_value'] else "0.00"
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                   

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                # v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
                v['Stock_PIC'] = str(SITE_ROOT) + str(stock.Stock_PIC)
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                
#voucher stock listing
class VoucherStockViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            s_ids  = list(ItemStocklist.objects.filter(itemstocklist_status=True,
            itemsite_code=site.itemsite_code,item_code__startswith="4").values_list('item_code', flat=True).distinct())
           
            queryset = Stock.objects.filter(item_isactive=True,  item_div="4",
            item_code__in=s_ids).order_by('item_name')

            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), voucher_brand=True).first()
                    if not item_brand:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code,
                    item_code__in=s_ids).order_by('item_name')

                # else:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            if request.GET.get('Item_Rangeid',None):
                if not request.GET.get('Item_Rangeid',None) is None:
                    if request.GET.get('Item_Rangeid',None):
                        itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isvoucher=True,itm_status=True).first()
                        if not itemrange:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code,
                        item_code__in=s_ids).order_by('item_name')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code,
                        item_code__in=s_ids).order_by('item_name')
            
            if request.GET.get('search',None):
                if not request.GET.get('search',None) is None:
                    queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))


            # stock_lst = [i.pk for i in queryset if ItemStocklist.objects.filter(item_code=i.item_code,itemsite_code=site.itemsite_code,
            # itemstocklist_status=True).exists()]
           
            
            systemids = Systemsetup.objects.filter(title='stockOrderBy',
            value_name='stockOrderBy',isactive=True).first()

            if systemids and systemids.value_data == 'item_name':
                queryset = queryset.order_by('item_name') 
            elif systemids and systemids.value_data == 'item_seq':
                queryset = queryset.order_by('item_seq')
            elif systemids and systemids.value_data == 'item_desc':
                queryset = queryset.order_by('item_desc')
            elif systemids and systemids.value_data == 'item_code':
                queryset = queryset.order_by('item_code')
            else:
                queryset = queryset.order_by('item_name') 
 

            serializer_class =  StockSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            # v = result.get('data')
            # d = v.get("dataList")
            # for dat in d:
            #     dat["item_price"] = "{:.2f}".format(float(dat['item_price'])) if dat['item_price'] else "0.00"
            return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                  

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                # v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
                v['Stock_PIC'] = str(SITE_ROOT) + str(stock.Stock_PIC)
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                
#catalog search api
class CatalogSearchViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def get_queryset(self):
        q = self.request.GET.get('search',None)
        if q:
            query = Stock.objects.filter(item_isactive=True).exclude(item_div=2).order_by('item_name')
            queryset = query.filter(Q(item_name__icontains=q) | Q(item_desc__icontains=q) | Q(pinyin__icontains=q)).order_by('item_name')
            link_ids = ItemLink.objects.filter(link_code__icontains=q,itm_isactive=True).order_by('pk')
            p = [i.item_code[:-4] for i in link_ids if i.item_code]
            if p != []:
                squeryset = queryset.values_list('pk', flat=True).distinct().order_by('item_name')
                wqueryset = Stock.objects.filter(item_isactive=True,item_code__in=p).exclude(item_div=2).values_list('pk', flat=True).distinct().order_by('item_name')
                combined_list = list(chain(squeryset,wqueryset))
                queryset = Stock.objects.filter(pk__in=combined_list).order_by('-pk')
                return queryset
            else:
                return queryset
        else:
            queryset = Stock.objects.none()
        return queryset
                        
    def list(self, request, *args, **kwargs):
        try:
            qs = self.request.GET.get('search',None)
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            
            serializer_class = StockSerializer
            queryset = self.filter_queryset(self.get_queryset())

            stock_lst = [i.pk for i in queryset if ItemStocklist.objects.filter(item_code=i.item_code,itemsite_code=site.itemsite_code,
            itemstocklist_status=True).exists()]
           
            
            systemids = Systemsetup.objects.filter(title='stockOrderBy',
            value_name='stockOrderBy',isactive=True).first()

            if systemids and systemids.value_data == 'item_name':
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_name') 
            elif systemids and systemids.value_data == 'item_seq':
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_seq')
            elif systemids and systemids.value_data == 'item_desc':
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_desc')
            elif systemids and systemids.value_data == 'item_code':
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_code')
            else:
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_name') 
  

            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
           
            v = result.get('data')
            d = v.get("dataList")
            lst = []
            for dat in d:
                q = dict(dat)
                
                uomlst = []
                stock = Stock.objects.filter(item_isactive=True, pk=q['id']).first()
                q["item_price"] = "{:.2f}".format(float(q['item_price'])) if q['item_price'] else "0.00"
                q["prepaid_value"] = "{:.2f}".format(float(q['prepaid_value'])) if q['prepaid_value'] else "0.00"
                
                if stock and stock.item_div and int(stock.item_div) == 1:
                    itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code).order_by('id')
                    # print(itemuomprice,"itemuomprice")
                    for i in itemuomprice:
                        itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=i.item_uom).order_by('id').first()
                        if itemuom:
                            itemuom_id = int(itemuom.id)
                            itemuom_desc = itemuom.uom_desc

                            batch = ItemBatch.objects.filter(item_code=stock.item_code,site_code=site.itemsite_code,
                            uom=itemuom.uom_code).order_by('-pk').last()
                            # print(batch,"batch")

                            uom = {
                                    "itemuomprice_id": int(i.id),
                                    "item_uom": i.item_uom,
                                    "uom_desc": i.uom_desc,
                                    "item_price": "{:.2f}".format(float(i.item_price)),
                                    "itemuom_id": itemuom_id, 
                                    "itemuom_desc" : itemuom_desc,
                                    "onhand_qty": int(batch.qty) if batch else 0
                                    }
                            uomlst.append(uom)

                    val = {'uomprice': uomlst}  
                    q.update(val) 

                    if uomlst !=[]:
                        lst.append(q)
                else:
                    lst.append(q)

            v['dataList'] = lst
            # print(lst,"lst")
            n_lst = []
            if lst == []:
                batchso_ids = ItemBatchSno.objects.filter(batch_sno__icontains=qs,
                availability=True,site_code=site.itemsite_code)
                if batchso_ids:
                    for b in batchso_ids:
                        a = b.item_code
                        v = a[-4:]
                        # print(v,type(v),"v")
                        if v == '0000':
                            code = str(b.item_code)[:-4]
                        else:
                            code = str(b.item_code)    
                        
                        stockobj = Stock.objects.filter(item_isactive=True, item_code=code).first()
                        if stockobj:
                            serializer = StockSerializer(stockobj, context={'request': self.request})
                            # print(serializer.data,"serializer.data")
                            itemuomprice_obj = ItemUomprice.objects.filter(isactive=True, 
                            item_code=code,item_uom=b.uom).order_by('id').first()
                            if itemuomprice_obj:
                                itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=b.uom).order_by('id').first()
                                if itemuom:
                                    itemuom_id = int(itemuom.id)
                                    itemuom_desc = itemuom.uom_desc

                                    batch = ItemBatch.objects.filter(item_code=code,site_code=site.itemsite_code,
                                    uom=itemuom.uom_code).order_by('-pk').last()
                                    # print(batch,"batch")
                                    da = serializer.data 
                                    uom = {
                                        "itemuomprice_id": int(itemuomprice_obj.id),
                                        "item_uom": itemuomprice_obj.item_uom,
                                        "uom_desc": itemuomprice_obj.uom_desc,
                                        "item_price": "{:.2f}".format(float(itemuomprice_obj.item_price)),
                                        "itemuom_id": itemuom_id, 
                                        "itemuom_desc" : itemuom_desc,
                                        "onhand_qty": int(batch.qty) if batch else 0,
                                        "serial_no": b.batch_sno
                                        }
                                    da.update({'uomprice': [uom]}) 
                                    n_lst.append(da)
            
            if n_lst != []:
                limit = request.GET.get('limit',12)
                page= request.GET.get('page',1)
                paginator = Paginator(n_lst, limit)
                total = len(n_lst)

                total_page = 1

                if len(n_lst) > int(limit):
                    total_page = math.ceil(len(n_lst)/int(limit))

                if int(page) > total_page:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Content",'error': False, 
                    'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                    "total_pages":total_page}}, 
                    'dataList': []}}


                try:
                    queryset_data = paginator.page(page)
                except PageNotAnInteger:
                    queryset_data = paginator.page(1)
                    page= 1 
                except EmptyPage:
                    queryset_data = paginator.page(paginator.num_pages)    

                data_final = queryset_data.object_list

               
                result = {"status": status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                "data": {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                "total_pages":total_page}}, "dataList": data_final}}
            

            return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                           

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                # v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
                v['Stock_PIC'] = str(SITE_ROOT) + str(stock.Stock_PIC)
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                

class CatalogFavoritesViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def get_queryset(self):
        today = timezone.now().date()
        month = today.month
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        daud_ids = PosDaud.objects.filter(ItemSite_Codeid__pk=site.pk,created_at__date__month=month,
        dt_qty__gt = 0,dt_status='SA').only('itemsite_code','created_at','dt_qty','dt_status').order_by('-pk')
        pro_lst = []
        for d in daud_ids:
            daudids = PosDaud.objects.filter(ItemSite_Codeid__pk=site.pk,created_at__date__month=month,
            dt_itemnoid=d.dt_itemnoid,dt_qty__gt = 0,dt_status='SA').only('itemsite_code','created_at','dt_itemnoid','dt_qty','dt_status').aggregate(Sum('dt_qty'))
            qdaudids = PosDaud.objects.filter(ItemSite_Codeid__pk=site.pk,created_at__date__month=month,
            dt_itemnoid=d.dt_itemnoid,dt_qty__gt = 0,dt_status='SA').only('itemsite_code','created_at','dt_itemnoid','dt_qty','dt_status').order_by('-pk')[:1]
           
            #client qty > 10 need to change later
            if float(daudids['dt_qty__sum']) > 1:
                if d.dt_itemnoid.pk not in pro_lst:
                    pro_lst.append(d.dt_itemnoid.pk)
        
        if pro_lst != []:
            queryset = Stock.objects.filter(pk__in=pro_lst,item_isactive=True).order_by('pk')
        else:
            queryset = Stock.objects.none()
        return queryset
                        
    def list(self, request, *args, **kwargs):
        try:
            fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = StockSerializer
            queryset = self.filter_queryset(self.get_queryset())
            
            stock_lst = [i.pk for i in queryset if ItemStocklist.objects.filter(item_code=i.item_code,itemsite_code=site.itemsite_code,
            itemstocklist_status=True).exists()]
           
            
            systemids = Systemsetup.objects.filter(title='stockOrderBy',
            value_name='stockOrderBy',isactive=True).first()

            if systemids and systemids.value_data == 'item_name':
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_name') 
            elif systemids and systemids.value_data == 'item_seq':
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_seq')
            elif systemids and systemids.value_data == 'item_desc':
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_desc')
            elif systemids and systemids.value_data == 'item_code':
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_code')
            else:
                queryset = Stock.objects.filter(pk__in=stock_lst).order_by('item_name') 
 

            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            
            v = result.get('data')
            d = v.get("dataList")
            lst = []
            for dat in d:
                q = dict(dat)
                
                uomlst = []
                stock = Stock.objects.filter(item_isactive=True, pk=q['id']).first()
                q["item_price"] = "{:.2f}".format(float(q['item_price'])) if q['item_price'] else "0.00"
                q["prepaid_value"] = "{:.2f}".format(float(q['prepaid_value'])) if q['prepaid_value'] else "0.00"
                
                if stock and stock.item_div and int(stock.item_div) == 1:
                    itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code).order_by('id')
                    # print(itemuomprice,"itemuomprice")
                    for i in itemuomprice:
                        itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=i.item_uom).order_by('id').first()
                        if itemuom:
                            itemuom_id = int(itemuom.id)
                            itemuom_desc = itemuom.uom_desc

                            batch = ItemBatch.objects.filter(item_code=stock.item_code,site_code=site.itemsite_code,
                            uom=itemuom.uom_code).order_by('-pk').last()
                            # print(batch,"batch")

                            uom = {
                                    "itemuomprice_id": int(i.id),
                                    "item_uom": i.item_uom,
                                    "uom_desc": i.uom_desc,
                                    "item_price": "{:.2f}".format(float(i.item_price)),
                                    "itemuom_id": itemuom_id, 
                                    "itemuom_desc" : itemuom_desc,
                                    "onhand_qty": int(batch.qty) if batch else 0
                                    }
                            uomlst.append(uom)

                    val = {'uomprice': uomlst}  
                    q.update(val) 
                
                    if uomlst !=[]:
                        lst.append(q)
                else:
                    lst.append(q)

            v['dataList'] = lst    
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                            

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                # v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
                v['Stock_PIC'] = str(SITE_ROOT) + str(stock.Stock_PIC)
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                

class SalonProductSearchViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def get_queryset(self):
        q = self.request.GET.get('search',None)
        if q is not None:
            itm_div = ItemDiv.objects.filter(itm_isactive=True, itm_code=2, itm_desc="SALON PRODUCT").first()
            queryset = Stock.objects.filter(item_isactive=True, Item_Divid=itm_div).filter(Q(item_name__icontains=q) | Q(item_desc__icontains=q)).order_by('item_name')
        else:
            queryset = Stock.objects.none()
        return queryset
                        
    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            v = result.get('data')
            for i in v:
                i["item_price"] = "{:.2f}".format(float(i['item_price']))
            return Response(result, status=status.HTTP_200_OK)     
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                       

class ForgotPswdRequestOtpAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = OtpRequestSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            request_data = serializer.validated_data
            emp_name = request_data['emp_name']
            employee = Employee.objects.get(emp_name=emp_name)
            fmspw = Fmspw.objects.get(Emp_Codeid=employee, pw_isactive=True)
            setup = Systemsetup.objects.get(title = 'smsmode')
            if setup.value_data == 'twilio':
                if fmspw and employee:
                    totp = pyotp.TOTP(SMS_SECRET_KEY)
                    otp = totp.now()   
                    employee.otp = otp
                    employee.save()
                    client = Client(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)
                    receiver = employee.emp_phone2
                    #receiver = "9629002963"
                    message = client.messages.create(
                            body='Your change password request otp is {}'.format(otp),
                            from_=SMS_SENDER,
                            to=receiver
                        )
                    result = {'status': status.HTTP_200_OK, "message": "OTP Sended Successfully", 'error': False}
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed to send OTP", 'error': False}
            if setup.value_data == 'table':
                if fmspw and employee:
                    totp = pyotp.TOTP(SMS_SECRET_KEY)
                    otp = totp.now()   
                    receiver = employee.emp_phone1
                    body ='Your change password request otp is {}'.format(otp)
                    sms_process = SmsProcessLog(sms_phone = receiver,sms_datetime = datetime.datetime.now(), sms_msg = body,site_code =fmspw.loginsite,vendor_type = 4 ,isactive = 1,sms_task_number = 1,sms_portno = 0,sms_sendername = fmspw.pw_userlogin,sms_campaignname='Forget Password',sms_type= 'Immediately')
                    sms_process.save()
                    #
                    result = {'status': status.HTTP_200_OK, "message": "OTP Sended Successfully", 'error': False}

                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed to send OTP", 'error': False}
            
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed to send OTP", 'error': False}
            
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)                


class ForgotPswdOtpValidationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = OtpValidationSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            request_data = serializer.validated_data
            emp_name = self.request.GET.get('emp_name',None)
            otp = request_data['otp']
            employee = Employee.objects.get(emp_name=emp_name)
            fmspw = Fmspw.objects.get(Emp_Codeid=employee, pw_isactive=True)
            if fmspw and employee and employee.otp == otp:
                result = {'status': status.HTTP_200_OK, "message": "OTP Verified Successfully", 'error': False}
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed...! Please enter a valid OTP", 'error': False}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            request_data = serializer.validated_data
            emp_name = self.request.GET.get('emp_name',None)
            new_password = request_data['new_password']
            employee = Employee.objects.get(emp_name=emp_name)
            fmspw = Fmspw.objects.get(Emp_Codeid=employee, pw_isactive=True)
            user = User.objects.get(username=emp_name)
            if fmspw and employee and user:
                fmspw.pw_password = new_password
                fmspw.save()
                user.set_password(new_password)
                user.save()
                employee.pw_password = new_password
                employee.save()
                result = {'status': status.HTTP_200_OK, "message": "Password Changed Successfully", 'error': False}
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "Failed to change Password", 'error': False}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


# class UpdateStockAPIView(APIView):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]
#     queryset = Stock.objects.filter().order_by('-pk')
#     serializer_class = StockSerializer

#     def post(self, request):
#         queryset = Stock.objects.filter().order_by('-pk')
#         for s in queryset:
#             print(s.pk,"PK")
#             divobj = ItemDiv.objects.filter(itm_code=s.item_div).first()
#             deptobj = ItemDept.objects.filter(itm_code=s.item_dept).first()
#             classobj = ItemClass.objects.filter(itm_code=s.item_class).first()
#             rangeobj = ItemRange.objects.filter(itm_code=s.item_range).first()
#             typeobj = ItemType.objects.filter(itm_name=s.item_type).first()
#             Stock.objects.filter(pk=s.pk).update(Item_Divid=divobj,Item_Deptid=deptobj,Item_Classid=classobj,Item_Rangeid=rangeobj,Item_Typeid=typeobj) 
#             print(s.Item_Divid,s.Item_Deptid,s.Item_Classid,s.Item_Rangeid,s.Item_Typeid,"kkk")
#         return True


class ReceiptPdfSendSMSAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def post(self, request, format=None):
        try:
            if request.GET.get('sa_transacno',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sa_transacno!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            sa_transacno = request.GET.get('sa_transacno',None)
            hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,
            ItemSite_Codeid__pk=site.pk).order_by("-pk")
            if not hdr:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sa Transacno Does not exist in Poshaud!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

            pdf_link = GeneratePDF(self,request, sa_transacno)
            if not pdf_link:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Pdf link not generated",'error': True}
                return Response(data=result, status=status.HTTP_200_OK)      

            if not hdr[0].sa_custnoid.cust_phone2:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer mobile number!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
            
            smpt_ids = SmtpSettings.objects.filter(site_code=site.itemsite_code).order_by('pk').first()
            if not smpt_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"SmtpSettings does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
            

            allow_sms = hdr[0].sa_custnoid.custallowsendsms
            if allow_sms:
                cust_name = hdr[0].sa_custnoid.cust_name
                client = Client(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)
                receiver = hdr[0].sa_custnoid.cust_phone2
                try:
                    message = client.messages.create(
                            body= smpt_ids.sms_content.format(cust_name,sa_transacno,pdf_link),
                            from_=SMS_SENDER,
                            to=receiver
                        )

                    result = {'status': status.HTTP_200_OK,"message":"SMS sent succesfully",'error': False}
                except Exception as e:
                    invalid_message = str(e)
                    return general_error_response(invalid_message)
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "Customer doesn't wish to send SMS", 'error': False}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


class CustomerSignatureAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CustomerSignSerializer

    def post(self, request):
        try:
            cust_code = self.request.GET.get('cust_code',None)
            cust_obj = Customer.objects.filter(cust_code=cust_code,cust_isactive=True)
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer code!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            request_data = serializer.validated_data
            
            customer = Customer.objects.get(cust_code=cust_code,cust_isactive=True)
            customersign = request_data['customersign']
            
            if customer and customersign is not None:
                customer.customersign = bytes(customersign, encoding='utf8')
                customer.save()
                result = {'status': status.HTTP_200_OK, "message": "Customer Signature updated Successfully", 'error': False}
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "Failed to update customer signature", 'error': False}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 

class TopupCombinedViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:   
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite  
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 
            
            type_id = self.request.GET.get('type',None)
            if not type_id:
                result = {'status': status.HTTP_200_OK,"message":"Please give type!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 
            
            system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()

            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Topup',
            value_name='Other Outlet Customer Topup',isactive=True).first()
           
                
            
            tsum = 0; tlst = []
            tqueryset = TreatmentAccount.objects.filter(Cust_Codeid=cust_id, type='Deposit',sa_status='SA', outstanding__gt = 0).order_by('pk')
            header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
            "topup_amount" : "0.00","new_outstanding" : "0.00"}
            if tqueryset:
                for q in tqueryset:
                    ser_splt = str(q.description).split(":")
                    # print(ser_splt,"ser_splt")
                    #acc_ids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                    #treatment_parentcode=q.treatment_parentcode,Site_Codeid=site).order_by('id').last()
                    tacc_ids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                    treatment_parentcode=q.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                    tacc = TreatmentAccount.objects.filter(pk=tacc_ids.pk)
                    tserializer = TreatmentAccountSerializer(tacc, many=True)

                    if tacc_ids.outstanding > 0.0:
                        multistaff_ids = list(set(Multistaff.objects.filter(sa_transacno=q.sa_transacno,dt_lineno=q.dt_lineno).values_list('emp_code', flat=True).distinct()))
                        # print(multistaff_ids,"multistaff_ids")
                        emp_ids = Employee.objects.filter(emp_code__in=multistaff_ids).order_by('-pk')
                        # print(emp_ids,"emp_ids") 
                        daud_l = PosDaud.objects.filter(sa_transacno=q.sa_transacno,dt_lineno=q.dt_lineno).order_by('pk').first()
                        

                        open_trmids = Treatment.objects.filter(cust_code=cust_obj.cust_code,treatment_parentcode=q.treatment_parentcode,
                        sa_transacno=tacc_ids.ref_transacno,status='Open').count()
                        

                        for data in tserializer.data:
                            tpos_haud = PosHaud.objects.none()
                            if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                                if tacc_ids.site_code != site.itemsite_code or tacc_ids.site_code == site.itemsite_code:
                                    tpos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,
                                    sa_transacno=q.sa_transacno).first()
                            
                            else:
                                if tacc_ids.site_code == site.itemsite_code: 
                                    tpos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                                    sa_transacno=q.sa_transacno).first()
                            

                            if tpos_haud:
                                tsum += data['outstanding']
                                if tpos_haud.sa_date:
                                    splt = str(tpos_haud.sa_date).split(" ")
                                    data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                                
                                data['TreatmentAccountid'] = q.pk
                                data["pay_amount"] = None
                                # data['qty'] = open_trmids
                                data['qty'] = q.qty
                                # data["total_amount"] = "{:.2f}".format(float(daud_l.dt_amt)) if daud_l and daud_l.dt_amt else "0.00"
                                data["total_amount"] = ser_splt[1]
                                if data['sa_transacno']:
                                    data['sa_transacno'] = tpos_haud.sa_transacno_ref if tpos_haud.sa_transacno_ref else "" 
                                # if data['treatment_parentcode']:
                                #     data['treatment_parentcode'] = q.treatment_parentcode     
                                if data["description"]:
                                    trmt = Treatment.objects.filter(treatment_account=q.pk).last()
                                    if trmt:
                                        data["description"] = trmt.course  
                                        data['stock_id'] = trmt.Item_Codeid.pk
                                if data["balance"]:
                                    data["balance"] = "{:.2f}".format(float(data['balance']))
                                else:
                                    data["balance"] = "0.00"
                                if data["outstanding"]:
                                    data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                                else:
                                    data["outstanding"] = "0.00"
                                data['sa_staffname']  = ','.join([i.display_name for i in emp_ids if i.display_name]) if emp_ids else ""
                                data.update({'type':"Service"})        
                                tlst.append(data) 
            
            
            psum = 0; plst = []
            pqueryset = DepositAccount.objects.filter(Cust_Codeid=cust_id, type='Deposit', 
            outstanding__gt=0).order_by('pk')
            
            if pqueryset:
                for pq in pqueryset:
                    pro_splt = str(pq.description).split(":")
                    # print(pro_splt,"pro_splt")
                    # ,type__in=('Deposit', 'Top Up')

                    # pacc_ids = DepositAccount.objects.filter(ref_transacno=pq.sa_transacno,
                    # ref_productcode=pq.treat_code).order_by('-sa_date','-sa_time','-id').first()

                    pacc_ids = DepositAccount.objects.filter(sa_transacno=pq.sa_transacno,
                    treat_code=pq.treat_code).order_by('-sa_date','-sa_time','-id').first()
                   
                    
                    if pacc_ids:
                        pacc = DepositAccount.objects.filter(pk=pacc_ids.pk)
                        pserializer = TopupproductSerializer(pacc, many=True)
                        if pacc_ids.outstanding > 0.0:
                            dmultistaff_ids = list(set(Multistaff.objects.filter(sa_transacno=pq.sa_transacno,dt_lineno=pq.dt_lineno).values_list('emp_code', flat=True).distinct()))
                            # print(dmultistaff_ids,"dmultistaff_ids")
                            demp_ids = Employee.objects.filter(emp_code__in=dmultistaff_ids).order_by('-pk')
                            # print(demp_ids,"demp_ids") 
                            daud_li = PosDaud.objects.filter(sa_transacno=pq.sa_transacno,dt_lineno=pq.dt_lineno).order_by('pk').first()
                            for dat in pserializer.data:
                                ppos_haud = PosHaud.objects.none()
                                if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                                    if pacc_ids.site_code != site.itemsite_code or pacc_ids.site_code == site.itemsite_code:
                                        ppos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,
                                        sa_transacno=pq.sa_transacno).first()

                                else:
                                    if pacc_ids.site_code == site.itemsite_code: 
                                        ppos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                                        sa_transacno=pq.sa_transacno).first()

                               
                                if ppos_haud:
                                    psum += dat['outstanding']
                                    if ppos_haud.sa_date:
                                        prsplt = str(ppos_haud.sa_date).split(" ")
                                        dat['sa_date'] = datetime.datetime.strptime(str(prsplt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                                    
                                    dat['DepositAccountid'] = pq.pk
                                    dat["pay_amount"] = None
                                    dat['qty'] = pq.qty
                                    dat['sa_transacno'] = ppos_haud.sa_transacno_ref if ppos_haud.sa_transacno_ref else ""     
                                    dat['stock_id'] = pacc_ids.Item_Codeid.pk
                                    # dat["total_amount"] = "{:.2f}".format(float(daud_li.dt_amt)) if daud_li and daud_li.dt_amt else "0.00"
                                    dat["total_amount"] = pro_splt[1]
                                    if dat["balance"]:
                                        dat["balance"] = "{:.2f}".format(float(dat['balance']))
                                    else:
                                        dat["balance"] = "0.00"    
                                    if dat["outstanding"]:
                                        dat["outstanding"] = "{:.2f}".format(float(dat['outstanding']))
                                    else:
                                        dat["outstanding"] = "0.00" 
                                    dat['sa_staffname'] =  ','.join([i.display_name for i in demp_ids if i.display_name]) if demp_ids else ""
                                    dat.update({'type':"Product"})             
                                    plst.append(dat)    


            # queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno_type="Receipt",
            # ItemSite_Codeid__pk=site.pk)
            queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno_type="Receipt")
            prsum = 0; lst = []
           
            if queryset:
                for rq in queryset:
                    # daud = PosDaud.objects.filter(sa_transacno=rq.sa_transacno,
                    # ItemSite_Codeid__pk=site.pk)
                    daud = PosDaud.objects.filter(sa_transacno=rq.sa_transacno)
                    for d in daud:
                        pacc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,sa_status='DEPOSIT',
                        cust_code=cust_obj.cust_code,line_no=d.dt_lineno,outstanding__gt = 0)
                       
                        if pacc_ids:
                            # if int(d.dt_itemnoid.item_div) == 3 and d.dt_itemnoid.item_type == 'PACKAGE':
                            #     acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,package_code=d.dt_combocode,
                            #     line_no=d.dt_lineno,outstanding__gt = 0,status=True).order_by('id').last()
                            # else:
                            #     acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,
                            #     line_no=d.dt_lineno,outstanding__gt = 0,status=True).order_by('id').last()
                            
                            acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,
                            line_no=d.dt_lineno,outstanding__gt = 0,status=True).order_by('id').last()
                            
                            
                            if acc_ids:
                                acc = PrepaidAccount.objects.filter(pk=acc_ids.pk)
                                serializer = TopupprepaidSerializer(acc, many=True)
                                pmultistaff_ids = list(set(Multistaff.objects.filter(sa_transacno=d.sa_transacno,dt_lineno=d.dt_lineno).values_list('emp_code', flat=True).distinct()))
                                # print(pmultistaff_ids,"pmultistaff_ids")
                                pemp_ids = Employee.objects.filter(emp_code__in=pmultistaff_ids).order_by('-pk')
                                # print(pemp_ids,"pemp_ids") 
                        
                                for pdata in serializer.data:
                                    pos_haud = PosHaud.objects.none()
                                    if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                                        if acc_ids.site_code != site.itemsite_code or acc_ids.site_code == site.itemsite_code:
                                            pos_haud = PosHaud.objects.filter(sa_custnoid=cust_obj,
                                            sa_transacno_type="Receipt",sa_transacno=rq.sa_transacno).first()
                               
                                    else:
                                        if acc_ids.site_code == site.itemsite_code: 
                                            pos_haud = PosHaud.objects.filter(sa_custnoid=cust_obj,ItemSite_Codeid__pk=site.pk,
                                            sa_transacno_type="Receipt",sa_transacno=rq.sa_transacno).first()
                               
                                    
                                    if pos_haud:
                                        prsum += pdata['outstanding']
                                        if pos_haud.sa_date:
                                            presplt = str(pos_haud.sa_date).split(" ")
                                            pdata['sa_date'] = datetime.datetime.strptime(str(presplt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                                    
                                        # psplt = str(pdata['exp_date']).split('T')
                                        # if pdata['exp_date']:
                                        #     pdata['exp_date'] = datetime.datetime.strptime(str(psplt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                                        
                                        pdata['qty'] = 1
                                        pdata['sa_transacno'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                                        pdata['prepaid_id']  = acc_ids.pk

                                        if int(d.dt_itemnoid.item_div) == 3 and d.dt_itemnoid.item_type == 'PACKAGE':
                                            pdata['stock_id'] = pacc_ids[0].Item_Codeid.pk
                                        else:
                                            pdata['stock_id'] = d.dt_itemnoid.pk

                                        pdata["pay_amount"] = None
                                        pdata["total_amount"] = "{:.2f}".format(float(acc_ids.pp_total)) if acc_ids.pp_total else "0.00"
                                        if pdata["remain"]:
                                            pdata["balance"] = "{:.2f}".format(float(pdata['remain']))
                                        if pdata["outstanding"]:
                                            pdata["outstanding"] = "{:.2f}".format(float(pdata['outstanding']))
                                        pdata['sa_staffname'] = ','.join([i.display_name for i in pemp_ids if i.display_name]) if pemp_ids else ""
                                        pdata.update({'type':"Prepaid"})             
                                        lst.append(pdata) 
            
            # print(len(tlst),"tlst")
            # print(len(plst),"plst")
            # print(len(lst),"lst")
            data_type = type_id.split(",")   
            # print(tsum,psum,prsum)                        
            total_sum = 0; final = []
            if 'service' in data_type:
                final = tlst
                total_sum += tsum
            if 'product' in data_type:
                final += plst 
                total_sum += psum 
            if 'prepaid' in data_type:
                final += lst
                total_sum += prsum
            if 'all' in data_type:
                final = tlst + plst + lst
                total_sum += tsum + psum + prsum 


            if final != []:
                limit = request.GET.get('limit',12)
                page= request.GET.get('page',1)
                paginator = Paginator(final, limit)
                total = len(final)

                total_page = 1

                if len(final) > int(limit):
                    total_page = math.ceil(len(final)/int(limit))

                if int(page) > total_page:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Content",'error': False, 
                    'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                    "total_pages":total_page}}, 
                    'dataList': []}}


                try:
                    queryset_data = paginator.page(page)
                except PageNotAnInteger:
                    queryset_data = paginator.page(1)
                    page= 1 
                except EmptyPage:
                    queryset_data = paginator.page(paginator.num_pages)    

                data_final = queryset_data.object_list

                header_data = {"customer_name" : cust_obj.cust_name,"cust_refer" : cust_obj.cust_refer if cust_obj.cust_refer else "",
                "old_outstanding" : "{:.2f}".format(float(total_sum)),
                "topup_amount" : None,"new_outstanding" : "{:.2f}".format(float(total_sum))}

                result = {"status": status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,
                "header_data":header_data, 
                "data": {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                "total_pages":total_page}}, "dataList": data_final}}
            
                return Response(result, status=status.HTTP_200_OK) 
            else:
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,'header_data':header_data,  'data': []}
                return Response(result, status=status.HTTP_200_OK)        
                 
               
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 
           

class TopupViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentAccountSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  
    
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            if not self.request.user.is_authenticated:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            if not fmspw:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            site = fmspw[0].loginsite
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()

            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Topup',
            value_name='Other Outlet Customer Topup',isactive=True).first()
           
                
                
            #queryset = TreatmentAccount.objects.filter(Cust_Codeid=cust_id, Site_Codeid=site, type='Deposit', outstanding__gt = 0).order_by('pk')
            queryset = TreatmentAccount.objects.filter(Cust_Codeid=cust_id, type='Deposit',sa_status='SA', outstanding__gt = 0).order_by('pk')
            sum = 0; lst = []
            header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
            "topup_amount" : "0.00","new_outstanding" : "0.00"}
            if queryset:
                for q in queryset:
                    #type__in=('Deposit', 'Top Up')
                    # accids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                    # treatment_parentcode=q.treatment_parentcode,Site_Codeid=site).order_by('id').first()
                    # trmtobj = Treatment.objects.filter(treatment_account__pk=accids.pk,status='Open').order_by('pk').first()

                    #acc_ids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                    #treatment_parentcode=q.treatment_parentcode,Site_Codeid=site).order_by('id').last()
                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                    treatment_parentcode=q.treatment_parentcode).order_by('sa_date','sa_time','id').last()
                    acc = TreatmentAccount.objects.filter(pk=acc_ids.pk)
                    serializer = self.get_serializer(acc, many=True)

                    if acc_ids and acc_ids.outstanding > 0.0:
                        for data in serializer.data:
                            pos_haud = PosHaud.objects.none()
                            if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                                if acc_ids.site_code != site.itemsite_code or acc_ids.site_code == site.itemsite_code:
                                    pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,
                                    sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                            else:
                                if acc_ids.site_code == site.itemsite_code: 
                                    pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                                    sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()

                                
                            if pos_haud:
                                sum += data['outstanding']
                                if pos_haud.sa_date:
                                    splt = str(pos_haud.sa_date).split(" ")
                                    data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                                
                                data['TreatmentAccountid'] = q.pk
                                data["pay_amount"] = None
                                if data['sa_transacno']:
                                    data['sa_transacno'] = pos_haud.sa_transacno_ref 
                                if data['treatment_parentcode']:
                                    data['treatment_parentcode'] = q.treatment_parentcode     
                                if data["description"]:
                                    trmt = Treatment.objects.filter(treatment_account=q.pk).last()
                                    if trmt:
                                        data["description"] = trmt.course  
                                        data['stock_id'] = trmt.Item_Codeid.pk
                                if data["balance"]:
                                    data["balance"] = "{:.2f}".format(float(data['balance']))
                                else:
                                    data["balance"] = "0.00"
                                if data["outstanding"]:
                                    data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                                else:
                                    data["outstanding"] = "0.00"    
                                lst.append(data) 
                                
                if lst != []:
                    header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "{:.2f}".format(float(sum)),
                    "topup_amount" : None,"new_outstanding" : "{:.2f}".format(float(sum))}
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,'header_data':header_data,  'data': []}
                    return Response(result, status=status.HTTP_200_OK)        
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)           

        
    # def get_object(self, pk):
    #     try:
    #         return TreatmentAccount.objects.get(pk=pk)
    #     except TreatmentAccount.DoesNotExist:
    #         raise Http404

    # def retrieve(self, request, pk=None):
    #     topup = self.get_object(pk)
    #     serializer = TopupSerializer(topup)
    #     result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
    #     v = result.get('data')
    #     if v["description"]:
    #         description = Treatment.objects.filter(treatment_account=v["id"]).last()
    #         v["description"] = description.course
    #     if v["amount"]:
    #         v["amount"] = "{:.2f}".format(float(v['amount']))
    #     else:
    #         v["amount"] = "0.00"            
    #     if v["balance"]:
    #         v["balance"] = "{:.2f}".format(float(v['balance']))
    #     else:
    #         v["balance"] = "0.00"
    #     if v["outstanding"]:
    #         v["outstanding"] = "{:.2f}".format(float(v['outstanding']))
    #     else:
    #         v["outstanding"] = "0.00"    
    #     return Response(result, status=status.HTTP_200_OK)    


# class TreatmentDoneViewset(viewsets.ModelViewSet):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]
#     serializer_class = TreatmentDoneSerializer

#     @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
#     authentication_classes=[TokenAuthentication])
#     def Year(self, request):
#         try:
#             today = timezone.now()
#             year = today.year
#             res = [r for r in range(2010, today.year+1)]
#             res.append("All")
#             result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': res[::-1]}
#             return Response(result, status=status.HTTP_200_OK) 
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)       

#     def list(self, request):
#         try:
#             cust_id = self.request.GET.get('cust_id',None)
#             cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
#             if cust_obj is None:
#                 result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_200_OK)  

#             fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
#             if not self.request.user.is_authenticated:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
#             if not fmspw:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
#             site = fmspw[0].loginsite
#             if not site:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             # queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
#             # status="Open").order_by('pk')
#             queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open").order_by('pk')


#             if request.GET.get('year',None):
#                 year = request.GET.get('year',None)
#                 if year != "All":
#                     queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
#                     status="Open", treatment_date__year=year).order_by('pk')
#                     par_lst = list(set([e.treatment_parentcode for e in queryset if e.treatment_parentcode])) 
#                     id_lst = []
#                     for p in par_lst:
#                         query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code, site_code=site.itemsite_code,
#                         status="Open", treatment_date__year=year).order_by('pk').last()
#                         id_lst.append(query.pk) 

#                     queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,site_code=site.itemsite_code, status="Open", treatment_date__year=year).order_by('pk')
        
#             if queryset:
#                 serializer = self.get_serializer(queryset, many=True)
#                 lst = []
#                 for i in serializer.data:
#                     splt = str(i['treatment_date']).split('T')
#                     trmt_obj = Treatment.objects.filter(pk=i['id']).first()
#                     # tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj)
#                     # tmp_ids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code)
                    
#                     # for emp in tmp_ids:
#                     #     appt = Appointment.objects.filter(cust_no=trmt_obj.cust_code,appt_date=date.today(),
#                     #     itemsite_code=fmspw[0].loginsite.itemsite_code,emp_no=emp.helper_code) 
#                     #     if not appt:
#                     #         # tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj,helper_code=emp.helper_code,
#                     #         # site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                            
#                     #         tmpids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,helper_code=emp.helper_code,
#                     #         site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                            
#                     #         if tmpids:
#                     #             emp.delete()
                        
#                         #need to uncomment later
#                         # if emp.appt_fr_time and emp.appt_to_time:         
#                         #     appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
#                         #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
#                         #     if appt_ids:
#                         #         emp.delete()

#                     for existing in trmt_obj.helper_ids.all():
#                         trmt_obj.helper_ids.remove(existing) 
                    
#                     for t in TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code):
#                         trmt_obj.helper_ids.add(t)
#                     # for t in TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,site_code=site.itemsite_code):
#                     #     trmt_obj.helper_ids.add(t)

#                     # pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
#                     # sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()        
#                     pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,itemsite_code=site.itemsite_code,
#                     sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()
#                     # if not pos_haud:
#                     #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Payment not done yet!!",'error': True} 
#                     #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
#                     item_code = str(trmt_obj.item_code)
#                     itm_code = item_code[:-4]
#                     # print(Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk'),"sss")
#                     stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()
                    
#                     if pos_haud and stockobj: 
#                         acc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
#                         site_code=site.itemsite_code).order_by('pk').first()
#                         i['treatment_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
#                         # i['TreatmentAccountid'] = trmt_obj.treatment_account.pk
#                         i['TreatmentAccountid'] = acc_obj.pk
#                         # i['stockid'] = trmt_obj.Item_Codeid.pk if trmt_obj and trmt_obj.Item_Codeid.Item_Codeid else 0
#                         i['stockid'] = stockobj.pk if stockobj else 0
#                         i["transacno_ref"] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
#                         if i["unit_amount"]:
#                             i["unit_amount"] = "{:.2f}".format(float(i['unit_amount']))
#                         i["rev"] = False
#                         i["limit"] = None
#                         if trmt_obj.helper_ids.all().exists():
#                             i["sel"] = True 
#                             i["staff"] = ','.join([v.helper_id.display_name for v in trmt_obj.helper_ids.all() if v.helper_id.display_name])
#                         else:    
#                             i["sel"] = None 
#                             i["staff"] = None

#                         i['is_reversal'] = fmspw[0].is_reversal   
#                         lst.append(i)
#                 result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': lst}
#                 return Response(data=result, status=status.HTTP_200_OK)  
#             else:
#                 result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
#                 return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)        


# class TreatmentDoneViewset(viewsets.ModelViewSet):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]
#     serializer_class = TreatmentDoneSerializer

#     @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
#     authentication_classes=[ExpiringTokenAuthentication])
#     def Year(self, request):
#         try:
#             today = timezone.now()
#             year = today.year
#             res = [r for r in range(2010, today.year+1)]
#             res.append("All")
#             result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': res[::-1]}
#             return Response(result, status=status.HTTP_200_OK) 
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)       

#     def list(self, request):
#         try:
#             cust_id = self.request.GET.get('cust_id',None)
#             cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
#             if cust_obj is None:
#                 result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_200_OK)  

#             fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
#             if not self.request.user.is_authenticated:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
#             if not fmspw:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
#             site = fmspw[0].loginsite
#             if not site:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             # check = False
#             system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
#             value_name='Other Outlet Customer Listings',isactive=True).first()

#             system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Reversal',
#             value_name='Other Outlet Customer Reversal',isactive=True).first()
#             # if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
#             #     if cust_obj.site_code != site.itemsite_code or cust_obj.site_code == site.itemsite_code:
#             #         check = True
#             # else:
#             #     if cust_obj.site_code == site.itemsite_code:
#             #         check = True    
            
#             # queryset = Treatment.objects.none()

#             # if check == True:
#             # queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
#             # status="Open").order_by('pk')
#             queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open").order_by('pk')


#             if request.GET.get('year',None):
#                 year = request.GET.get('year',None)
#                 if year != "All":
#                     # queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
#                     # status="Open", treatment_date__year=year).order_by('pk')
#                     queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open", treatment_date__year=year).order_by('pk')
#                     par_lst = list(set([e.treatment_parentcode for e in queryset if e.treatment_parentcode])) 
#                     id_lst = []
#                     for p in par_lst:
#                         # query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code, site_code=site.itemsite_code,
#                         # status="Open", treatment_date__year=year).order_by('pk').last()
#                         query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code,
#                         status="Open", treatment_date__year=year).order_by('pk').last()
                    
#                         id_lst.append(query.pk) 

#                     # queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,site_code=site.itemsite_code, status="Open", treatment_date__year=year).order_by('pk')
#                     queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,status="Open", treatment_date__year=year).order_by('pk')
            
#             if queryset:
#                 serializer = self.get_serializer(queryset, many=True)
#                 lst = []
#                 for i in serializer.data:
#                     session = 0
#                     treatmentids=[]
#                     splt = str(i['treatment_date']).split('T')
#                     trmt_obj = Treatment.objects.filter(pk=i['id']).first()
#                     # tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj)
#                     tmp_ids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code)
#                     #reverseorder = True
#                     #trmtparobj1 = Treatment.objects.filter(treatment_parentcode=i['treatment_parentcode'],status="Open").only('pk').order_by('-pk').first
#                     #if trmtparobj1:
#                     #    print(trmtparobj1.times,"trmtparobj1.times")
#                     #    if trmtparobj1.times > 1:
#                     #        reverseorder = True:
#                     trmtparobj = Treatment.objects.filter(treatment_parentcode=i['treatment_parentcode'],status="Open").only('pk').order_by('pk')
#                     for oneids in trmtparobj:
#                         treatmentids.append(oneids.pk)

#                         TmpItemHelper.objects.filter(treatment=oneids,created_at__date__lt=date.today(),line_no__isnull=True).delete()

#                         if trmt_obj.helper_ids.all().exists():
#                             if oneids.helper_ids.all().exists():
#                                 session += 1
#                         else:
#                             for existing in oneids.helper_ids.all():
#                                 existing.delete()
                            

#                     # for emp in tmp_ids:
#                     #     appt = Appointment.objects.filter(cust_no=trmt_obj.cust_code,appt_date=date.today(),
#                     #     itemsite_code=fmspw[0].loginsite.itemsite_code,emp_no=emp.helper_code) 
#                     #     if not appt:
#                     #         # tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj,helper_code=emp.helper_code,
#                     #         # site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                            
#                     #         tmpids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,helper_code=emp.helper_code,
#                     #         site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                            
#                     #         if tmpids:
#                     #             emp.delete()
                        
#                         #need to uncomment later
#                         # if emp.appt_fr_time and emp.appt_to_time:         
#                         #     appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
#                         #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
#                         #     if appt_ids:
#                         #         emp.delete()

#                     for existing in trmt_obj.helper_ids.all():
#                         trmt_obj.helper_ids.remove(existing) 
                    
#                     #for t in TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code):
#                     #    trmt_obj.helper_ids.add(t)
#                     for t in TmpItemHelper.objects.filter(treatment=trmt_obj):
#                         trmt_obj.helper_ids.add(t)

#                     # for t in TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,site_code=site.itemsite_code):
#                     #     trmt_obj.helper_ids.add(t)

#                     # pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
#                     # sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()        
#                     # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,itemsite_code=site.itemsite_code,
#                     # sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()
#                     pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
#                     sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()
#                     # if not pos_haud:
#                     #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Payment not done yet!!",'error': True} 
#                     #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
#                     item_code = str(trmt_obj.item_code)
#                     if len(item_code) > 8:
#                         itm_code = item_code[:-4]
#                     else:
#                         itm_code = item_code

#                     #itm_code = item_code[:-4]
#                     # print(Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk'),"sss")
#                     stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()
                    
#                     if pos_haud and stockobj: 
#                         # acc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
#                         # site_code=site.itemsite_code).order_by('pk').first()
#                         # trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=i['treatment_parentcode']).order_by('-id').first()
#                         trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=i['treatment_parentcode']).order_by('sa_date','sa_time','id').last()
#                         if trmtAccObj:
#                             i["balance"] = "{:.2f}".format(float(trmtAccObj.balance)) if trmtAccObj.balance else "0.00"
#                             i["ar"] = "{:.2f}".format(float(trmtAccObj.outstanding)) if trmtAccObj.outstanding else "0.00"
#                         acc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode).order_by('pk').first()
#                         i['treatment_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
#                         # i['TreatmentAccountid'] = trmt_obj.treatment_account.pk
#                         i['TreatmentAccountid'] = acc_obj.pk
#                         # i['stockid'] = trmt_obj.Item_Codeid.pk
#                         i['stockid'] = stockobj.pk if stockobj else ""
#                         i["transacno_ref"] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
#                         if i["unit_amount"]:
#                             i["unit_amount"] = "{:.2f}".format(float(i['unit_amount'])) if i['unit_amount'] else ""
#                         # i["rev"] = False
#                         #i["td"] = i["times"] + "/" +  i["treatment_no"]
#                         i["td"] = str(len(treatmentids)) + "/" +  i["treatment_no"]
#                         i["rev"] = "0/" +  i["treatment_no"]
#                         #i["open"] = i["times"]
#                         i["open"] = str(len(treatmentids))
#                         i["session"] = session
#                         i["session_flag"] = True
#                         if session == 0:
#                             i["session_flag"] = False

#                         i["exchange_flag"] = False
#                         if session == 1:
#                             i["exchange_flag"] = True    

#                         # Allow Reversal in other salons for Healspa. Set False for Midyson
#                         i["iscurrentloggedinsalon"] = ""
#                         if site.itemsite_code == acc_obj.site_code:
#                             i["iscurrentloggedinsalon"] = True
#                         elif site.itemsite_code != acc_obj.site_code:
#                             i["iscurrentloggedinsalon"] = False

                        
#                         i["limit"] = None
#                         i["treatmentids"] = treatmentids

#                         if trmt_obj.helper_ids.all().exists():
#                             i["sel"] = True 
#                             i["staff"] = ','.join([v.helper_id.display_name for v in trmt_obj.helper_ids.all() if v.helper_id.display_name])
#                         else:    
#                             i["sel"] = None 
#                             i["staff"] = None

#                         i['is_reversal'] = fmspw[0].is_reversal
#                         i['is_allow']  = False
#                         if trmt_obj:
#                             if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
#                                 if trmt_obj.site_code != site.itemsite_code or trmt_obj.site_code == site.itemsite_code:
#                                     i['is_allow'] = True
#                             else:
#                                 if trmt_obj.site_code == site.itemsite_code:
#                                     i['is_allow'] = True
                        
#                         lst.append(i)
#                 result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': lst,
#                 'cust_data': {'cust_name': cust_obj.cust_name if cust_obj.cust_name else "", 
#                 'cust_refer': cust_obj.cust_refer if cust_obj.cust_refer else ""}}
#                 return Response(data=result, status=status.HTTP_200_OK)  
#             else:
#                 result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 'data': [],
#                 'cust_data': {'cust_name': cust_obj.cust_name if cust_obj.cust_name else "", 
#                 'cust_refer': cust_obj.cust_refer if cust_obj.cust_refer else ""}}
#                 return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)    

class TreatmentDoneNewViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = TreatmentPackage.objects.filter().order_by('-pk')
    serializer_class = TreatmentPackageDoneListSerializer

    #old code by monica 
    # def list(self, request):
    #     try:
    #         now = timezone.now()
    #         print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
    #         fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
    #         site = fmspw[0].loginsite

    #         cust_id = self.request.GET.get('cust_id',None)
    #         cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
    #         if not cust_obj:
    #             result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
    #             return Response(data=result, status=status.HTTP_200_OK) 

    #         system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
    #         value_name='Other Outlet Customer Listings',isactive=True).first()

    #         system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Reversal',
    #         value_name='Other Outlet Customer Reversal',isactive=True).first()

    #         flexi_setup = Systemsetup.objects.filter(title='B21showServiceOnTreatmentForFlexi',
    #         value_name='B21showServiceOnTreatmentForFlexi',isactive=True).first()
    #         def_setup = Systemsetup.objects.filter(title='Default TD List Years Ago',
    #         value_name='Default TD List Years Ago',isactive=True).first()

    #         current_year = date.today().year
            
    #         queryset = TreatmentPackage.objects.none()

    #         if not request.GET.get('year',None):
    #             raise Exception('Please give year!!') 

    #         if request.GET.get('year',None):
    #             year = request.GET.get('year',None)
    #             if year == "Default":
    #                 if def_setup and def_setup.value_data: 
    #                     ylst = []
    #                     for i in range(0,int(def_setup.value_data)):
    #                         yr = current_year - i
    #                         if yr not in ylst:
    #                             ylst.append(yr)
                                
    #                     if ylst != []: 
    #                         queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
    #                         open_session__gt=0, treatment_date__year__in=ylst).order_by('-pk')

    #                 else:
    #                     raise Exception('Please Give Systemsetup year in Default TD List Years Ago!!')     
    #             elif year == "Expiry":
    #                 queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
    #                 open_session__gt=0,expiry_date__date__lt=date.today()).order_by('-pk')

    #             elif year == "All":
    #                 queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
    #                 open_session__gt=0).order_by('-pk')

    #         if queryset:
    #             full_tot = queryset.count()
    #             try:
    #                 limit = int(request.GET.get("limit",12))
    #             except:
    #                 limit = 12
    #             try:
    #                 page = int(request.GET.get("page",1))
    #             except:
    #                 page = 1

    #             paginator = Paginator(queryset, limit)
    #             total_page = paginator.num_pages

    #             try:
    #                 queryset = paginator.page(page)
    #                 # print(queryset,"queryset")
    #             except (EmptyPage, InvalidPage):
    #                 queryset = paginator.page(total_page) # last page
    #             data_list= []
    #             for row in queryset:
    #                 trmt_obj = row ;is_allow=False
    #                 session = 0; balance = "0.00"; ar= "0.00" 
    #                 done_ids = Treatment.objects.filter(treatment_parentcode=row.treatment_parentcode,status="Done").order_by('pk').count()
    #                 open_ids = Treatment.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,status="Open").only('pk').order_by('pk').count()
                    
    #                 last_ids = Treatment.objects.filter(treatment_parentcode=row.treatment_parentcode).order_by('-pk').first()

    #                 expiry = False; query = False;expiry_date = ""
    #                 if row.expiry_date:
    #                     splte = str(row.expiry_date).split(' ')
    #                     expiry = splte[0]
    #                     expiry_date = datetime.datetime.strptime(str(splte[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        
                    
    #                 treatment_limit_times = row.treatment_limit_times

    #                 # print(q_val[0],"vv")
    #                 if row.type == 'N':
    #                     query = row
    #                 elif row.type in ['FFd','FFi']:
    #                     if expiry and treatment_limit_times is not None:
    #                         if expiry >= str(date.today()):
    #                             if treatment_limit_times > done_ids or treatment_limit_times == 0:
    #                                 query = row
                    
    #                 if query:
    #                     search_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
    #                     created_at=date.today()).order_by('-pk').first()

    #                     iscurrentloggedinsalon = True if site.itemsite_code == trmt_obj.site_code else False 
    #                     trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=row.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
    #                     # print(trmtAccObj,"trmtAccObj")
    #                     if trmtAccObj:
    #                         balance = "{:.2f}".format(float(trmtAccObj.balance)) if trmtAccObj.balance else "0.00"
    #                         ar = "{:.2f}".format(float(trmtAccObj.outstanding)) if trmtAccObj.outstanding else "0.00"

    #                     if flexi_setup and flexi_setup.value_data == 'True' and row.type == 'FFi':
    #                         b21flexitype = True
    #                     else:
    #                         b21flexitype = False  

    #                     session =  search_ids.session if search_ids and search_ids.session else 0
                         
    #                     session_flag = False if session == 0 else True 
    #                     exchange_flag = True if session == 1 else False 
    
                        
    #                     if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
    #                         if trmt_obj.site_code != site.itemsite_code or trmt_obj.site_code == site.itemsite_code:
    #                             is_allow = True
    #                     else:
    #                         if trmt_obj.site_code == site.itemsite_code:
    #                             is_allow = True  

    #                     flexiservice_ids = ItemFlexiservice.objects.filter(item_code=str(trmt_obj.item_code),
    #                     itm_isactive=True)
    #                     if row.type == 'FFi' and flexiservice_ids:
    #                         itemflexiservice = True
    #                     else:
    #                         itemflexiservice = False
        
    #                     rev = "0"+"/"+last_ids.treatment_no
    #                     td = str(open_ids)+"/"+last_ids.treatment_no

    #                     if row.type in ['FFd','FFi'] and done_ids > 0:
    #                         reversal_check = False
    #                     else:
    #                         reversal_check = True
                        
                       
    #                     sel = True if search_ids else None  

    #                     splt = str(trmt_obj.treatment_date).split(' ')
    #                     treatment_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
    #                     unit_amount =  "{:.2f}".format(float(trmt_obj.unit_amount)) if trmt_obj.unit_amount else "0.00"

    #                     data_list.append({
    #                         "TreatmentAccountid": row.treatment_accountid.pk if row.treatment_accountid else "",
    #                         "balance": balance,
    #                         "ar": ar,
    #                         "b21flexitype": b21flexitype,
    #                         "course": row.course,
    #                         "done_sessioncnt": done_ids,
    #                         "session_flag": session_flag,
    #                         "exchange_flag" : exchange_flag,
    #                         "expiry_date" : expiry_date,
    #                         "is_allow" : is_allow,
    #                         "is_reversal" : fmspw[0].is_reversal,
    #                         "iscurrentloggedinsalon": iscurrentloggedinsalon,
    #                         "item_code" : str(trmt_obj.item_code),
    #                         "itemflexiservice" : itemflexiservice,
    #                         "open" : open_ids,
    #                         "rev": rev,
    #                         "td":td,
    #                         "reversal_check": reversal_check, 
    #                         "sel": sel,
    #                         "session" : session,
    #                         "site_code" :  trmt_obj.site_code,
    #                         "stockid" :  trmt_obj.Item_Codeid.pk if trmt_obj.Item_Codeid else "",
    #                         "transacno_ref": trmt_obj.sa_transacno_ref,
    #                         "treatment_code" : trmt_obj.treatment_parentcode,
    #                         "treatment_date" : treatment_date,
    #                         "treatment_limit_times": trmt_obj.treatment_limit_times,
    #                         "type" : trmt_obj.type,
    #                         "unit_amount" : unit_amount
    #                     })        
                    
               
    #             resData = {
    #                 'dataList': data_list,
    #                 'meta' : {'pagination': {
    #                        "per_page":limit,
    #                        "current_page":page,
    #                        "total":full_tot,
    #                        "total_pages":total_page
    #                 }},
                    
    #             }
    #             now1 = timezone.now()
    #             print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
    #             totalh = now1.second - now.second
    #             print(totalh,"total")
    #             result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",
    #             'error': False, 'data':  resData ,
    #             'cust_data': {'cust_name': cust_obj.cust_name if cust_obj.cust_name else "", 
    #             'cust_refer': cust_obj.cust_refer if cust_obj.cust_refer else ""}}
    #         else:
    #             serializer = self.get_serializer()
    #             result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
    #         return Response(data=result, status=status.HTTP_200_OK) 
    #     except Exception as e:
    #         invalid_message = str(e)
    #         return general_error_response(invalid_message)          
    
    # treatmentids = Treatment.objects.filter(cust_code=cust_obj.cust_code,
    # treatment_parentcode=trmt_obj.treatment_parentcode,status="Open").only('pk').order_by('pk').values_list('pk', flat=True).distinct()
    # print(treatmentids,"treatmentids")
    # if row.type == 'N':
    #     query = row
    # elif row.type in ['FFd','FFi']:
    #     if expiry and treatment_limit_times is not None:
    #         if expiry >= str(date.today()):
    #             if treatment_limit_times > done_ids or treatment_limit_times == 0:
    #                 query = row
    #         else:
    #             flsystem_ids = Systemsetup.objects.filter(title='flexitdexpiredlist',value_name='flexitdexpiredlist',value_data='True',isactive=True).first()
    #             if flsystem_ids: 
    #                 if treatment_limit_times > done_ids or treatment_limit_times == 0:
    #                     query = row        
    #     else:
    #         if treatment_limit_times is not None:
    #             if treatment_limit_times > done_ids or treatment_limit_times == 0:
    #                 query = row
    # trmtAccObj = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,treatment_parentcode=row.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
    # # print(trmtAccObj,"trmtAccObj")
    # if trmtAccObj:
    #     balance = "{:.2f}".format(float(trmtAccObj.balance)) if trmtAccObj.balance else "0.00"
    #     ar = "{:.2f}".format(float(trmtAccObj.outstanding)) if trmtAccObj.outstanding else "0.00"



    #new code given by yoouns
    def list(self, request):
        try:
            now = timezone.now()
            print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 

            system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()

            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Reversal',
            value_name='Other Outlet Customer Reversal',isactive=True).first()

            flexi_setup = Systemsetup.objects.filter(title='B21showServiceOnTreatmentForFlexi',
            value_name='B21showServiceOnTreatmentForFlexi',isactive=True).first()
            def_setup = Systemsetup.objects.filter(title='Default TD List Years Ago',
            value_name='Default TD List Years Ago',isactive=True).first()

            flexirev_setup = Systemsetup.objects.filter(title='FlexiRedeemAllowReversal',
            value_name='FlexiRedeemAllowReversal',isactive=True).first()


            current_year = date.today().year
            
            queryset = TreatmentPackage.objects.none()

            if not request.GET.get('year',None):
                raise Exception('Please give year!!') 

            if request.GET.get('year',None):
                year = request.GET.get('year',None)
                if year == "Default":
                    if def_setup and def_setup.value_data: 
                        ylst = []
                        for i in range(0,int(def_setup.value_data)):
                            yr = current_year - i
                            if yr not in ylst:
                                ylst.append(yr)
                                
                        if ylst != []: 
                            queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
                            open_session__gt=0, treatment_date__year__in=ylst).filter(Q(expiry_date__date__gte=date.today()) | Q(expiry_date__isnull=True)).order_by('-pk')

                    else:
                        raise Exception('Please Give Systemsetup year in Default TD List Years Ago!!')     
                elif year == "Expiry":
                    queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
                    open_session__gt=0,expiry_date__date__lt=date.today()).order_by('-pk')

                elif year == "All":
                    queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
                    open_session__gt=0).filter(Q(expiry_date__date__gte=date.today()) | Q(expiry_date__isnull=True)).order_by('-pk')
            
            q = self.request.GET.get('search',None)
            if q:
                queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
                open_session__gt=0).filter(Q(course__icontains=q)).filter(Q(expiry_date__date__gte=date.today()) | Q(expiry_date__isnull=True)).order_by('-pk')
            
            purchase_date = self.request.GET.get('purchase_date',None)
            if purchase_date and q:
                queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
                open_session__gt=0,treatment_date__date=purchase_date).filter(Q(course__icontains=q)).filter(Q(expiry_date__date__gte=date.today()) | Q(expiry_date__isnull=True)).order_by('-pk')
            elif purchase_date:
                queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
                open_session__gt=0,treatment_date__date=purchase_date).filter(Q(expiry_date__date__gte=date.today()) | Q(expiry_date__isnull=True)).order_by('-pk')


            tmp_ids = list(set(TmpItemHelper.objects.filter(treatment__Cust_Codeid__pk=cust_obj.pk,
            site_code=site.itemsite_code,created_at__date=date.today(),line_no__isnull=True).values_list('treatment__treatment_parentcode', flat=True).distinct()))   
             

            if queryset:
                full_tot = queryset.count()
                try:
                    limit = int(request.GET.get("limit",12))
                except:
                    limit = 12
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(queryset, limit)
                total_page = paginator.num_pages

                try:
                    queryset = paginator.page(page)
                    # print(queryset,"queryset")
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page
                    
                data_list= []
                for row in queryset:
                    trmt_obj = row ;is_allow=False
                    a = row.item_code
                    v = a[-4:]
                    # print(v,type(v),"v")
                    if v == '0000':
                        code = str(row.item_code)[:-4]
                    else:
                        code = str(row.item_code)    
                    
                    expiry_date = ""
                    if row.expiry_date:
                        splte = str(row.expiry_date).split(' ')
                        expiry = splte[0]
                        expiry_date = datetime.datetime.strptime(str(splte[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                    
                    flexiservice_ids = ItemFlexiservice.objects.filter(item_code=str(code),
                    itm_isactive=True)
                    search_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
                    created_at=date.today()).order_by('-pk').first()
                    if not search_ids:
                        TmpItemHelper.objects.filter(treatment__treatment_parentcode=trmt_obj.treatment_parentcode,line_no__isnull=True).delete()

                    session =  search_ids.session if search_ids and search_ids.session else 0
                        
                    if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                        if trmt_obj.site_code != site.itemsite_code or trmt_obj.site_code == site.itemsite_code:
                            is_allow = True
                    else:
                        if trmt_obj.site_code == site.itemsite_code:
                            is_allow = True  

                    splt = str(trmt_obj.treatment_date).split(' ')
                    treatment_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                    
                    td_setup = Systemsetup.objects.filter(title='TDSessionSelect',
                    value_name='TDSessionSelect',isactive=True).first()
                    
                    # treatmentids = json.loads(row.treatmentids) if row.treatmentids else []

                    # if td_setup and td_setup.value_data == 'asc':
                    #     c = treatmentids.sort()
                    # elif td_setup and td_setup.value_data == 'desc':
                    #     c = treatmentids.sort(reverse=True)
                    # # print(treatmentids,"treatmentids")

                    treatmentids =  list(Treatmentids.objects.filter(
                    treatment_parentcode=trmt_obj.treatment_parentcode).order_by('treatment_int').values_list('treatment_int', flat=True).distinct())
                    reversal_check = True
                    if flexirev_setup and flexirev_setup.value_data == 'True':
                        if row.type in ['FFd','FFi'] and row.done_session > 0:
                            reversal_check = False



                    data_list.append({
                        "TreatmentAccountid": row.treatment_accountid.pk if row.treatment_accountid else "",
                        "balance": "{:.2f}".format(float(row.balance)) if row.balance else "0.00",
                        "ar": "{:.2f}".format(float(row.outstanding)) if row.outstanding else "0.00",
                        "b21flexitype":True if flexi_setup and flexi_setup.value_data == 'True' and row.type == 'FFi' else False,
                        "course": row.course,
                        "done_sessioncnt": row.done_session,
                        "session_flag": False if session == 0 else True,
                        "exchange_flag" : True if session > 0 else False ,
                        "expiry_date" : expiry_date,
                        "is_allow" : is_allow,
                        "is_reversal" : fmspw[0].is_reversal,
                        "iscurrentloggedinsalon": True if site.itemsite_code == row.site_code else False ,
                        "item_code" : code,
                        "itemflexiservice" : True if row.type == 'FFi' and flexiservice_ids else False,
                        "open" : row.open_session,
                        "rev": "0"+"/"+row.treatment_no,
                        "td":str(row.open_session)+"/"+row.treatment_no,
                        "reversal_check": reversal_check, 
                        "sel": True if search_ids else None ,
                        "session" : session,
                        "site_code" :  trmt_obj.site_code,
                        "stockid" :  trmt_obj.Item_Codeid.pk if trmt_obj.Item_Codeid  else '' ,
                        "transacno_ref": trmt_obj.sa_transacno_ref,
                        "treatment_code" : trmt_obj.treatment_parentcode,
                        "treatment_date" : treatment_date,
                        "treatment_limit_times": row.treatment_limit_times,
                        "type" : row.type,
                        "treatmentids" : treatmentids,
                        "unit_amount" : "{:.2f}".format(float(row.unit_amount)),
                        "id": row.pk,
                    })        
                
               
                resData = {
                    'dataList': data_list,
                    'meta' : {'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
                    }},
                    
                }
                now1 = timezone.now()
                print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
                totalh = now1.second - now.second
                print(totalh,"total")

               
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",
                'error': False, 'data':  resData ,
                'cust_data': {'cust_name': cust_obj.cust_name if cust_obj.cust_name else "", 
                'cust_refer': cust_obj.cust_refer if cust_obj.cust_refer else "",
                'cust_phone': cust_obj.cust_phone2 if cust_obj.cust_phone2 else "",
                'cust_remark': cust_obj.cust_remark if cust_obj.cust_remark else "",
                },
                'totaltdlines' : len(tmp_ids),
                }
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_200_OK,"message":"No Content"
                ,'error': False, 'data': [],
                'cust_data': {'cust_name': cust_obj.cust_name if cust_obj.cust_name else "", 
                'cust_refer': cust_obj.cust_refer if cust_obj.cust_refer else "",
                'cust_phone': cust_obj.cust_phone2 if cust_obj.cust_phone2 else "",
                'cust_remark': cust_obj.cust_remark if cust_obj.cust_remark else "",
                },
                'totaltdlines' : len(tmp_ids),
                }
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          


    @transaction.atomic
    @action(detail=False, methods=['GET'], name='treatmentget')
    def treatmentget(self, request):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        
                site = fmspw[0].loginsite
                session = request.GET.get('session',None)
                if not session:
                    raise Exception('Please Give Session Value') 
                
                parentcode = request.GET.get('treatment_parentcode',None)
                if not parentcode:
                    raise Exception('Please Give treatment parentcode')

                trmt_ids = Treatment.objects.filter(treatment_parentcode=parentcode,status="Open").only('pk').order_by('-pk')    
                # print(trmt_ids,"trmt_ids")
                if not trmt_ids:
                    raise Exception('Open Treatment Does not exist')

                val = trmt_ids.order_by('-pk').values_list('pk', flat=True).distinct()
                # print(val,"val")
                if int(session) > len(val):
                    raise Exception('Session should not be greater than open treatments')

                resData = val[:int(session)]    
                
                var = TmpItemHelper.objects.filter(treatment__pk__in=val,created_at__date__lt=date.today(),line_no__isnull=True).delete() 
                
                search_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=parentcode,
                created_at=date.today()) 
                if not search_ids:
                    var_ids = TmpItemHelper.objects.filter(treatment__pk__in=val,line_no__isnull=True).delete() 

                sear_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=parentcode,
                created_at__lt=date.today()).delete()

                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",
                'error': False, 'treatmentid':  resData}
                return Response(data=result, status=status.HTTP_200_OK) 

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          
        



    


class TreatmentDoneViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentDoneSerializer

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def Year(self, request):
        try:
            today = timezone.now()
            year = today.year
            res = [r for r in range(2010, today.year+1)]
            res.append("All")
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': res[::-1]}
            return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)       

    def list(self, request):
        try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            # now2 = timezone.now()
            # print(str(now2.hour) + '  ' +  str(now2.minute) + '  ' +  str(now2.second),"End hour, minute, second\n")
            # totalr = now2.second - now.second
            # print(totalr,"total 22")
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            if not self.request.user.is_authenticated:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            if not fmspw:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            site = fmspw[0].loginsite
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # check = False
            system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()

            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Reversal',
            value_name='Other Outlet Customer Reversal',isactive=True).first()

            def_setup = Systemsetup.objects.filter(title='Default TD List Years Ago',
            value_name='Default TD List Years Ago',isactive=True).first()

            flexi_setup = Systemsetup.objects.filter(title='B21showServiceOnTreatmentForFlexi',
            value_name='B21showServiceOnTreatmentForFlexi',isactive=True).first()


            current_year = date.today().year
            
            
            queryset = Treatment.objects.none()

            if request.GET.get('year',None):
                year = request.GET.get('year',None)
                if year == "Default":
                    if def_setup and def_setup.value_data: 
                        ylst = []
                        for i in range(0,int(def_setup.value_data)):
                            yr = current_year - i
                            if yr not in ylst:
                                ylst.append(yr)
                                
                        if ylst != []:
                            # queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
                            # status="Open", treatment_date__year__in=ylst).order_by('pk')
                            # queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code,
                            # status="Open", treatment_date__year__in=ylst).order_by('-pk')

                            query_ids = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open", treatment_date__year__in=ylst).order_by('-pk').values_list('treatment_parentcode', flat=True).distinct()
                            # print(query_ids,"query_ids")
                            parlst = list(set([t for t in list(query_ids)]))
                            id_lst = []
                            if parlst != []:
                                for p in parlst:
                                    # query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code, site_code=site.itemsite_code,
                                    # status="Open", treatment_date__year=year).order_by('pk').last()
                                    query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code,
                                    status="Open", treatment_date__year__in=ylst).order_by('-pk').first()
                                    if query.pk not in id_lst:
                                        id_lst.append(query.pk) 
                            
                            # queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,site_code=site.itemsite_code, status="Open", treatment_date__year=year).order_by('pk')
                            queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,status="Open", treatment_date__year__in=ylst).order_by('-pk')
        
                    else:
                        raise Exception('Please Give Systemsetup year in Default TD List Years Ago!!')     
                elif year == "Expiry":
                    # queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open",expiry__date__lt=date.today()).order_by('-pk')
                    query_ids = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open",expiry__date__lt=date.today()).order_by('-pk').values_list('treatment_parentcode', flat=True).distinct()
                    parlst = list(set([t for t in list(query_ids)]))
                    idlst = []
                    if parlst != []:
                        for p in parlst:
                            query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code,
                            status="Open", expiry__date__lt=date.today()).order_by('-pk').first()
                            if query.pk not in idlst:
                                idlst.append(query.pk) 

                    queryset = Treatment.objects.filter(pk__in=idlst,cust_code=cust_obj.cust_code,status="Open", expiry__date__lt=date.today()).order_by('-pk')

                elif year == "All":
                    query_ids = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open").order_by('-pk').values_list('treatment_parentcode', flat=True).distinct()
                    # print(query_ids,"query_ids")
                    parlst = list(set([t for t in list(query_ids)]))
                    aid_lst = []
                    if parlst != []:
                        for pa in parlst:
                            # query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code, site_code=site.itemsite_code,
                            # status="Open", treatment_date__year=year).order_by('pk').last()
                            query = Treatment.objects.filter(treatment_parentcode=pa, cust_code=cust_obj.cust_code,
                            status="Open").order_by('-pk').first()
                            if query.pk not in aid_lst:
                                aid_lst.append(query.pk) 
                    
                    # print(aid_lst,"aid_lst")
                    # queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,site_code=site.itemsite_code, status="Open", treatment_date__year=year).order_by('pk')
                    queryset = Treatment.objects.filter(pk__in=aid_lst,cust_code=cust_obj.cust_code,status="Open").order_by('-pk')
                    # print(queryset.values_list('pk',flat=True),"queryset")


                
            limit = int(request.GET.get('limit',10)) if request.GET.get('limit',10) else 10
            page= int(request.GET.get('page',1)) if request.GET.get('page',1) else 1
            if page <= 0:
                raise Exception('Page less than one not allowed!!')     

            # exclude_ids = self.request.GET.get('exclude',[])
            # if exclude_ids and exclude_ids != []:
            #     excludeds = str(exclude_ids).split(',')
            #     # print(excludeds,"excludeds")
            #     if excludeds:
            #         queryt = queryset.filter(~Q(pk__in=excludeds)).order_by('-pk')
            #         l = sorted([i.pk for i in queryt])
            # else:
            #     queryt = queryset.filter().order_by('-pk')[:limit]
            #     l = sorted([i.pk for i in queryt])
            

            paginator = Paginator(queryset, limit) # chunks of 1000
            total_page = 1;total = len(queryset)
            if len(queryset) > int(limit):
                total_page = math.ceil(len(queryset)/int(limit))

            if queryset:
                if int(page) > total_page:
                    result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 
                    'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,"total_pages":total_page}}, 
                    'dataList': []}}
                    return Response(result, status=status.HTTP_200_OK) 


            # per = paginator.page(page)
            # print(per,"PPPPPPPPPPPPPPPPPP")
            
            # print(paginator.num_pages,"paginator.num_pages")
            # for page_idx in range(1, paginator.num_pages+1):
            #     # print(page_idx,"KKKKKKKKKKKKKKKKKKKKK")
            #     if page_idx == page:
            lst = [] 
            # for row in paginator.page(page_idx).object_list:
            for row in paginator.page(page).object_list:
                # print(row,row.pk,"RRRRRRRRRRRRRRRRRRRRRR")
                # here you can do what you want with the row
    
                session = 0;balance = "0.00"; ar= "0.00"
                treatmentids=[];is_allow=False;
                trmt_obj = row
                
                splt = str(trmt_obj.treatment_date).split(' ')
                treatment_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                unit_amount =  "{:.2f}".format(float(trmt_obj.unit_amount)) if trmt_obj.unit_amount else "0.00"
                service_codeids = Treatment.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode).order_by('pk').first()    

                if row.type in ['FFd','FFi']:
                    course = service_codeids.Item_Codeid.item_name
                    item_code = str(service_codeids.item_code) 
                else:
                    course = trmt_obj.course
                    item_code = str(trmt_obj.item_code) 

                if len(item_code) > 8:
                    itm_code = item_code[:-4]
                else:
                    itm_code = item_code    

                stockobj = Stock.objects.filter(item_code=itm_code).order_by('pk').first()  
                stockid = stockobj.pk if stockobj else 0      
                
                trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode).order_by('sa_date','sa_time','id').last()
                # print(trmtAccObj,"trmtAccObj")
                if trmtAccObj:
                    balance = "{:.2f}".format(float(trmtAccObj.balance)) if trmtAccObj.balance else "0.00"
                    ar = "{:.2f}".format(float(trmtAccObj.outstanding)) if trmtAccObj.outstanding else "0.00"
                
                if TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode).order_by('pk').exists():
                    acc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode).order_by('pk').first().pk
                else:
                    acc_obj = 0

                # print(trmt_obj.helper_ids.all(),"trmt_obj.helper_ids.all()")    
                trmtparobj = Treatment.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,status="Open").only('pk').order_by('pk')
                # print(trmtparobj,"trmtparobj")
                for oneids in trmtparobj:
                    # print(oneids.pk,"oneids PKK")
                    # print(oneids.helper_ids.all(),"oneids.helper_ids.all()")
                    treatmentids.append(oneids.pk)

                    var = TmpItemHelper.objects.filter(treatment=oneids,created_at__date__lt=date.today(),line_no__isnull=True).delete()
                    if trmt_obj.helper_ids.all().exists():
                        if oneids.helper_ids.all().exists():
                            session += 1
                    else:
                        for existing in oneids.helper_ids.all():
                            existing.delete() 
                
                # print(treatmentids,"treatmentids")
                # print(session,"session")
                for existing in trmt_obj.helper_ids.all():
                    trmt_obj.helper_ids.remove(existing) 
                
                #for t in TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code):
                #    trmt_obj.helper_ids.add(t)
                for t in TmpItemHelper.objects.filter(treatment=trmt_obj):
                    trmt_obj.helper_ids.add(t)  

                pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=trmt_obj.sa_transacno).order_by('-pk').first()

                transacno_ref = pos_haud.sa_transacno_ref if pos_haud and pos_haud.sa_transacno_ref else ""
                if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                    if trmt_obj.site_code != site.itemsite_code or trmt_obj.site_code == site.itemsite_code:
                        is_allow = True
                else:
                    if trmt_obj.site_code == site.itemsite_code:
                        is_allow = True               


                staff = ','.join([v.helper_id.display_name for v in trmt_obj.helper_ids.all() if v.helper_id.display_name]) if trmt_obj.helper_ids.all().exists() else None
                sel = True if trmt_obj.helper_ids.all().exists() else None 
                iscurrentloggedinsalon = True if site.itemsite_code == trmt_obj.site_code else False 

                session_flag = False if session == 0 else True 
                exchange_flag = True if session == 1 else False 

                if flexi_setup and flexi_setup.value_data == 'True' and row.type == 'FFi':
                    b21flexitype = True
                else:
                    b21flexitype = False 
                
                flexiservice_ids = ItemFlexiservice.objects.filter(item_code=str(trmt_obj.item_code)[:-4],
                itm_isactive=True)
                if row.type == 'FFi' and flexiservice_ids:
                    itemflexiservice = True
                else:
                    itemflexiservice = False

                
                expiry_date = ""
                if trmt_obj.expiry:
                    splti = str(trmt_obj.expiry).split(" ")
                    expiry_date = datetime.datetime.strptime(str(splti[0]), "%Y-%m-%d").strftime("%d-%b-%y")
               

                done_ids = Treatment.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,status="Done").order_by('pk').count()

                if row.type in ['FFd','FFi'] and done_ids > 0:
                    reversal_check = False
                else:
                    reversal_check = True

                

                # Thing.objects.annotate(favorited=Count(Case(When(favorites__user=john_cleese, then=1),default=0,output_field=BooleanField(),)),)
                # print(fmspw[0].is_reversal,"fmspw[0].is_reversal")
                q_val = list(Treatment.objects.filter(pk=trmt_obj.pk).order_by('-pk').values('pk').annotate(id=F('pk'),
                TreatmentAccountid=Value(acc_obj, output_field=IntegerField()) ,
                stockid=Value(stockid, output_field=IntegerField()),
                transacno_ref= Value(transacno_ref, output_field=CharField()),
                session_flag =  Value(session_flag, output_field=BooleanField()),
                exchange_flag =  Value(exchange_flag, output_field=BooleanField()),
                iscurrentloggedinsalon=Value(iscurrentloggedinsalon, output_field=BooleanField()),
                limit=Value(None, output_field=CharField()),
                staff=Value(staff, output_field=CharField()), 
                rev=Concat(Value('0/'), Value(' '), F('treatment_no'), output_field=CharField()),
                td=Concat(Value(len(treatmentids)), Value('/'), F('treatment_no'), output_field=CharField()),
                is_reversal=Value(fmspw[0].is_reversal, output_field=BooleanField()),
                is_allow=Value(is_allow, output_field=BooleanField())
                ).order_by('-pk'))
                # print(q_val,"q_val")
                # print(q_val[0],"kk")
                q_val[0].update({'course': course,'treatment_date': treatment_date,
                # 'expiry':trmt_obj.expiry,
                # 'isfoc':trmt_obj.isfoc,'sa_transacno':trmt_obj.sa_transacno,
                'treatment_code':trmt_obj.treatment_code,
                # 'type':trmt_obj.type,'status':trmt_obj.status,
                # 'times':trmt_obj.times,'treatment_parentcode':trmt_obj.treatment_parentcode,
                # 'treatment_no': trmt_obj.treatment_no,
                'site_code': trmt_obj.site_code,
                'unit_amount': unit_amount,'balance':balance,'ar':ar,
                'treatmentids' : treatmentids,
                'open' : len(treatmentids),
                'done_sessioncnt': done_ids,
                'session' : session,
                'sel' : sel,
                'type': row.type,
                'b21flexitype': b21flexitype,
                'itemflexiservice': itemflexiservice,
                'reversal_check' : reversal_check,
                'treatment_limit_times' : trmt_obj.treatment_limit_times,
                'expiry_date' : expiry_date,
                'item_code': service_codeids.service_itembarcode[:-4] if service_codeids and service_codeids.service_itembarcode else ""
                })
                # print( q_val[0]," q_val[0]")
                expiry = False
                if row.expiry:
                    splte = str(row.expiry).split(' ')
                    expiry = splte[0]
                # treatment_limit_times = False
                # print(row.treatment_limit_times,"row.treatment_limit_times")
                # if row.treatment_limit_times:
                treatment_limit_times = row.treatment_limit_times

                # print(q_val[0],"vv")
                if row.type == 'N':
                    # if expiry:
                    #     if expiry >= str(date.today()):
                    #         lst.extend([q_val[0]])
                    # else:  
                    lst.extend([q_val[0]])
                elif row.type in ['FFd','FFi']:
                    if expiry and treatment_limit_times is not None:
                        if expiry >= str(date.today()):
                            if treatment_limit_times > done_ids or treatment_limit_times == 0:
                                lst.extend([q_val[0]])   
                        else:
                            flsystem_ids = Systemsetup.objects.filter(title='flexitdexpiredlist',value_name='flexitdexpiredlist',value_data='True',isactive=True).first()
                            if flsystem_ids: 
                                if treatment_limit_times > done_ids or treatment_limit_times == 0:
                                    lst.extend([q_val[0]]) 
                    else:
                        if treatment_limit_times is not None:
                            if treatment_limit_times > done_ids or treatment_limit_times == 0:
                                lst.extend([q_val[0]])   



                                

                # print(lst,"lst")
                # site_code,treatment_date,course,transacno_ref,unit_amount,treatment_code,td,rev,open,ar,session,session_flag,iscurrentloggedinsalon,is_reversal,is_allow,

            
        
            if lst != []:
                now1 = timezone.now()
                # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
                totalh = now1.second - now.second
                # print(totalh,"total")
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                "total_pages":total_page}}, 'dataList': lst},
                'cust_data': {'cust_name': cust_obj.cust_name if cust_obj.cust_name else "", 
                'cust_refer': cust_obj.cust_refer if cust_obj.cust_refer else "",
                'cust_phone': cust_obj.cust_phone2 if cust_obj.cust_phone2 else "",
                'cust_remark': cust_obj.cust_remark if cust_obj.cust_remark else "",
                },
                }
                return Response(result, status=status.HTTP_200_OK) 
            else:
                result = {'status':status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,  'data': []}
                return Response(data=result, status=status.HTTP_200_OK)  
    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def changetreatduration(self, request): 
        try:  
            with transaction.atomic():
                if not request.data['treatment_id']:
                    raise Exception('Please give Treatment id!!.') 
                
                if not request.data['duration']:
                    raise Exception('Please give duration!!.') 

                if request.data['treatment_id']:
                    tr_obj = Treatment.objects.filter(pk=request.data['treatment_id']).first()
                    if not tr_obj:
                        raise Exception('Treatment ID does not exist!!.') 

                    if tr_obj:
                        tr_obj.duration = request.data['duration']
                        tr_obj.save()
                        result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                        'error': False}
                        return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)                
 

# class TrmtTmpItemHelperViewset(viewsets.ModelViewSet):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]
#     queryset = TmpItemHelper.objects.filter().order_by('-id')
#     serializer_class = TmpItemHelperSerializer

#     # def get_permissions(self):
#     #     if self.request.GET.get('treatmentid',None) is None:
#     #         msg = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Treatment Record ID",'error': False} 
#     #         raise exceptions.AuthenticationFailed(msg)
#     #     else:
#     #         self.permission_classes = [permissions.IsAuthenticated,]
#     #         return self.permission_classes

#     def list(self, request):
#         try:
#             if request.GET.get('treatmentid',None) is None:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
#             if not trmt_obj:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
#             # acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.sa_transacno,
#             # treatment_parentcode=trmt_obj.treatment_parentcode,Site_Codeid=trmt_obj.Site_Codeid).order_by('id').last()
#             acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.sa_transacno,
#             treatment_parentcode=trmt_obj.treatment_parentcode,site_code=trmt_obj.site_code).order_by('id').last()

#             if acc_ids and acc_ids.balance:  
#                 if acc_ids.balance < trmt_obj.unit_amount:
#                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Insufficient Amount in Treatment Account. Please Top Up!!",'error': True} 
#                     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            

#             # if cart_obj.deposit < cart_obj.discount_price:
#             #     msg = "Min Deposit for this treatment is SS {0} ! Treatment Done not allow.".format(str(cart_obj.discount_price))
#             #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
#             #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
#             item_code = str(trmt_obj.item_code)
#             itm_code = item_code[:-4]
#             stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()

#             # if trmt_obj.Item_Codeid.workcommpoints == None or trmt_obj.Item_Codeid.workcommpoints == 0.0:             
#             if stockobj.workcommpoints == None or stockobj.workcommpoints == 0.0:
#                 workcommpoints = 0.0
#                 # result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Work Point should not be None/zero value!!",'error': True} 
#                 # return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 workcommpoints = stockobj.workcommpoints
            
#             # stock_obj = Stock.objects.filter(pk=trmt_obj.Item_Codeid.pk,item_isactive=True).first()
#             if stockobj.srv_duration is None or stockobj.srv_duration == 0.0:
#                 srvduration = 60
#             else:
#                 srvduration = stockobj.srv_duration

#             stkduration = int(srvduration) + 30
#             hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                
#             h_obj = TmpItemHelper.objects.filter(treatment=trmt_obj).first()
#             value = {'Item':trmt_obj.course,'Price':"{:.2f}".format(float(trmt_obj.unit_amount)),
#             'work_point':"{:.2f}".format(float(workcommpoints)),'room_id':None,'room_name':None,
#             'source_id': trmt_obj.times if trmt_obj.times else "",'source_name':None,'new_remark':None,
#             'times':trmt_obj.times if trmt_obj.times else "",'add_duration':hrs}
#             if h_obj:
#                 if not h_obj.Room_Codeid is None:
#                     value['room_id'] = h_obj.Room_Codeid.pk
#                     value['room_name']  = h_obj.Room_Codeid.displayname
#                 if not h_obj.Source_Codeid is None:
#                     value['source_id'] = h_obj.Source_Codeid.pk
#                     value['source_name']  = h_obj.Source_Codeid.source_desc
#                 if not h_obj.new_remark is None:
#                     value['new_remark']  = h_obj.new_remark
#                 if h_obj.times:
#                     value['times']  = trmt_obj.times
#                 if h_obj.workcommpoints:
#                     sumwp1 = TmpItemHelper.objects.filter(treatment=trmt_obj.pk).aggregate(Sum('wp1'))
#                     value['work_point'] = "{:.2f}".format(float(sumwp1['wp1__sum']))       
        
        
#             queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id')
#             serializer = self.get_serializer(queryset, many=True)
#             final = []
#             if queryset:
#                 for t in serializer.data:
#                     s = dict(t)
#                     s['wp1'] = "{:.2f}".format(float(s['wp1']))
#                     s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
#                     s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
#                     s['add_duration'] =  get_in_val(self, s['add_duration'])
#                     final.append(s)
#             # else:
#             #     val = {'id':None,'helper_id':None,'helper_name':None,'wp1':None,'appt_fr_time':None,
#             #     'appt_to_time':None,'add_duration':None}  
#             #     final.append(val)
        
#             result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
#             'value': value,'data':  final}
#             return Response(data=result, status=status.HTTP_200_OK)  
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)    

#     def create(self, request):
#         try:
#             fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
#             site = fmspw[0].loginsite

#             if request.GET.get('treatmentid',None) is None:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            
#             trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
#             if not trmt_obj:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist / not in open status!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
#             item_code = str(trmt_obj.item_code)
#             itm_code = item_code[:-4]
#             stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()

#             # acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.treatment_account.ref_transacno,
#             # treatment_parentcode=trmt_obj.treatment_account.treatment_parentcode,Site_Codeid=site,).order_by('id').last()
            
#             tracc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
#             site_code=site.itemsite_code).order_by('pk').first()

#             acc_ids = TreatmentAccount.objects.filter(ref_transacno=tracc_obj.ref_transacno,
#             treatment_parentcode=tracc_obj.treatment_parentcode,site_code=site.itemsite_code,).order_by('id').last()

#             if acc_ids and acc_ids.balance:        
#                 if acc_ids.balance < trmt_obj.unit_amount:
#                     msg = "Treatment Account Balance is SS {0} is not less than Treatment Price {1}.".format(str(acc_ids.balance),str(trmt_obj.unit_amount))
#                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
#                     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            

#             # if not request.GET.get('Room_Codeid',None) is None:
#             #     room_ids = Room.objects.filter(id=request.GET.get('Room_Codeid',None),isactive=True).first()
#             #     if not room_ids:
#             #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
#             #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             # if not request.GET.get('Source_Codeid',None) is None:
#             #     source_ids = Source.objects.filter(id=request.GET.get('Source_Codeid',None),source_isactive=True).first()
#             #     if not source_ids:
#             #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Source ID does not exist!!",'error': True} 
#             #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             # if request.GET.get('Room_Codeid',None) is None:
#             #     room_ids = None

#             # if request.GET.get('Source_Codeid',None) is None:
#             #     source_ids = None 

        
#             if request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
#                 workcommpoints = 0.0
#             else:
#                 workcommpoints = request.GET.get('workcommpoints',None)  


#             tmp = []
#             h_obj = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk')

#             count = 1;Source_Codeid=None;Room_Codeid=None;new_remark=None;appt_fr_time=None;appt_to_time=None;add_duration=None
#             if stockobj.srv_duration is None or float(stockobj.srv_duration) == 0.0:
#                 stk_duration = 60
#             else:
#                 stk_duration = int(stockobj.srv_duration)

#             stkduration = int(stk_duration) + 30
#             hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
#             duration = hrs
#             add_duration = duration

#             helper_obj = Employee.objects.filter(emp_isactive=True,pk=request.data['helper_id']).first()
#             if not helper_obj:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             alemp_ids = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk,
#             helper_code=helper_obj.emp_code,site_code=site.itemsite_code).order_by('pk')
#             if alemp_ids:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Employee already selected!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
#             if h_obj:
#                 count = int(h_obj.count()) + 1
#                 Source_Codeid = h_obj[0].Source_Codeid
#                 Room_Codeid = h_obj[0].Room_Codeid
#                 new_remark = h_obj[0].new_remark
#                 last = h_obj.last()
            
#                 start_time =  get_in_val(self, last.appt_to_time); endtime = None
#                 if start_time:
#                     starttime = datetime.datetime.strptime(start_time, "%H:%M")

#                     end_time = starttime + datetime.timedelta(minutes = stkduration)
#                     endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
#                 appt_fr_time = starttime if start_time else None
#                 appt_to_time = endtime if endtime else None
                
#             wp1 = float(workcommpoints) / float(count)
        
#             serializer = self.get_serializer(data=request.data)
#             if serializer.is_valid():
#                 temph = serializer.save(item_name=stockobj.item_desc,helper_id=helper_obj,
#                 helper_name=helper_obj.display_name,helper_code=helper_obj.emp_code,Room_Codeid=Room_Codeid,
#                 site_code=site.itemsite_code,times=trmt_obj.times,treatment_no=trmt_obj.treatment_no,
#                 wp1=wp1,wp2=0.0,wp3=0.0,itemcart=None,treatment=trmt_obj,Source_Codeid=Source_Codeid,
#                 new_remark=new_remark,appt_fr_time=appt_fr_time,appt_to_time=appt_to_time,
#                 add_duration=add_duration,workcommpoints=workcommpoints)
#                 # trmt_obj.helper_ids.add(temph.id) 
#                 tmp.append(temph.id)

#                 for h in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk,site_code=site.itemsite_code).order_by('pk'):
#                     TmpItemHelper.objects.filter(id=h.id).update(wp1=wp1)
#             else:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 
#                 'data': serializer.errors}
#                 return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
#             if tmp != []:
#                 value = {'Item':stockobj.item_desc,'Price':"{:.2f}".format(float(trmt_obj.unit_amount)),
#                 'work_point':"{:.2f}".format(float(workcommpoints)),'Room':None,'Source':None,'new_remark':None,
#                 'times':trmt_obj.times}  
#                 tmp_h = TmpItemHelper.objects.filter(id__in=tmp)
#                 serializer_final = self.get_serializer(tmp_h, many=True)
#                 final = []
#                 for t in serializer_final.data:
#                     s = dict(t)
#                     s['wp1'] = "{:.2f}".format(float(s['wp1']))
#                     s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
#                     s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
#                     s['add_duration'] =  get_in_val(self, s['add_duration'])
#                     final.append(s)

#                 result = {'status': status.HTTP_201_CREATED,"message": "Created Succesfully",'error': False, 
#                 'value':value,'data':  final}
#                 return Response(result, status=status.HTTP_201_CREATED)

#             result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Invalid Input",'error': False, 
#             'data':  serializer.errors}
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)    
        

#     def get_object(self, pk):
#         try:
#             return TmpItemHelper.objects.get(pk=pk)
#         except TmpItemHelper.DoesNotExist:
#             raise Http404

#     def retrieve(self, request, pk=None):
#         try:
#             queryset = TmpItemHelper.objects.filter().order_by('pk')
#             tmpitm = get_object_or_404(queryset, pk=pk)
#             serializer = TmpItemHelperSerializer(tmpitm)
#             result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
#             'data':  serializer.data}
#             return Response(data=result, status=status.HTTP_200_OK)
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)      

    
#     def partial_update(self, request, pk=None):
#         try:
#             fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
#             site = fmspw[0].loginsite

#             if request.GET.get('Room_Codeid',None):
#                 room_ids = Room.objects.filter(id=request.GET.get('Room_Codeid',None),isactive=True).first()
#                 if not room_ids:
#                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
#                     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             if request.GET.get('Source_Codeid',None):
#                 source_ids = Source.objects.filter(id=request.GET.get('Source_Codeid',None),source_isactive=True).first()
#                 if not source_ids:
#                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Source ID does not exist!!",'error': True} 
#                     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             # if request.GET.get('Room_Codeid',None) is None or request.GET.get('Room_Codeid',None) == "null":
#             if not request.GET.get('Room_Codeid',None):
#                 room_ids = None

#             # if request.GET.get('Source_Codeid',None) is None or request.GET.get('Source_Codeid',None) == "null":
#             if not request.GET.get('Source_Codeid',None):     
#                 source_ids = None 

#             if request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
#                 workcommpoints = 0.0
#             else:
#                 workcommpoints = request.GET.get('workcommpoints',None)  

#             tmpobj = self.get_object(pk)
#             # appt = Appointment.objects.filter(cust_noid=tmpobj.treatment.Cust_Codeid,appt_date=date.today(),
#             # ItemSite_Codeid=site)    
#             # if not appt:
#             #     if (not 'appt_fr_time' in request.data or str(request.data['appt_fr_time']) is None) and (not 'add_duration' in request.data or str(request.data['add_duration']) is None):
#             #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment is not available today so please give appointment details",'error': True} 
#             #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
#             item_code = str(tmpobj.treatment.item_code)
#             itm_code = item_code[:-4]
#             stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()

#             serializer = self.get_serializer(tmpobj, data=request.data, partial=True)
#             if serializer.is_valid():
#                 if ('appt_fr_time' in request.data and not request.data['appt_fr_time'] == None):
#                     if ('add_duration' in request.data and not request.data['add_duration'] == None):
#                         if stockobj.srv_duration is None or float(stockobj.srv_duration) == 0.0:
#                             stk_duration = 60
#                         else:
#                             stk_duration = int(stockobj.srv_duration)

#                         stkduration = int(stk_duration) + 30
#                         t1 = datetime.datetime.strptime(str(request.data['add_duration']), '%H:%M')
#                         t2 = datetime.datetime(1900,1,1)
#                         addduration = (t1-t2).total_seconds() / 60.0

#                         hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
#                         start_time =  get_in_val(self, request.data['appt_fr_time'])
#                         starttime = datetime.datetime.strptime(start_time, "%H:%M")

#                         end_time = starttime + datetime.timedelta(minutes = addduration)
#                         endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
#                         duration = hrs
#                         serializer.save(appt_fr_time=starttime,appt_to_time=endtime,add_duration=request.data['add_duration'],
#                         Room_Codeid=room_ids,Source_Codeid=source_ids,new_remark=request.GET.get('new_remark',None))

#                         next_recs = TmpItemHelper.objects.filter(id__gte=tmpobj.pk,site_code=site.itemsite_code).order_by('pk')
#                         for t in next_recs:
#                             start_time =  get_in_val(self, t.appt_to_time)
#                             if start_time:
#                                 starttime = datetime.datetime.strptime(str(start_time), "%H:%M")
#                                 end_time = starttime + datetime.timedelta(minutes = stkduration)
#                                 endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
#                                 idobj = TmpItemHelper.objects.filter(id__gt=t.pk,site_code=site.itemsite_code).order_by('pk').first()
#                                 if idobj:
#                                     TmpItemHelper.objects.filter(id=idobj.pk).update(appt_fr_time=starttime,
#                                     appt_to_time=endtime,add_duration=duration)

#                 if 'wp1' in request.data and not request.data['wp1'] == None:
#                     serializer.save(wp1=float(request.data['wp1']))
#                     tmpids = TmpItemHelper.objects.filter(treatment=tmpobj.treatment,site_code=site.itemsite_code).order_by('pk').aggregate(Sum('wp1'))
#                     value ="{:.2f}".format(float(tmpids['wp1__sum']))
#                     tmpl_ids = TmpItemHelper.objects.filter(treatment=tmpobj.treatment,site_code=site.itemsite_code).order_by('pk')
#                     for t in tmpl_ids:
#                         TmpItemHelper.objects.filter(id=t.pk).update(workcommpoints=value)

#                 result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
#                 return Response(result, status=status.HTTP_200_OK)

#             result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)      
        

#     @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
#     authentication_classes=[TokenAuthentication])
#     def confirm(self, request):
#         try:
#             fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
#             site = fmspw[0].loginsite
#             # per = self.check_permissions(self.get_permissions(self))
#             # print(per,"per")
#             if request.GET.get('treatmentid',None) is None:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
#             trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
#             if not trmt_obj:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
#             trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None))
#             # print(trmt_obj,"trmt_obj")
#             if trmt_obj:
#                 tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj[0],site_code=site.itemsite_code)
#                 # print(tmp_ids,"tmp_ids")
#                 if not tmp_ids:
#                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Without employee cant do confirm!!",'error': False}
#                     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
#                 for emp in tmp_ids:
#                     appt = Appointment.objects.filter(cust_no=trmt_obj[0].cust_code,appt_date=date.today(),
#                     itemsite_code=fmspw[0].loginsite.itemsite_code,emp_no=emp.helper_code)
#                     # print(appt,"appt") 
#                     if not appt:
#                         tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj[0],
#                         helper_code=emp.helper_code,site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
#                         if tmpids:
#                             amsg = "Appointment is not available today, please give Start Time & Add Duration for employee {0} ".format(emp.helper_name)
#                             result = {'status': status.HTTP_400_BAD_REQUEST,"message": amsg,'error': True} 
#                             return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#                     #need to uncomment later
#                     # if emp.appt_fr_time and emp.appt_to_time:         
#                     #     appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
#                     #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
#                     #     if appt_ids:
#                     #         msg = "In These timing already Appointment is booked for employee {0} so allocate other duration".format(emp.helper_name)
#                     #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
#                     #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    
#                 # print(trmt_obj[0].helper_ids.all(),"trmt_obj[0].helper_ids")
#                 for existing in trmt_obj[0].helper_ids.all():
#                     trmt_obj[0].helper_ids.remove(existing) 
                
#                 # print(tmp_ids,"111")
#                 for t in tmp_ids:
#                     trmt_obj[0].helper_ids.add(t)
                
#                 # print(trmt_obj[0].helper_ids.all(),"222")
#             result = {'status': status.HTTP_200_OK , "message": "Confirmed Succesfully", 'error': False}
#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)        

    
#     @action(detail=False, methods=['delete'], name='delete', permission_classes=[IsAuthenticated & authenticated_only],
#     authentication_classes=[TokenAuthentication])
#     def delete(self, request): 
#         try:  
#             fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
#             site = fmspw[0].loginsite

#             if self.request.GET.get('clear_all',None) is None:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give clear all/line in parms!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
#             if request.GET.get('treatmentid',None) is None:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
#             if not trmt_obj:
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
#             state = status.HTTP_204_NO_CONTENT
#             try:
#                 tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).values_list('id')
#                 if not tmp_ids:
#                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Tmp Item Helper records is not present for this Treatment record id!!",'error': True} 
#                     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#                 if self.request.GET.get('clear_all',None) == "1":
#                     queryset = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).order_by('id').delete()
                    
#                 elif self.request.GET.get('clear_all',None) == "0":
#                     queryset = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).order_by('id').first().delete()
                
#                 result = {'status': status.HTTP_200_OK , "message": "Deleted Succesfully", 'error': False}
#                 return Response(result, status=status.HTTP_200_OK) 
        
#             except Http404:
#                 pass

#             result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': True}
#             return Response(result,status=status.HTTP_200_OK) 
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)

class SessionTmpItemHelperViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = TmpItemHelperSession.objects.filter().order_by('-id')
    serializer_class = SessionTmpItemHelperSerializer

    def get_queryset(self):
        
        
        queryset = TmpItemHelperSession.objects.filter(treatment_parentcode=self.request.GET.get('treatment_parentcode',None),
        sa_date__date=date.today()).order_by('-pk')

        return queryset

    def list(self, request):
        try:
            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            arrtreatmentid = request.GET.get('treatmentid',None).split(',')
            trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk__in=arrtreatmentid).order_by('-pk').first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            treatment_parentcode = self.request.GET.get('treatment_parentcode',None)
            if not treatment_parentcode:
                result = {'status': status.HTTP_400_BAD_REQUEST,
                "message":"Please give treatment parentcode",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            tpackage_obj = TreatmentPackage.objects.filter(treatment_parentcode=treatment_parentcode).first()
            if not tpackage_obj:
                result = {'status': status.HTTP_200_OK,"message":"TreatmentPackage id does't exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 
            

            if tpackage_obj.Item_Codeid.workcommpoints == None or tpackage_obj.Item_Codeid.workcommpoints == 0.0:
                workcommpoints = 0.0
            else:
                workcommpoints = tpackage_obj.Item_Codeid.workcommpoints
            
            value = {'Item': tpackage_obj.course,
            'Price':"{:.2f}".format(float(tpackage_obj.unit_amount)),
            'work_point':"{:.2f}".format(float(workcommpoints)),
            
            
            'flexipoints': int(trmt_obj.flexipoints) if trmt_obj.flexipoints else None,
            'item_code': tpackage_obj.Item_Codeid.item_code}
              

            queryset = self.filter_queryset(self.get_queryset())
            print(queryset,"queryset")
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
              
                
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data':  serializer.data,'value':value}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",
                'error': False, 'data': [],'value':value}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)             
    
    def get_object(self, pk):
        try:
            return TmpItemHelperSession.objects.get(pk=pk)
        except TmpItemHelperSession.DoesNotExist:
            raise Exception('TmpItemHelperSession Does not Exist') 

    def retrieve(self, request, pk=None):
        try:
            tmps = self.get_object(pk)
            serializer = SessionTmpItemHelperSerializer(tmps, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Sucessfully",
            'error': False, 'data': serializer.data} 
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
    
    @transaction.atomic
    def create(self, request):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
                cartdate = timezone.now().date()

                if request.data.get('treatmentid',None) is None:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if not 'helper_id' in request.data or not request.data['helper_id']:
                    result = {'status': status.HTTP_200_OK,"message":"Please Give Employee id!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
                
                if not 'wp1' in request.data or not request.data['wp1']:
                    result = {'status': status.HTTP_200_OK,"message":"Please Give wp1!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
                
                if not 'session' in request.data or not request.data['session']:
                    result = {'status': status.HTTP_200_OK,"message":"Please Give session!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
                


                arrtreatmentid = request.data.get('treatmentid',None)

                if request.data['session'] > len(arrtreatmentid):
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                    "message":"Session should not be greater than selected session count !!",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


                tids = Treatment.objects.filter(status="Open",pk__in=arrtreatmentid,type="FFi")
                if tids: 
                    accids = TreatmentAccount.objects.filter(ref_transacno=tids[0].sa_transacno,
                    treatment_parentcode=tids[0].treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                    if accids and accids.outstanding > 0:
                        fdsystem_ids = Systemsetup.objects.filter(title='flexitdwithpartialpay',value_name='flexitdwithpartialpay',value_data='False',isactive=True).first()
                        if fdsystem_ids: 
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please topup. Flexi TD cannot do with partial payment!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                        
                t_ids = Treatment.objects.filter(status="Open",pk__in=arrtreatmentid,type="N")

                if t_ids:
                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=t_ids[0].sa_transacno,
                    treatment_parentcode=t_ids[0].treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                    # print(acc_ids.balance,"acc_ids") 
                    trids = t_ids.aggregate(amount=Coalesce(Sum('unit_amount'), 0))
                    if acc_ids and acc_ids.balance:
                        # acc_balance = float("{:.2f}".format(acc_ids.balance))
                        acc_balance = acc_ids.balance
                    else:
                        acc_balance = 0
                        
                    if trids['amount'] and trids['amount'] > 0:
                        # tr_unitamt = float("{:.2f}".format(trids['amount']))
                        tr_unitamt = trids['amount']
                        if acc_balance < tr_unitamt:
                            system_setup = Systemsetup.objects.filter(title='Treatment',value_name='Allow layaway',value_data='FALSE',isactive=True).first()
                            if system_setup: 
                                msg = "Treatment Account Balance is S{0} is not enough to TD ${1}, Please Topup".format(str("{:.2f}".format(acc_ids.balance)),str("{:.2f}".format(trids['amount'])))
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                for a in arrtreatmentid:            
                    carttr_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_status="Inprogress",is_payment=False,
                    treatment__pk=int(a),type='Sales').exclude(type__in=type_ex).order_by('lineno') 
                    if carttr_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Delete Cart line then add new staffs",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


            
                if not request.GET.get('workcommpoints',None):
                    workcommpoints = 0.0
                elif request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
                    workcommpoints = 0.0
                else:
                    workcommpoints = request.GET.get('workcommpoints',None)  
                
                treatment_parentcode = self.request.data.get('treatment_parentcode',None)
                if not treatment_parentcode:
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                    "message":"Please give treatment parentcode",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                tpackage_obj = TreatmentPackage.objects.filter(treatment_parentcode=treatment_parentcode).first()
                if not tpackage_obj:
                    result = {'status': status.HTTP_200_OK,"message":"TreatmentPackage id does't exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 

            
                helper_obj = Employee.objects.filter(emp_isactive=True,
                pk=request.data['helper_id']).first()
                if not helper_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                alemp_ids = TmpItemHelperSession.objects.filter(treatment_parentcode=treatment_parentcode,
                helper_id=helper_obj,sa_date__date=cartdate).order_by('pk')
                if alemp_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Employee already selected!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    # trmt_obj.Item_Codeid.item_desc
                    
                    temph = serializer.save(treatment_parentcode=tpackage_obj.treatment_parentcode,
                    helper_id=helper_obj,
                    helper_name=helper_obj.display_name,helper_code=helper_obj.emp_code,
                    site_code=site.itemsite_code,
                    wp1=request.data['wp1'],sa_date=cartdate,
                    session=request.data['session'])
                    result = {'status': status.HTTP_201_CREATED,"message": "Created Succesfully",'error': False, 
                    'data':  serializer.data}
                    return Response(result, status=status.HTTP_201_CREATED)

                
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 
                    'data': serializer.errors}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
          
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    @transaction.atomic        
    def partial_update(self, request, pk=None):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
                if request.data.get('treatmentid',None) is None:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                arrtreatmentid = request.data.get('treatmentid',None)

                if request.data['session'] > len(arrtreatmentid):
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                    "message":"Session should not be greater than selected session count !!",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        

                if not 'wp1' in request.data or not request.data['wp1']:
                    result = {'status': status.HTTP_200_OK,"message":"Please Give wp1!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
                
                if not 'session' in request.data or not request.data['session']:
                    result = {'status': status.HTTP_200_OK,"message":"Please Give session!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
            
                
                tmpobj = self.get_object(pk)
                
                serializer = self.get_serializer(tmpobj, data=request.data, partial=True)
                if serializer.is_valid():
                
                    serializer.save(wp1=float(request.data['wp1']),
                    session=float(request.data['session']))
                    
                    result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)

                result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,
                'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)  

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    

            
             
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def confirm(self, request):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
                if request.data.get('treatmentid',None) is None:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                cartobj = ItemCart.objects.filter(pk=request.data.get('cart_id',None)).first()
                
                arrtreatmentid = request.data.get('treatmentid',None)
                print(arrtreatmentid,"arrtreatmentid")
                treatment_parentcode = self.request.data.get('treatment_parentcode',None)
                if not treatment_parentcode:
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                    "message":"Please give treatment parentcode",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                tpackage_obj = TreatmentPackage.objects.filter(treatment_parentcode=treatment_parentcode).first()
                if not tpackage_obj:
                    result = {'status': status.HTTP_200_OK,"message":"TreatmentPackage id does't exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
                
                queryset = TmpItemHelperSession.objects.filter(treatment_parentcode=treatment_parentcode,
                sa_date__date=date.today()).order_by('-pk')
                print(queryset,"queryset")
                
                totlist = []
                for idx, c in enumerate(queryset, start=1):
                    print(idx,c)
                    session_v = int(c.session) 
                
                    if totlist == []:
                        ori = arrtreatmentid[:session_v]
                        print(ori,"iff")
                        rem = arrtreatmentid[session_v:]
                        print(rem,"iff")
                        val = {'id': c.pk,'helper_id': c.helper_id.pk,'session': session_v,
                        'treatment': ori}
                        totlist.append(val)

                        for t in ori:
                            trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=t).first()
                            if not trmt_obj:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist / not in open status!!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                            
                            alemp_ids = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk,
                            helper_id__pk=c.helper_id.pk,site_code=site.itemsite_code).order_by('pk')
                            if alemp_ids:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Employee already selected!!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                            if trmt_obj.treatment_account and trmt_obj.treatment_account.itemcart and trmt_obj.treatment_account.itemcart.itemcodeid and trmt_obj.treatment_account.itemcart.itemcodeid.item_type and trmt_obj.treatment_account.itemcart.itemcodeid.item_type == 'PACKAGE':
                                item_name = trmt_obj.course
                            else:
                                item_name = trmt_obj.treatment_account.itemcart.itemdesc if trmt_obj.treatment_account and trmt_obj.treatment_account.itemcart and trmt_obj.treatment_account.itemcart.itemdesc else trmt_obj.course

                            
                            temph = TmpItemHelper(item_name=item_name,helper_id=c.helper_id,
                            helper_name=c.helper_id.display_name,helper_code=c.helper_id.emp_code,
                            site_code=site.itemsite_code,times=trmt_obj.times,treatment_no=trmt_obj.treatment_no,
                            wp1=c.wp1,wp2=0.0,wp3=0.0,itemcart=None,treatment=trmt_obj,
                            session=int(c.session))
                            temph.save()
                            trmt_obj.helper_ids.add(temph.id) 

                    else:
                        ori = rem[:session_v]
                        print(ori,"else")
                        treatori = ori
                        bal_ses = session_v - len(ori)
                        print(bal_ses,type(bal_ses),"bal_ses")
                        if bal_ses == 0:
                            rem = arrtreatmentid
                        else:
                            orii = arrtreatmentid[:bal_ses]
                            print(orii,"orii")
                            rem = arrtreatmentid[bal_ses:] 
                            print(rem,"else rem")
                            treatori = ori + orii
                    
                        print(treatori,"treatori")
                        val = {'id': c.pk,'helper_id': c.helper_id.pk,'session': session_v,
                        'treatment': treatori}
                        totlist.append(val)

                        for t in treatori:
                            trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=t).first()
                            if not trmt_obj:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist / not in open status!!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                            
                            alemp_ids = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk,
                            helper_id__pk=c.helper_id.pk,site_code=site.itemsite_code).order_by('pk')
                            if alemp_ids:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Employee already selected!!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                            if trmt_obj.treatment_account and trmt_obj.treatment_account.itemcart and trmt_obj.treatment_account.itemcart.itemcodeid and trmt_obj.treatment_account.itemcart.itemcodeid.item_type and trmt_obj.treatment_account.itemcart.itemcodeid.item_type == 'PACKAGE':
                                item_name = trmt_obj.course
                            else:
                                item_name = trmt_obj.treatment_account.itemcart.itemdesc if trmt_obj.treatment_account and trmt_obj.treatment_account.itemcart and trmt_obj.treatment_account.itemcart.itemdesc else trmt_obj.course

                            
                            temph = TmpItemHelper(item_name=item_name,helper_id=c.helper_id,
                            helper_name=c.helper_id.display_name,helper_code=c.helper_id.emp_code,
                            site_code=site.itemsite_code,times=trmt_obj.times,treatment_no=trmt_obj.treatment_no,
                            wp1=c.wp1,wp2=0.0,wp3=0.0,itemcart=None,treatment=trmt_obj,
                            session=int(c.session))
                            temph.save()
                            trmt_obj.helper_ids.add(temph.id) 
                        
                print(totlist,"totlist")

                
                for t in arrtreatmentid:
                    trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=t).first()
                    if not trmt_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                    trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=t)
                    if trmt_obj:
                        tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj[0])
                        if not tmp_ids:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Without employee cant do confirm!!",'error': False}
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        
                        for existing in trmt_obj[0].helper_ids.all():
                            trmt_obj[0].helper_ids.remove(existing) 

                        # print(trmt_obj[0],"id")
                        for t1 in tmp_ids:
                            trmt_obj[0].helper_ids.add(t1)

                        if cartobj:    
                            # for existing in cartobj.helper_ids.all():
                            #     cartobj.helper_ids.remove(existing) 

                            for exis in cartobj.treatment.helper_ids.all():
                                cartobj.treatment.helper_ids.remove(exis) 

                            for exist in cartobj.service_staff.all():
                                cartobj.service_staff.remove(exist)     

                            for t in TmpItemHelper.objects.filter(treatment=trmt_obj[0]):
                                helper_obj = Employee.objects.filter(emp_isactive=True,pk=t.helper_id.pk).first()
                                cartobj.helper_ids.add(t) 
                                cartobj.treatment.helper_ids.add(t) 
                                if helper_obj:
                                    cartobj.service_staff.add(helper_obj.pk) 

                    

                session_ids = list(set(TmpItemHelper.objects.filter(treatment__pk__in=arrtreatmentid).values_list('treatment', flat=True).distinct()))
                # print(session_ids,"session_ids")
                if session_ids:
                    trmtobj = Treatment.objects.filter(pk=arrtreatmentid[0]).first()
                    if not trmtobj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    if trmtobj.status == "Open":  
                        search_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=trmtobj.treatment_parentcode,
                        created_at=date.today()) 
                        if not search_ids:
                            t = TmpTreatmentSession(treatment_parentcode=trmtobj.treatment_parentcode,session=len(arrtreatmentid))
                            t.save()
                


                result = {'status': status.HTTP_200_OK , "message": "Confirmed Succesfully", 'error': False}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
    
    @transaction.atomic
    def destroy(self, request, pk=None):
        try:
            with transaction.atomic():
                if request.data.get('treatmentid',None) is None:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                arrtreatmentid = request.data.get('treatmentid',None)
                cartdate = timezone.now().date()
                
                for a in arrtreatmentid:            
                    carttr_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_status="Inprogress",is_payment=False,
                    treatment__pk=int(a),type='Sales').exclude(type__in=type_ex).order_by('lineno') 
                    if carttr_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Delete Cart line then try",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                treatment_parentcode = self.request.data.get('treatment_parentcode',None)
                if not treatment_parentcode:
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                    "message":"Please give treatment_parentcode",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                tpackage_obj = TreatmentPackage.objects.filter(treatment_parentcode=treatment_parentcode).first()
                if not tpackage_obj:
                    result = {'status': status.HTTP_200_OK,"message":"TreatmentPackage id does't exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 

                tmp = self.get_object(pk)
                serializer = SessionTmpItemHelperSerializer(tmp, data=request.data)

                state = status.HTTP_204_NO_CONTENT
                if serializer.is_valid():
                    # serializer.save()
                    tmp.delete()
                    oldobj = TmpItemHelperSession.objects.filter(treatment_parentcode=treatment_parentcode).order_by('pk')
                
                    if not oldobj:
                    
                        search_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=tpackage_obj.treatment_parentcode,
                        created_at=date.today()) 
                        if search_ids:
                            search_ids.delete()

                    result = {'status': status.HTTP_200_OK,"message":"Deleted Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)

                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
                'error': True, 'data': serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)       
                 
    @transaction.atomic
    @action(detail=False, methods=['delete'], name='delete', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def delete(self, request):  
        try: 
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite

                if self.request.data.get('clear_all',None) is None:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give clear all/line in parms!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                if request.data.get('treatmentid',None) is None:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                treatment_parentcode = self.request.data.get('treatment_parentcode',None)
                if not treatment_parentcode:
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                    "message":"Please give treatment_parentcode",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                tmp_ids = TmpItemHelperSession.objects.filter(treatment_parentcode=treatment_parentcode).values_list('id')
                if not tmp_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"TmpItemHelperSession records is not present for this treatment parentcode!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        

                arrtreatmentid = request.data.get('treatmentid',None)
                print(arrtreatmentid,"arrtreatmentid")
                cartdate = timezone.now().date()
                
                for a in arrtreatmentid:            
                    carttr_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_status="Inprogress",is_payment=False,
                    treatment__pk=int(a),type='Sales').exclude(type__in=type_ex).order_by('lineno') 
                    if carttr_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Delete Cart line then try",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                if self.request.data.get('clear_all',None) == 1:
                    tqueryset = TmpItemHelper.objects.filter(treatment__pk__in=arrtreatmentid).order_by('id').delete()
                    queryset = TmpItemHelperSession.objects.filter(treatment_parentcode=treatment_parentcode).order_by('id').delete()
                    
                elif self.request.data.get('clear_all',None) == 0:
                    q = TmpItemHelperSession.objects.filter(treatment_parentcode=treatment_parentcode).order_by('id').first()
                    tyqueryset = TmpItemHelper.objects.filter(treatment__pk__in=arrtreatmentid,helper_id=q.helper_id).order_by('id').delete()
                    queryset = q.delete()


                # workcommpoints = 0.0

                # for tt in arrtreatmentid:
                #     trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=tt).first()
                #     if not trmt_obj:
                #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                #     state = status.HTTP_204_NO_CONTENT
                #     tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj).values_list('id')
                #     if not tmp_ids:
                #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Tmp Item Helper records is not present for this Treatment record id!!",'error': True} 
                #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                #     if self.request.GET.get('clear_all',None) == "1":
                #         queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id').delete()
                        
                #     elif self.request.GET.get('clear_all',None) == "0":
                #         queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id').first().delete()

                #         if trmt_obj.Item_Codeid.workcommpoints == None or trmt_obj.Item_Codeid.workcommpoints == 0.0:
                #             workcommpoints = 0.0
                #         else:
                #             workcommpoints = trmt_obj.Item_Codeid.workcommpoints
                #         h_obj = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk')
                #         count = 1
                #         if h_obj:
                #             count = int(h_obj.count())

                #         wp11 = float(workcommpoints)
                #         wp12 = 0
                #         wp13 = 0
                #         wp14 = 0
                #         wp1 = float(workcommpoints)
                #         if wp1 > 0 :
                #             wp11 = float(workcommpoints) / float(count)
                #             if count == 2:
                #                 wp12 = float(workcommpoints) / float(count)
                #             if count == 3:
                #                 wp12 = float(workcommpoints) / float(count)
                #                 wp13 = float(workcommpoints) / float(count)
                #             if count == 4:
                #                 wp12 = float(workcommpoints) / float(count)
                #                 wp13 = float(workcommpoints) / float(count)
                #                 wp14 = float(workcommpoints) / float(count)

                #             if count == 2 and wp1 == 3:
                #                 wp11 = 2
                #                 wp12 = 1
                #             if count == 2 and wp1 == 5:
                #                 wp11 = 3
                #                 wp12 = 2
                #             if count == 2 and wp1 == 7:
                #                 wp11 = 4
                #                 wp12 = 3
                #             if count == 2 and wp1 == 9:
                #                 wp11 = 5
                #                 wp12 = 4
                #             if count == 2 and wp1 == 11:
                #                 wp11 = 6
                #                 wp12 = 5

                #             if count == 3 and wp1 == 2:
                #                 wp11 = 1
                #                 wp12 = 1
                #                 wp13 = 0
                #             if count == 3 and wp1 == 4:
                #                 wp11 = 2
                #                 wp12 = 1
                #                 wp13 = 1
                #             if count == 3 and wp1 == 5:
                #                 wp11 = 2
                #                 wp12 = 2
                #                 wp13 = 1
                #             if count == 3 and wp1 == 7:
                #                 wp11 = 3
                #                 wp12 = 2
                #                 wp13 = 2
                #             if count == 3 and wp1 == 8:
                #                 wp11 = 3
                #                 wp12 = 3
                #                 wp13 = 2
                #             if count == 3 and wp1 == 10:
                #                 wp11 = 4
                #                 wp12 = 3
                #                 wp13 = 3
                #             if count == 3 and wp1 == 11:
                #                 wp11 = 4
                #                 wp12 = 4
                #                 wp13 = 3

                #             runx=1
                #             for h in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk'):
                #                 if runx == 1:
                #                     TmpItemHelper.objects.filter(id=h.id).update(wp1=wp11)
                #                 if runx == 2:
                #                     TmpItemHelper.objects.filter(id=h.id).update(wp1=wp12)
                #                 if runx == 3:
                #                     TmpItemHelper.objects.filter(id=h.id).update(wp1=wp13)
                #                 if runx == 4:
                #                     TmpItemHelper.objects.filter(id=h.id).update(wp1=wp14)
                #                 runx = runx + 1



                # oldobj = TmpItemHelper.objects.filter(treatment__pk__in=arrtreatmentid).order_by('pk')
                # tr_lst = list(set([i.treatment.pk for i in oldobj]))
                # for j in tr_lst:
                #     trmtobj = Treatment.objects.filter(status="Open",pk=j).first()
                #     if not trmtobj:
                #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                #     hobj = TmpItemHelper.objects.filter(treatment__pk=trmtobj.pk).order_by('pk')
                #     scount = 1
                #     if hobj:
                #         scount = int(hobj.count())


                #     if workcommpoints and float(workcommpoints) > 0:
                #         wp = float(workcommpoints) / float(scount)
                #         v = str(wp).split('.')
                #         c = float(v[0]+"."+v[1][:2])
                #         r = count - 1
                #         x = float(workcommpoints) -  (c * r)
                #         last_rec = TmpItemHelper.objects.filter(treatment__pk=trmtobj.pk).order_by('pk').last()
                #         for j in TmpItemHelper.objects.filter(treatment__pk=trmtobj.pk).order_by('pk').exclude(pk=last_rec.pk):
                #             TmpItemHelper.objects.filter(id=j.id).update(wp1=c)
                #         last_rec.wp1 = x   
                #         last_rec.save()     
            
                oldobj = TmpItemHelperSession.objects.filter(treatment_parentcode=treatment_parentcode).order_by('pk')
                if not oldobj:
                
                    search_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=treatment_parentcode,
                    created_at=date.today()) 
                    if search_ids:
                        search_ids.delete()

                result = {'status': status.HTTP_200_OK , "message": "Deleted Succesfully", 'error': False}
                return Response(result, status=status.HTTP_200_OK)
                
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
    


class TrmtTmpItemHelperViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = TmpItemHelper.objects.filter().order_by('-id')
    serializer_class = TmpItemHelperSerializer


    def list(self, request):
        try:
            # print(request.GET.get('treatmentid',None),"request.GET.get('treatmentid',None)")
            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            arrtreatmentid = request.GET.get('treatmentid',None).split(',')
            tids = Treatment.objects.filter(status="Open",pk__in=arrtreatmentid,type="FFi")
            if tids: 
                accids = TreatmentAccount.objects.filter(ref_transacno=tids[0].sa_transacno,
                treatment_parentcode=tids[0].treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                if accids and accids.outstanding > 0:
                    fdsystem_ids = Systemsetup.objects.filter(title='flexitdwithpartialpay',value_name='flexitdwithpartialpay',value_data='False',isactive=True).first()
                    if fdsystem_ids: 
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please topup. Flexi TD cannot do with partial payment!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            

            t_ids = Treatment.objects.filter(status="Open",pk__in=arrtreatmentid,type="N")
            if t_ids:
                acc_ids = TreatmentAccount.objects.filter(ref_transacno=t_ids[0].sa_transacno,
                treatment_parentcode=t_ids[0].treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                trids = t_ids.aggregate(amount=Coalesce(Sum('unit_amount'), 0))
                if acc_ids and acc_ids.balance:
                    # acc_balance = float("{:.2f}".format(acc_ids.balance))
                    acc_balance = acc_ids.balance
                else:
                    acc_balance = 0

                if trids['amount'] and float(trids['amount']) > 0:
                    # tr_unitamt = float("{:.2f}".format(trids['amount']))
                    tr_unitamt = trids['amount']
                    if acc_balance < tr_unitamt:
                        system_setup = Systemsetup.objects.filter(title='Treatment',value_name='Allow layaway',value_data='FALSE',isactive=True).first()
                        if system_setup:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Insufficient Amount in Treatment Account, Please Top Up!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            

            for t in arrtreatmentid:
                trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=t).first()
                if not trmt_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                # if trmt_obj.type in ["FFi",'FFd'] and len(arrtreatmentid) > 1:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Multiple Treatment done not possible for type FFi/FFd!!",'error': True} 
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)



                # acc_ids = TreatmentAccount.objects.filter(ref_transacno=t_ids[0].sa_transacno,
                # treatment_parentcode=t_ids[0].treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
        
                # if acc_ids and acc_ids.balance:  
                #     if acc_ids.balance < trmt_obj.unit_amount:
                #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Insufficient Amount in Treatment Account. Please Top Up!!",'error': True} 
                #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        

                if trmt_obj.Item_Codeid.workcommpoints == None or trmt_obj.Item_Codeid.workcommpoints == 0.0:
                    workcommpoints = 0.0
                else:
                    workcommpoints = trmt_obj.Item_Codeid.workcommpoints
                
                srvduration = 60
                # stock_obj = Stock.objects.filter(pk=trmt_obj.Item_Codeid.pk,item_isactive=True).first()
                stock_obj = Stock.objects.filter(pk=trmt_obj.Item_Codeid.pk).first()
                if stock_obj:
                    if stock_obj.srv_duration is None or stock_obj.srv_duration == 0.0:
                        srvduration = 60
                    else:
                        srvduration = stock_obj.srv_duration

                stkduration = int(srvduration) + 30
                hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))

            
                h_obj = TmpItemHelper.objects.filter(treatment=trmt_obj).first()
                value = {'Item':trmt_obj.course,'Price':"{:.2f}".format(float(trmt_obj.unit_amount)),
                'work_point':"{:.2f}".format(float(workcommpoints)),'room_id':None,'room_name':None,
                'source_id': trmt_obj.times if trmt_obj.times else "",'source_name':None,'new_remark':None,
                'times':trmt_obj.times if trmt_obj.times else "",'add_duration':hrs,
                'flexipoints': int(trmt_obj.flexipoints) if trmt_obj.flexipoints else None,
                'item_code': trmt_obj.service_itembarcode[:-4] if trmt_obj.service_itembarcode else ""}
                if h_obj:
                    if not h_obj.Room_Codeid is None:
                        value['room_id'] = h_obj.Room_Codeid.pk
                        value['room_name']  = h_obj.Room_Codeid.displayname
                    if not h_obj.Source_Codeid is None:
                        value['source_id'] = h_obj.Source_Codeid.pk
                        value['source_name']  = h_obj.Source_Codeid.source_desc
                        if not h_obj.new_remark is None:
                            value['new_remark']  = h_obj.new_remark
                        if not h_obj.session is None:
                            value['session']  = h_obj.session
                        if h_obj.times:
                            value['times']  = trmt_obj.times
            
            sear_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
            created_at__lt=date.today()).delete()
            trmtparobj = Treatment.objects.filter(cust_code=trmt_obj.cust_code,treatment_parentcode=trmt_obj.treatment_parentcode,status="Open").only('pk').order_by('pk').values_list('pk', flat=True).distinct()
            var = TmpItemHelper.objects.filter(treatment__pk__in=trmtparobj,created_at__date__lt=date.today(),line_no__isnull=True).delete() 

            queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id')
            serializer = self.get_serializer(queryset, many=True)
            final = []
            if queryset:
                for t1 in serializer.data:
                    s = dict(t1)
                    s['wp1'] = "{:.2f}".format(float(s['wp1']))
                    # print(s,"s")
                    s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
                    s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
                    s['add_duration'] =  get_in_val(self, s['add_duration'])
                    s['session'] = "{:.2f}".format(float(s['session'])) if s['session'] else ""
                    final.append(s)
            
            
            result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
            'value': value,'data':  final}
            return Response(data=result, status=status.HTTP_200_OK)  

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    
    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            cartdate = timezone.now().date()

            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            arrtreatmentid = request.GET.get('treatmentid',None).split(',')

            tids = Treatment.objects.filter(status="Open",pk__in=arrtreatmentid,type="FFi")
            if tids: 
                accids = TreatmentAccount.objects.filter(ref_transacno=tids[0].sa_transacno,
                treatment_parentcode=tids[0].treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                if accids and accids.outstanding > 0:
                    fdsystem_ids = Systemsetup.objects.filter(title='flexitdwithpartialpay',value_name='flexitdwithpartialpay',value_data='False',isactive=True).first()
                    if fdsystem_ids: 
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please topup. Flexi TD cannot do with partial payment!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                    
            t_ids = Treatment.objects.filter(status="Open",pk__in=arrtreatmentid,type="N")

            if t_ids:
                acc_ids = TreatmentAccount.objects.filter(ref_transacno=t_ids[0].sa_transacno,
                treatment_parentcode=t_ids[0].treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                # print(acc_ids.balance,"acc_ids") 
                trids = t_ids.aggregate(amount=Coalesce(Sum('unit_amount'), 0))
                if acc_ids and acc_ids.balance:
                    # acc_balance = float("{:.2f}".format(acc_ids.balance))
                    acc_balance = acc_ids.balance
                else:
                    acc_balance = 0
                    
                if trids['amount'] and trids['amount'] > 0:
                    # tr_unitamt = float("{:.2f}".format(trids['amount']))
                    tr_unitamt = trids['amount']
                    if acc_balance < tr_unitamt:
                        system_setup = Systemsetup.objects.filter(title='Treatment',value_name='Allow layaway',value_data='FALSE',isactive=True).first()
                        if system_setup: 
                            msg = "Treatment Account Balance is S{0} is not enough to TD ${1}, Please Topup".format(str("{:.2f}".format(acc_ids.balance)),str("{:.2f}".format(trids['amount'])))
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            for a in arrtreatmentid:            
                carttr_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_status="Inprogress",is_payment=False,
                treatment__pk=int(a),type='Sales').exclude(type__in=type_ex).order_by('lineno') 
                if carttr_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Delete Cart line then add new staffs",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


            for t in arrtreatmentid:
                trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=t).first()
                if not trmt_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist / not in open status!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                item_code = str(trmt_obj.item_code)
                itm_code = item_code[:-4]
                stockobj = Stock.objects.filter(item_code=itm_code).order_by('pk').first()
            
                # acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.treatment_account.ref_transacno,
                # treatment_parentcode=trmt_obj.treatment_account.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()

                # if acc_ids and acc_ids.balance:        
                #     if acc_ids.balance < trmt_obj.unit_amount:
                #         msg = "Treatment Account Balance is SS {0} is not less than Treatment Price {1}.".format(str(acc_ids.balance),str(trmt_obj.unit_amount))
                #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                if not request.GET.get('workcommpoints',None):
                    workcommpoints = 0.0
                elif request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
                    workcommpoints = 0.0
                else:
                    workcommpoints = request.GET.get('workcommpoints',None)  

                tmp = []
                h_obj = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk')

                count = 1;Source_Codeid=None;Room_Codeid=None;new_remark=None;appt_fr_time=None;appt_to_time=None;add_duration=None
                # session=1
                session = len(arrtreatmentid)
                if trmt_obj.Item_Codeid.srv_duration is None or float(trmt_obj.Item_Codeid.srv_duration) == 0.0:
                    stk_duration = 60
                else:
                    stk_duration = stockobj.srv_duration if stockobj and stockobj.srv_duration else 60

                stkduration = int(stk_duration) + 30
                hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                duration = hrs
                add_duration = duration

                helper_obj = Employee.objects.filter(emp_isactive=True,pk=request.data['helper_id']).first()
                if not helper_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


                alemp_ids = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk,
                helper_code=helper_obj.emp_code,site_code=site.itemsite_code).order_by('pk')
                if alemp_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Employee already selected!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
                if h_obj:
                    count = int(h_obj.count()) + 1
                    Source_Codeid = h_obj[0].Source_Codeid
                    Room_Codeid = h_obj[0].Room_Codeid
                    new_remark = h_obj[0].new_remark
                    session = h_obj[0].session
                    last = h_obj.last()
            
                    start_time =  get_in_val(self, last.appt_to_time); endtime = None
                    if start_time:
                        starttime = datetime.datetime.strptime(start_time, "%H:%M")

                        end_time = starttime + datetime.timedelta(minutes = stkduration)
                        endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                    appt_fr_time = starttime if start_time else None
                    appt_to_time = endtime if endtime else None
                
                # wp1 = float(workcommpoints) / float(count)
                wp11 = float(workcommpoints)
                wp12 = 0
                wp13 = 0
                wp14 = 0
                wp1 = float(workcommpoints)
                if wp1 > 0 :
                    wp11 = float(workcommpoints) / float(count)
                    if count == 2:
                        wp12 = float(workcommpoints) / float(count)
                    if count == 3:
                        wp12 = float(workcommpoints) / float(count)
                        wp13 = float(workcommpoints) / float(count)
                    if count == 4:
                        wp12 = float(workcommpoints) / float(count)
                        wp13 = float(workcommpoints) / float(count)
                        wp14 = float(workcommpoints) / float(count)
        
                    if count == 2 and wp1 == 3:
                        wp11 = 2
                        wp12 = 1
                    if count == 2 and wp1 == 5:
                        wp11 = 3
                        wp12 = 2
                    if count == 2 and wp1 == 7:
                        wp11 = 4
                        wp12 = 3
                    if count == 2 and wp1 == 9:
                        wp11 = 5
                        wp12 = 4
                    if count == 2 and wp1 == 11:
                        wp11 = 6
                        wp12 = 5

                    if count == 3 and wp1 == 2:
                        wp11 = 1
                        wp12 = 1
                        wp13 = 0
                    if count == 3 and wp1 == 4:
                        wp11 = 2
                        wp12 = 1
                        wp13 = 1
                    if count == 3 and wp1 == 5:
                        wp11 = 2
                        wp12 = 2
                        wp13 = 1
                    if count == 3 and wp1 == 7:
                        wp11 = 3
                        wp12 = 2
                        wp13 = 2
                    if count == 3 and wp1 == 8:
                        wp11 = 3
                        wp12 = 3
                        wp13 = 2
                    if count == 3 and wp1 == 10:
                        wp11 = 4
                        wp12 = 3
                        wp13 = 3
                    if count == 3 and wp1 == 11:
                        wp11 = 4
                        wp12 = 4
                        wp13 = 3
        
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    # trmt_obj.Item_Codeid.item_desc
                    
                    if trmt_obj.treatment_account and trmt_obj.treatment_account.itemcart and trmt_obj.treatment_account.itemcart.itemcodeid and trmt_obj.treatment_account.itemcart.itemcodeid.item_type and trmt_obj.treatment_account.itemcart.itemcodeid.item_type == 'PACKAGE':
                        item_name = trmt_obj.course
                    else:
                        item_name = trmt_obj.treatment_account.itemcart.itemdesc if trmt_obj.treatment_account and trmt_obj.treatment_account.itemcart and trmt_obj.treatment_account.itemcart.itemdesc else trmt_obj.course

                    
                    temph = serializer.save(item_name=item_name,helper_id=helper_obj,
                    helper_name=helper_obj.display_name,helper_code=helper_obj.emp_code,Room_Codeid=Room_Codeid,
                    site_code=site.itemsite_code,times=trmt_obj.times,treatment_no=trmt_obj.treatment_no,
                    wp1=wp1,wp2=0.0,wp3=0.0,itemcart=None,treatment=trmt_obj,Source_Codeid=Source_Codeid,
                    new_remark=new_remark,appt_fr_time=appt_fr_time,appt_to_time=appt_to_time,
                    add_duration=add_duration,workcommpoints=workcommpoints,session=session)
                    trmt_obj.helper_ids.add(temph.id) 
                    tmp.append(temph.id)
    
                    runx=1
                    for h in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk'):
                        # TmpItemHelper.objects.filter(id=h.id).update(wp1=wp1)
                        if runx == 1:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp11)
                        if runx == 2:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp12)
                        if runx == 3:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp13)
                        if runx == 4:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp14)
                        runx = runx + 1


                    wp = float(workcommpoints) / float(count)
                    v = str(wp).split('.')
                    c = float(v[0]+"."+v[1][:2])
                    r = count - 1
                    x = float(workcommpoints) -  (c * r)
                    last_rec = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk').last()
                    for j in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk').exclude(pk=last_rec.pk):
                        TmpItemHelper.objects.filter(id=j.id).update(wp1=c)
                    last_rec.wp1 = x   
                    last_rec.save()    

                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 
                    'data': serializer.errors}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
            if tmp != []:
                value = {'Item':trmt_obj.Item_Codeid.item_desc,'Price':"{:.2f}".format(float(trmt_obj.unit_amount)),
                'work_point':"{:.2f}".format(float(workcommpoints)),'Room':None,'Source':None,'new_remark':None,
                'times':trmt_obj.times}  
                tmp_h = TmpItemHelper.objects.filter(id__in=tmp)
                serializer_final = self.get_serializer(tmp_h, many=True)
                final = []
                for t1 in serializer_final.data:
                    s = dict(t1)
                    s['wp1'] = "{:.2f}".format(float(s['wp1']))
                    s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
                    s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
                    s['add_duration'] =  get_in_val(self, s['add_duration'])
                    final.append(s)
                # print(final,"final")
                result = {'status': status.HTTP_201_CREATED,"message": "Created Succesfully",'error': False, 
                'value':value,'data':  final}
                return Response(result, status=status.HTTP_201_CREATED)

            result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Invalid Input",'error': False, 
            'data':  serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
    
    
    def get_object(self, pk):
        try:
            return TmpItemHelper.objects.get(pk=pk)
        except TmpItemHelper.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            # print(request,"retrieve")
            queryset = TmpItemHelper.objects.filter().order_by('pk')
            tmpitm = get_object_or_404(queryset, pk=pk)
            serializer = TmpItemHelperSerializer(tmpitm)
            # print(serializer.data,"serializer.data")
            result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
            'data':  serializer.data}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
     
   
    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            if request.GET.get('Room_Codeid',None):
                room_ids = Room.objects.filter(id=request.GET.get('Room_Codeid',None),isactive=True).first()
                if not room_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            source_ids = None 
            room_ids = None
            if not request.GET.get('Room_Codeid',None):
                room_ids = None

            if request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
                workcommpoints = 0.0
            else:
                workcommpoints = request.GET.get('workcommpoints',None)  

            tmpobj = self.get_object(pk)
            
            serializer = self.get_serializer(tmpobj, data=request.data, partial=True)
            if serializer.is_valid():
                if ('appt_fr_time' in request.data and not request.data['appt_fr_time'] == None):
                    if ('add_duration' in request.data and not request.data['add_duration'] == None):
                        if tmpobj.treatment.Item_Codeid.srv_duration is None or float(tmpobj.treatment.Item_Codeid.srv_duration) == 0.0:
                            stk_duration = 60
                        else:
                            stk_duration = int(tmpobj.treatment.Item_Codeid.srv_duration)

                        stkduration = int(stk_duration) + 30
                        t1 = datetime.datetime.strptime(str(request.data['add_duration']), '%H:%M')
                        t2 = datetime.datetime(1900,1,1)
                        addduration = (t1-t2).total_seconds() / 60.0

                        hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                        start_time =  get_in_val(self, request.data['appt_fr_time'])
                        starttime = datetime.datetime.strptime(start_time, "%H:%M")

                        end_time = starttime + datetime.timedelta(minutes = addduration)
                        endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                        duration = hrs
                        serializer.save(appt_fr_time=starttime,appt_to_time=endtime,add_duration=request.data['add_duration'],
                        Room_Codeid=room_ids,Source_Codeid=source_ids,new_remark=request.GET.get('new_remark',None))

                        next_recs = TmpItemHelper.objects.filter(id__gte=tmpobj.pk,site_code=site.itemsite_code).order_by('pk')
                        for t in next_recs:
                            start_time =  get_in_val(self, t.appt_to_time)
                            if start_time:
                                starttime = datetime.datetime.strptime(str(start_time), "%H:%M")
                                end_time = starttime + datetime.timedelta(minutes = stkduration)
                                endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                                idobj = TmpItemHelper.objects.filter(id__gt=t.pk,site_code=site.itemsite_code).order_by('pk').first()
                                if idobj:
                                    TmpItemHelper.objects.filter(id=idobj.pk).update(appt_fr_time=starttime,
                                    appt_to_time=endtime,add_duration=duration)

                if 'session' in request.data and not request.data['session'] == None:
                    serializer.save(session=float(request.data['session']))

                if 'wp1' in request.data and not request.data['wp1'] == None:
                    serializer.save(wp1=float(request.data['wp1']))
                    tmpids = TmpItemHelper.objects.filter(treatment=tmpobj.treatment,site_code=site.itemsite_code).order_by('pk').aggregate(Sum('wp1'))
                    value ="{:.2f}".format(float(tmpids['wp1__sum']))
                    tmpl_ids = TmpItemHelper.objects.filter(treatment=tmpobj.treatment,site_code=site.itemsite_code).order_by('pk')
                    for t in tmpl_ids:
                        TmpItemHelper.objects.filter(id=t.pk).update(workcommpoints=value)

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)  

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
    
    

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def confirm(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            cartobj = ItemCart.objects.filter(pk=request.GET.get('cart_id',None)).first()
            
            
            arrtreatmentid = request.GET.get('treatmentid',None).split(',')
            for t in arrtreatmentid:
                trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=t).first()
                if not trmt_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=t)
                if trmt_obj:
                    tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj[0])
                    if not tmp_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Without employee cant do confirm!!",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    
                    for existing in trmt_obj[0].helper_ids.all():
                        trmt_obj[0].helper_ids.remove(existing) 

                    # print(trmt_obj[0],"id")
                    for t1 in tmp_ids:
                        trmt_obj[0].helper_ids.add(t1)

                    if cartobj:    
                        # for existing in cartobj.helper_ids.all():
                        #     cartobj.helper_ids.remove(existing) 

                        for exis in cartobj.treatment.helper_ids.all():
                            cartobj.treatment.helper_ids.remove(exis) 

                        for exist in cartobj.service_staff.all():
                            cartobj.service_staff.remove(exist)     

                        for t in TmpItemHelper.objects.filter(treatment=trmt_obj[0]):
                            helper_obj = Employee.objects.filter(emp_isactive=True,pk=t.helper_id.pk).first()
                            cartobj.helper_ids.add(t) 
                            cartobj.treatment.helper_ids.add(t) 
                            if helper_obj:
                                cartobj.service_staff.add(helper_obj.pk) 

                  

            session_ids = list(set(TmpItemHelper.objects.filter(treatment__pk__in=arrtreatmentid).values_list('treatment', flat=True).distinct()))
            # print(session_ids,"session_ids")
            if session_ids:
                trmtobj = Treatment.objects.filter(pk=arrtreatmentid[0]).first()
                if not trmtobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if trmtobj.status == "Open":  
                    search_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=trmtobj.treatment_parentcode,
                    created_at=date.today()) 
                    if not search_ids:
                        t = TmpTreatmentSession(treatment_parentcode=trmtobj.treatment_parentcode,session=len(arrtreatmentid))
                        t.save()
            


            result = {'status': status.HTTP_200_OK , "message": "Confirmed Succesfully", 'error': False}
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def destroy(self, request, pk=None):
        try:
            tmp = self.get_object(pk)
            serializer = TmpItemHelperSerializer(tmp, data=request.data)
            state = status.HTTP_204_NO_CONTENT
            if serializer.is_valid():
                # serializer.save()
                tmp.delete()
                result = {'status': status.HTTP_200_OK,"message":"Deleted Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
            'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)       
                 

    
    @action(detail=False, methods=['delete'], name='delete', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def delete(self, request):  
        try: 
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            if self.request.GET.get('clear_all',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give clear all/line in parms!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            arrtreatmentid = request.GET.get('treatmentid',None).split(',')
            cartdate = timezone.now().date()
            
            for a in arrtreatmentid:            
                carttr_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_status="Inprogress",is_payment=False,
                treatment__pk=int(a),type='Sales').exclude(type__in=type_ex).order_by('lineno') 
                if carttr_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Delete Cart line then try",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            workcommpoints = 0.0

            for tt in arrtreatmentid:
                trmt_obj = Treatment.objects.filter(status__in=["Open","Done"],pk=tt).first()
                if not trmt_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                state = status.HTTP_204_NO_CONTENT
                tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj).values_list('id')
                if not tmp_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Tmp Item Helper records is not present for this Treatment record id!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if self.request.GET.get('clear_all',None) == "1":
                    queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id').delete()
                    
                elif self.request.GET.get('clear_all',None) == "0":
                    queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id').first().delete()

                    if trmt_obj.Item_Codeid.workcommpoints == None or trmt_obj.Item_Codeid.workcommpoints == 0.0:
                        workcommpoints = 0.0
                    else:
                        workcommpoints = trmt_obj.Item_Codeid.workcommpoints
                    h_obj = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk')
                    count = 1
                    if h_obj:
                        count = int(h_obj.count())

                    wp11 = float(workcommpoints)
                    wp12 = 0
                    wp13 = 0
                    wp14 = 0
                    wp1 = float(workcommpoints)
                    if wp1 > 0 :
                        wp11 = float(workcommpoints) / float(count)
                        if count == 2:
                            wp12 = float(workcommpoints) / float(count)
                        if count == 3:
                            wp12 = float(workcommpoints) / float(count)
                            wp13 = float(workcommpoints) / float(count)
                        if count == 4:
                            wp12 = float(workcommpoints) / float(count)
                            wp13 = float(workcommpoints) / float(count)
                            wp14 = float(workcommpoints) / float(count)

                        if count == 2 and wp1 == 3:
                            wp11 = 2
                            wp12 = 1
                        if count == 2 and wp1 == 5:
                            wp11 = 3
                            wp12 = 2
                        if count == 2 and wp1 == 7:
                            wp11 = 4
                            wp12 = 3
                        if count == 2 and wp1 == 9:
                            wp11 = 5
                            wp12 = 4
                        if count == 2 and wp1 == 11:
                            wp11 = 6
                            wp12 = 5

                        if count == 3 and wp1 == 2:
                            wp11 = 1
                            wp12 = 1
                            wp13 = 0
                        if count == 3 and wp1 == 4:
                            wp11 = 2
                            wp12 = 1
                            wp13 = 1
                        if count == 3 and wp1 == 5:
                            wp11 = 2
                            wp12 = 2
                            wp13 = 1
                        if count == 3 and wp1 == 7:
                            wp11 = 3
                            wp12 = 2
                            wp13 = 2
                        if count == 3 and wp1 == 8:
                            wp11 = 3
                            wp12 = 3
                            wp13 = 2
                        if count == 3 and wp1 == 10:
                            wp11 = 4
                            wp12 = 3
                            wp13 = 3
                        if count == 3 and wp1 == 11:
                            wp11 = 4
                            wp12 = 4
                            wp13 = 3

                        runx=1
                        for h in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk'):
                            if runx == 1:
                                TmpItemHelper.objects.filter(id=h.id).update(wp1=wp11)
                            if runx == 2:
                                TmpItemHelper.objects.filter(id=h.id).update(wp1=wp12)
                            if runx == 3:
                                TmpItemHelper.objects.filter(id=h.id).update(wp1=wp13)
                            if runx == 4:
                                TmpItemHelper.objects.filter(id=h.id).update(wp1=wp14)
                            runx = runx + 1



            oldobj = TmpItemHelper.objects.filter(treatment__pk__in=arrtreatmentid).order_by('pk')
            tr_lst = list(set([i.treatment.pk for i in oldobj]))
            for j in tr_lst:
                trmtobj = Treatment.objects.filter(status="Open",pk=j).first()
                if not trmtobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                hobj = TmpItemHelper.objects.filter(treatment__pk=trmtobj.pk).order_by('pk')
                scount = 1
                if hobj:
                    scount = int(hobj.count())


                if workcommpoints and float(workcommpoints) > 0:
                    wp = float(workcommpoints) / float(scount)
                    v = str(wp).split('.')
                    c = float(v[0]+"."+v[1][:2])
                    r = count - 1
                    x = float(workcommpoints) -  (c * r)
                    last_rec = TmpItemHelper.objects.filter(treatment__pk=trmtobj.pk).order_by('pk').last()
                    for j in TmpItemHelper.objects.filter(treatment__pk=trmtobj.pk).order_by('pk').exclude(pk=last_rec.pk):
                        TmpItemHelper.objects.filter(id=j.id).update(wp1=c)
                    last_rec.wp1 = x   
                    last_rec.save()     
            
            
            if not oldobj:
                trmtrobj = Treatment.objects.filter(pk=arrtreatmentid[0]).first()
                if not trmtrobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                search_ids = TmpTreatmentSession.objects.filter(treatment_parentcode=trmtrobj.treatment_parentcode,
                created_at=date.today()) 
                if search_ids:
                    search_ids.delete()

            result = {'status': status.HTTP_200_OK , "message": "Deleted Succesfully", 'error': False}
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
    


class TopupproductViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TopupproductSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  
    
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            if not self.request.user.is_authenticated:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            if not fmspw:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            site = fmspw[0].loginsite
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            queryset = DepositAccount.objects.filter(Cust_Codeid=cust_id, type='Deposit', 
            outstanding__gt=0).order_by('pk')
            sum = 0; lst = []
            header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
            "topup_amount" : "0.00","new_outstanding" : "0.00"}

            system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()

            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Topup',
            value_name='Other Outlet Customer Topup',isactive=True).first()
           
                
            if queryset:
                for q in queryset:
                    # ,type__in=('Deposit', 'Top Up')
                    acc_ids = DepositAccount.objects.filter(ref_transacno=q.sa_transacno,
                    ref_productcode=q.treat_code).order_by('sa_date','sa_time','id').last()
                    if acc_ids:
                        acc = DepositAccount.objects.filter(pk=acc_ids.pk)
                        serializer = self.get_serializer(acc, many=True)
                        if acc_ids and acc_ids.outstanding > 0.0:
                            for data in serializer.data:
                                pos_haud = PosHaud.objects.none()
                                if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                                    if acc_ids.site_code != site.itemsite_code or acc_ids.site_code == site.itemsite_code:
                                        pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,
                                        sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                                else:
                                    if acc_ids.site_code == site.itemsite_code: 
                                        pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                                        sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()


                               
                                if pos_haud:
                                    sum += data['outstanding']
                                    data['DepositAccountid'] = q.pk
                                    data["pay_amount"] = None
                                    data['transaction_code'] = pos_haud.sa_transacno_ref     
                                    data['stock_id'] = acc_ids.Item_Codeid.pk
                                    if data["balance"]:
                                        data["balance"] = "{:.2f}".format(float(data['balance']))
                                    else:
                                        data["balance"] = "0.00"    
                                    if data["outstanding"]:
                                        data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                                    else:
                                        data["outstanding"] = "0.00"    
                                    lst.append(data)    

                if lst != []:
                    header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "{:.2f}".format(float(sum)),
                    "topup_amount" : None,"new_outstanding" : "{:.2f}".format(float(sum))}
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                    return Response(result, status=status.HTTP_200_OK)   
                else:
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': []}
                    return Response(result, status=status.HTTP_200_OK)

            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)           


class TopupprepaidViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class =  TopupprepaidSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  
    
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            if not self.request.user.is_authenticated:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            if not fmspw:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            site = fmspw[0].loginsite
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()

            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Topup',
            value_name='Other Outlet Customer Topup',isactive=True).first()
           
                    
            # queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno_type="Receipt",
            # ItemSite_Codeid__pk=site.pk)
            queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno_type="Receipt")
            sum = 0; lst = []
            header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
            "topup_amount" : "0.00","new_outstanding" : "0.00"}
            if queryset:
                for q in queryset:
                    # daud = PosDaud.objects.filter(sa_transacno=q.sa_transacno,
                    # ItemSite_Codeid__pk=site.pk)
                    daud = PosDaud.objects.filter(sa_transacno=q.sa_transacno)
                    for d in daud:
                        pacc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,sa_status='DEPOSIT',
                        cust_code=cust_obj.cust_code,pos_daud_lineno=d.dt_lineno,outstanding__gt = 0)

                        if pacc_ids:
                            if int(d.dt_itemnoid.item_div) == 3 and d.dt_itemnoid.item_type == 'PACKAGE':
                                acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,package_code=d.dt_combocode,
                                pos_daud_lineno=d.dt_lineno,outstanding__gt = 0,status=True).order_by('id').last()
                            else:
                                acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,
                                pos_daud_lineno=d.dt_lineno,outstanding__gt = 0,status=True).order_by('id').last()

                            
                            if acc_ids:
                                acc = PrepaidAccount.objects.filter(pk=acc_ids.pk)
                                serializer = self.get_serializer(acc, many=True)
                        
                                for data in serializer.data:
                                    pos_haud = PosHaud.objects.none()
                                    if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                                        if acc_ids.site_code != site.itemsite_code or acc_ids.site_code == site.itemsite_code:
                                            pos_haud = PosHaud.objects.filter(sa_custnoid=cust_obj,
                                            sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                                    else:
                                        if acc_ids.site_code == site.itemsite_code: 
                                            pos_haud = PosHaud.objects.filter(sa_custnoid=cust_obj,ItemSite_Codeid__pk=site.pk,
                                            sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                                   
                                    if pos_haud:
                                        sum += data['outstanding']
                                        splt = str(data['exp_date']).split('T')
                                        if data['exp_date']:
                                            data['exp_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                                        data['transaction_code'] = pos_haud.sa_transacno_ref
                                        data['prepaid_id']  = acc_ids.pk

                                        if int(d.dt_itemnoid.item_div) == 3 and d.dt_itemnoid.item_type == 'PACKAGE':
                                            data['stock_id'] = acc_ids.Item_Codeid.pk
                                        else:
                                            data['stock_id'] = d.dt_itemnoid.pk

                                        data["pay_amount"] = None
                                        if data["remain"]:
                                            data["remain"] = "{:.2f}".format(float(data['remain']))
                                        if data["outstanding"]:
                                            data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                                        lst.append(data)    

                header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "{:.2f}".format(float(sum)),
                "topup_amount" : None,"new_outstanding" : "{:.2f}".format(float(sum))}
                if lst != []:
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                else:
                    result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK)    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)           


class ReversalListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentReversalSerializer

    def list(self, request):
        try:
            treatment_id = self.request.GET.get('treatment_id',None)
            if treatment_id is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            if not fmspw:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            site = fmspw[0].loginsite
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            treat_id = treatment_id.split(',')
            sum = 0; lst = []; count = 0 ; tot_balance = 0 ; tot_credit = 0; checklst = [];total=0
            for i in treat_id:
                count +=1
                # queryset = Treatment.objects.filter(pk=i,status='Open',site_code=site.itemsite_code).order_by('-pk')
                queryset = Treatment.objects.filter(pk=i,status='Open').order_by('-pk')
                if queryset:
                    # type__in=('Deposit', 'Top Up','CANCEL')
                    #acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                    #treatment_parentcode=queryset[0].treatment_parentcode,Site_Codeid=queryset[0].Site_Codeid).order_by('id').last()
                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                    treatment_parentcode=queryset[0].treatment_parentcode).order_by('sa_date','sa_time','id').last()
                    serializer = self.get_serializer(queryset, many=True)
                    for data in serializer.data:
                        if queryset[0].treatment_parentcode not in checklst:
                            checklst.append(queryset[0].treatment_parentcode)
                            if acc_ids:
                                tot_balance += acc_ids.balance if acc_ids.balance else 0
                            
                            if acc_ids.balance:
                                if float(acc_ids.balance) > float(queryset[0].unit_amount):
                                    tot_credit += queryset[0].unit_amount
                                elif float(acc_ids.balance) <= float(queryset[0].unit_amount):
                                    tot_credit += acc_ids.balance
                        
                        if count == 1:
                            outstanding = acc_ids.outstanding
                            
                        if acc_ids:
                            if outstanding >= queryset[0].unit_amount:
                                tamount = queryset[0].unit_amount
                                balance = acc_ids.balance
                                outstanding = outstanding - queryset[0].unit_amount
                                total += 0
                            elif queryset[0].unit_amount > outstanding and outstanding > 0:
                                tamount = queryset[0].unit_amount 
                                remaining = queryset[0].unit_amount - outstanding
                                if remaining > 0:
                                    balance = acc_ids.balance - remaining
                                    total += remaining
                                outstanding = 0    
                            else:
                                if queryset[0].unit_amount > 0 and outstanding == 0:
                                    tamount = queryset[0].unit_amount
                                    outstanding = outstanding
                                    balance = acc_ids.balance - queryset[0].unit_amount
                                    total += queryset[0].unit_amount

                        data['no'] = count
                        sum += data['unit_amount']
                        data['unit_amount'] = "{:.2f}".format(float(data['unit_amount']))
                        lst.append(data) 
                else:
                    result = {'status': status.HTTP_200_OK,"message":"Treatment ID does not exist/Not in Open Status!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
            
            # print(total,"total")
            if lst != []:
                control_obj = ControlNo.objects.filter(control_description__iexact="Reverse No",Site_Codeid=site).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reverse Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                rev_code = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                header_data = {"reverse_no" : rev_code, "total" : "{:.2f}".format(float(sum)),
                "total_depobalance" : "{:.2f}".format(float(tot_balance)),"total_credit" : "{:.2f}".format(float(tot_credit)),
                "creditnote_amt": "{:.2f}".format(float(total))}
                
                # if self.request.GET.get('adjustment',None) is not None:
                #     header_data["creditnote_after_adjustment"] = "Null"
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                return Response(result, status=status.HTTP_200_OK)     
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)      
    
    @transaction.atomic
    def create(self, request):
        try:
            with transaction.atomic():
                if not self.request.user.is_authenticated:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                today_date = timezone.now().date()
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                if not fmspw:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                site = fmspw[0].loginsite
                if not site:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                treatment_id = self.request.GET.get('treatment_id',None)
                if treatment_id is None:
                    result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
                
                recontrol_obj = ControlNo.objects.filter(control_description__iexact="Reverse No",Site_Codeid=site).first()
                if not recontrol_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reverse Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                rev_code = str(recontrol_obj.control_prefix)+str(recontrol_obj.Site_Codeid.itemsite_code)+str(recontrol_obj.control_no)
                
                control_obj = ControlNo.objects.filter(control_description__iexact="Reference Credit Note No",Site_Codeid=site).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reverse Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                credit_code = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)

                fmspw = fmspw.first()
                treat_id = treatment_id.split(',')

                treat_obj = Treatment.objects.filter(pk=treat_id[0]).order_by('-pk').first()
                
                flexirev_setup = Systemsetup.objects.filter(title='FlexiRedeemAllowReversal',
                value_name='FlexiRedeemAllowReversal',isactive=True).first()
                if flexirev_setup and flexirev_setup.value_data == 'True': 
                    if treat_obj and treat_obj.type in ['FFd','FFi']:
                        done_ids = Treatment.objects.filter(treatment_parentcode=treat_obj.treatment_parentcode,status="Done").order_by('pk').count()
                        if done_ids > 0:
                            result = {'status': status.HTTP_400_BAD_REQUEST,
                            "message":"Reversal Not possible for FFi/FFd already have treatment done!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)

                # print(treat_id,"treat_id")
                sum = 0; lst = [];total = 0;trm_lst = [];total_r = 0.0;rea_obj = False
                
                if treat_id:
                    for i in treat_id:
                        #queryset = Treatment.objects.filter(pk=i,status='Open',site_code=site.itemsite_code).order_by('-pk')
                        queryset = Treatment.objects.filter(pk=i,status='Open').order_by('-pk')
                        if not queryset:
                            result = {'status': status.HTTP_200_OK,"message":"Treatment ID does not exist/Not in Open Status!!",'error': True} 
                            return Response(data=result, status=status.HTTP_200_OK) 
                        
                        # type__in=('Deposit', 'Top Up','CANCEL')
                        #acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                        #treatment_parentcode=queryset[0].treatment_parentcode,Site_Codeid=queryset[0].Site_Codeid).order_by('id').last()
                        acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                        treatment_parentcode=queryset[0].treatment_parentcode).order_by('sa_date','sa_time','id').last()

                        # if acc_ids.balance == 0.0:
                        #     result = {'status': status.HTTP_200_OK,"message":"Treatment Account for this customer is Zero so cant create Credit Note!!",'error': True} 
                        #     return Response(data=result, status=status.HTTP_200_OK) 


                        j = queryset.first()
                        #treatment update
                        j.status = 'Cancel'
                        j.transaction_time = timezone.now()
                        j.save()

                        # cust_obj = Customer.objects.filter(cust_code=j.cust_code,cust_isactive=True).first()
                        cust_obj = j.Cust_Codeid

                        # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,itemsite_code=site.itemsite_code,
                        # sa_transacno=j.sa_transacno).first()
                        pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                        sa_transacno=j.sa_transacno).first()


                        val = {'invoice': "Credit for Invoice Number : "+str(pos_haud.sa_transacno_ref) if pos_haud and pos_haud.sa_transacno_ref else "",
                        'desc':j.course,'amount':j.unit_amount}
                        trm_lst.append(val)
                        total_r += j.unit_amount
                        
                        
                        #reversedtl creation
                        reversedtl = ReverseDtl(treatment_no=j.treatment_code,treatment_desc=j.course,
                        treatment_price=j.unit_amount,transac_no=j.sa_transacno,reverse_no=rev_code,
                        site_code=j.site_code)
                        reversedtl.save()

                        desc = "CANCEL" +" "+ str(j.course)+" "+str(j.times)+"/"+str(j.treatment_no)
                        #treatment Account creation 
                        # if acc_ids.balance > queryset[0].unit_amount: 
                        #     balance = acc_ids.balance - queryset[0].unit_amount 
                        #     tamount =  queryset[0].unit_amount
                        #     total += j.unit_amount
                        # elif acc_ids.balance <= queryset[0].unit_amount:  
                        #     balance = acc_ids.balance - acc_ids.balance  
                        #     tamount = acc_ids.balance 
                        #     total += acc_ids.balance

                        # tamount = Treatmentaccount account Field
                        # balance = Treatmentaccount balance Field
                        # outstanding = Treatmentaccount outstanding Field
                        # total = creditnote amount & balance
                        
                        # print(acc_ids.outstanding,"acc_ids.outstanding")
                        # print(queryset[0].unit_amount,"queryset[0].unit_amount")

                        if acc_ids.outstanding >= queryset[0].unit_amount:
                            # print("iff")
                            tamount = queryset[0].unit_amount
                            balance = acc_ids.balance
                            outstanding = acc_ids.outstanding - queryset[0].unit_amount
                            total += 0
                        elif queryset[0].unit_amount > acc_ids.outstanding and acc_ids.outstanding > 0:
                            # print("elif")
                            tamount = queryset[0].unit_amount 
                            remaining = queryset[0].unit_amount - acc_ids.outstanding
                            if remaining > 0:
                                balance = acc_ids.balance - remaining
                                total += remaining
                            outstanding = 0    
                        else:
                            # print("else")
                            if queryset[0].unit_amount > 0 and acc_ids.outstanding == 0:
                                tamount = queryset[0].unit_amount
                                outstanding = acc_ids.outstanding
                                balance = acc_ids.balance - queryset[0].unit_amount
                                total += queryset[0].unit_amount

                        treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                        description=desc,ref_no=j.treatment_parentcode,type='CANCEL',amount=-float("{:.2f}".format(float(tamount))) if tamount else 0,
                        balance="{:.2f}".format(float(balance)),User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=j.sa_transacno,
                        sa_transacno="",qty=1,outstanding="{:.2f}".format(float(outstanding)) if acc_ids and acc_ids.outstanding is not None and acc_ids.outstanding > 0 else 0,deposit=None,treatment_parentcode=j.treatment_parentcode,
                        sa_status="VT",cas_name=fmspw.pw_userlogin,sa_staffno=acc_ids.sa_staffno,sa_staffname=acc_ids.sa_staffname,
                        dt_lineno=j.dt_lineno,Site_Codeid=site,
                        site_code=j.site_code)
                        treatacc.save()
                        treatacc.sa_date = today_date
                        treatacc.save()
                                
                    #creditnote creation  
                    creditnote = CreditNote(treatment_code=j.treatment_parentcode,treatment_name=j.course,
                    treatment_parentcode=j.treatment_parentcode,type="CANCEL",cust_code=j.cust_code,
                    cust_name=j.cust_name,sa_transacno=j.sa_transacno,status="OPEN",
                    credit_code=credit_code,deposit_type="TREATMENT",site_code=j.site_code,
                    treat_code=j.treatment_parentcode)
                    creditnote.save()
                    creditnote.sa_date = today_date
                    creditnote.save()
                    if creditnote.pk:
                        control_obj.control_no = int(control_obj.control_no) + 1
                        control_obj.save()
                        if creditnote.pk not in lst:
                            lst.append(creditnote.pk)

                        PackageAuditingLog(treatment_parentcode=j.treatment_parentcode,
                        user_loginid=fmspw,package_type="Reversal",pa_qty=len(treat_id)).save()    



                    #reversehdr creation
                    reversehdr = ReverseHdr(reverse_no=rev_code,staff_code="",staff_name="",
                    cust_code=j.cust_code,cust_name=j.cust_name,site_code=j.site_code,
                    ref_creditnote=creditnote.credit_code,total_balance=total)

                    reversehdr.save()
                    reversehdr.reverse_date = today_date
                    reversehdr.save()
                    if reversehdr.pk:
                        recontrol_obj.control_no = int(recontrol_obj.control_no) + 1
                        recontrol_obj.save()

                    print(total,"total") 
                    if self.request.GET.get('adjustment_value',None) and float(self.request.GET.get('adjustment_value',None)) != 0.0:
                        amount = self.request.GET.get('adjustment_value',None)
                        # print(amount,"amount")
                        # print(float(amount),"float(amount)")


                        reversehdr.has_adjustment = True  
                        reversehdr.adjustment_value = amount 
                        split = str(amount).split('-')
                        if '-' in split:
                            reversehdr.credit_note_amt = total - float(amount)
                            creditnote.amount = total - float(amount)
                            creditnote.balance = total - float(amount)
                        else:
                            reversehdr.credit_note_amt = total + float(amount)
                            creditnote.amount = total + float(amount)
                            creditnote.balance = total + float(amount)

                        if creditnote.amount == 0.0 and creditnote.balance == 0.0:     
                            creditnote.status = "CLOSE"
                            
                        creditnote.save()
                        if self.request.GET.get('reason_id',None):
                            rea_obj = ReverseTrmtReason.objects.filter(id=self.request.GET.get('reason_id',None),
                            is_active=True)

                            if not rea_obj:
                                result = {'status': status.HTTP_200_OK,"message":"Reason ID does not exist!!",'error': True} 
                                return Response(data=result, status=status.HTTP_200_OK)  

                            reversehdr.reason = rea_obj[0].rev_desc

                            if rea_obj and rea_obj[0].rev_no == '100001':
                                if rea_obj:
                                    reversehdr.reason1 = rea_obj[0].rev_desc 
                                if amount:
                                    reversehdr.reason_adj_value1 = amount

                        

                        if self.request.GET.get('remark',None):
                            reversehdr.remark = self.request.GET.get('remark',None)

                       
                        reversehdr.save()

                        if creditnote.amount < 0 and float(amount) < 0:
                            raise Exception("Credit Note value cannot be negative!!")
                            
                    else:
                        creditnote.amount = total
                        creditnote.balance = total
                        if creditnote.amount == 0.0 and creditnote.balance == 0.0:     
                            creditnote.status = "CLOSE"
                        creditnote.save() 
                        reversehdr.credit_note_amt = total
                        reversehdr.save()

                if treat_obj:
                    searcids = TreatmentPackage.objects.filter(treatment_parentcode=treat_obj.treatment_parentcode).first()
                    if searcids:
                        stptdone_ids = Treatment.objects.filter(treatment_parentcode=treat_obj.treatment_parentcode,status="Done").order_by('pk').count()
                        stptcancel_ids = Treatment.objects.filter(treatment_parentcode=treat_obj.treatment_parentcode,status="Cancel").order_by('pk').count()
                        stptopen_ids = Treatment.objects.filter(treatment_parentcode=treat_obj.treatment_parentcode,status="Open").order_by('pk').count()
                        
                        trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=treat_obj.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                      
                        searcids.open_session = stptopen_ids
                        searcids.done_session = stptdone_ids
                        searcids.cancel_session = stptcancel_ids

                        searcids.balance = "{:.2f}".format(float(trmtAccObj.balance)) 
                        searcids.outstanding = "{:.2f}".format(float(trmtAccObj.outstanding))
                        # searcids.treatmentids = treatmids
                        searcids.save()
                        treatmids = list(set(Treatment.objects.filter(
                        treatment_parentcode=treat_obj.treatment_parentcode).filter(~Q(status="Open")).only('pk').order_by('pk').values_list('pk', flat=True).distinct()))

                        Treatmentids.objects.filter(treatment_parentcode=treat_obj.treatment_parentcode,
                        treatment_int__in=treatmids).delete()

                        p_ids = list(set(Treatmentids.objects.filter(treatment_parentcode=treat_obj.treatment_parentcode).values_list('treatment_int', flat=True).distinct()))
                        op_ids = list(Treatment.objects.filter(
                        treatment_parentcode=treat_obj.treatment_parentcode).filter(Q(status="Open"),~Q(pk__in=p_ids)).only('pk').order_by('pk').values_list('pk', flat=True).distinct())
                        if op_ids:
                            for j in op_ids:
                                stf_ids = Treatmentids.objects.filter(treatment_int=j)
                                if not stf_ids: 
                                    Treatmentids(treatment_parentcode=treat_obj.treatment_parentcode,
                                                treatment_int=j).save()
        
                
            
                if lst != [] and trm_lst != []:
                    title = Title.objects.filter(product_license=site.itemsite_code).first()

                    credit_ids = CreditNote.objects.filter(pk__in=lst).order_by('pk')
                        

                    path = None
                    if title and title.logo_pic:
                        path = BASE_DIR + title.logo_pic.url

                    split = str(credit_ids[0].sa_date).split(" ")
                    date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime("%d/%m/%Y")
                    adjustamt = self.request.GET.get('adjustment_value',None)
                    remark = self.request.GET.get('remark',None)
                    if adjustamt:
                        total_credit = float(total_r) + float(adjustamt)
                    else:
                        total_credit = float(total_r)


                    data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
                    'address': title.trans_h2 if title and title.trans_h2 else '', 
                    'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
                    'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
                    'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
                    'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
                    'credit_ids': credit_ids[0], 'date':date,'total':total_r,'credit_balance': reversehdr.total_balance,'adjustamt':adjustamt if adjustamt else "",
                    'reason':reversehdr.reason if reversehdr.reason else "",'remark':remark if remark else "",'total_credit':reversehdr.credit_note_amt,
                    'credit': trm_lst,'cust': cust_obj,'creditno': credit_ids[0].credit_code,'fmspw':fmspw,'adjustamtstr': "0.00",
                    'path':path if path else '','title':title if title else None,
                    }

                    template = get_template('creditnote.html')
                    display = Display(visible=0, size=(800, 600))
                    display.start()
                    html = template.render(data)
                    options = {
                        'margin-top': '.25in',
                        'margin-right': '.25in',
                        'margin-bottom': '.25in',
                        'margin-left': '.25in',
                        'encoding': "UTF-8",
                        'no-outline': None,
                        
                    }

                    dst ="creditnote_" + str(str(credit_ids[0].credit_code)) + ".pdf"

                    p=pdfkit.from_string(html,False,options=options)
                    PREVIEW_PATH = dst
                    pdf = FPDF() 

                    pdf.add_page() 
                    
                    pdf.set_font("Arial", size = 15) 
                    file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                    pdf.output(file_path) 

                    if p:
                        file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                        report = os.path.isfile(file_path)
                        if report:
                            file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                            with open(file_path, 'wb') as fh:
                                fh.write(p)
                            display.stop()

                            # ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/creditnote_"+str(credit_ids[0].credit_code)+".pdf"
                            ip_link = str(SITE_ROOT) + "pdf/creditnote_"+str(credit_ids[0].credit_code)+".pdf"

                            result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False,
                            'data': ip_link}
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed to create ", 'error': False}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def creditprint(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            
            site = fmspw[0].loginsite
            if not request.data['credit_id']:
                result = {'status': status.HTTP_200_OK,"message":"Please Give Credit Note id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 

            credit_id = request.data['credit_id']
            # credit_obj = CreditNote.objects.filter(pk=credit_id,site_code=site.itemsite_code).order_by('pk').first()
            credit_obj = CreditNote.objects.filter(pk=credit_id).order_by('pk').first()
            # print(credit_obj,"credit_obj")
            if not credit_obj:
                result = {'status': status.HTTP_200_OK,"message":"Credit note does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 

            title = Title.objects.filter(product_license=site.itemsite_code).first()

                
            path = None
            if title and title.logo_pic:
                path = BASE_DIR + title.logo_pic.url

            split = str(credit_obj.sa_date).split(" ")
            date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime("%d/%m/%Y")
            # print(credit_obj.credit_code,"credit_obj.credit_code")
            
            
            trm_lst = [] ; total_r = 0 
            # rev_ids = ReverseHdr.objects.filter(site_code=site.itemsite_code,ref_creditnote=credit_obj.credit_code).order_by('pk').first() 
            rev_ids = ReverseHdr.objects.filter(ref_creditnote=credit_obj.credit_code).order_by('pk').first()   
            # print(rev_ids,"rev_ids")
            if rev_ids:
                # dtl_ids = ReverseDtl.objects.filter(reverse_no=rev_ids.reverse_no,site_code=site.itemsite_code).order_by('pk')
                dtl_ids = ReverseDtl.objects.filter(reverse_no=rev_ids.reverse_no).order_by('pk')
                # print(dtl_ids,"dtl_ids")
                for j in dtl_ids:
                    # pos_haud = PosHaud.objects.filter(sa_custno=rev_ids.cust_code,itemsite_code=site.itemsite_code,
                    # sa_transacno=j.transac_no).first()
                    pos_haud = PosHaud.objects.filter(sa_custno=rev_ids.cust_code,
                    sa_transacno=j.transac_no).first()
                    # print(pos_haud,"pos_haud")

                    if pos_haud:
                        val = {'invoice': "Credit for Invoice Number : "+str(pos_haud.sa_transacno_ref),
                        'desc':j.treatment_desc,'amount':j.treatment_price}
                        trm_lst.append(val)  
                        total_r += j.treatment_price  

               

                data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else '', 
                'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
                'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
                'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
                'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
                'credit_ids': credit_obj, 'date':date,'total':total_r,'adjustamt':rev_ids.adjustment_value if rev_ids.adjustment_value else "",
                'credit_balance' : rev_ids.total_balance if rev_ids.total_balance else "",
                'reason':rev_ids.reason if rev_ids.reason else "",'remark':rev_ids.remark if rev_ids.remark else "",
                'total_credit': rev_ids.credit_note_amt if rev_ids.credit_note_amt else "",
                'credit': trm_lst,'creditno': credit_obj.credit_code,'fmspw':fmspw,
                'adjustamtstr': "0.00",
                'path':path if path else '','title':title if title else None,
                }

                template = get_template('creditnote.html')
                display = Display(visible=0, size=(800, 600))
                display.start()
                html = template.render(data)
                options = {
                    'margin-top': '.25in',
                    'margin-right': '.25in',
                    'margin-bottom': '.25in',
                    'margin-left': '.25in',
                    'encoding': "UTF-8",
                    'no-outline': None,
                    
                }

                dst ="creditnote_" + str(str(credit_obj.credit_code)) + ".pdf"

                p=pdfkit.from_string(html,False,options=options)
                PREVIEW_PATH = dst
                pdf = FPDF() 

                pdf.add_page() 
                
                pdf.set_font("Arial", size = 15) 
                file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                pdf.output(file_path) 

                if p:
                    file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                    report = os.path.isfile(file_path)
                    if report:
                        file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                        with open(file_path, 'wb') as fh:
                            fh.write(p)
                        display.stop()

                        # ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/creditnote_"+str(credit_obj.credit_code)+".pdf"
                        ip_link = str(SITE_ROOT)+"pdf/creditnote_"+str(credit_obj.credit_code)+".pdf"

                        result = {'status': status.HTTP_200_OK, "message": "Printed Successfully", 'error': False,
                        'data': ip_link}
                        return Response(data=result, status=status.HTTP_200_OK)

            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Reverse Header does not exist", 'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
             


class ShowBalanceViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ShowBalanceSerializer

    def list(self, request):
        try:
            treatment_id = self.request.GET.get('treatment_id',None)
            if treatment_id is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite     

            treat_id = treatment_id.split(',')
            checklst = []; lst = []; sum = 0
            for i in treat_id:
                #q = Treatment.objects.filter(pk=i,status='Open',site_code=site.itemsite_code)
                q = Treatment.objects.filter(pk=i,status='Open')
                if not q:
                    result = {'status': status.HTTP_200_OK,"message":"Treatment ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
                
                # 'Deposit', 'Top Up','CANCEL')
                #acc_ids = TreatmentAccount.objects.filter(ref_transacno=q[0].sa_transacno,
                #treatment_parentcode=q[0].treatment_parentcode,Site_Codeid=q[0].Site_Codeid).order_by('id').last()
                acc_ids = TreatmentAccount.objects.filter(ref_transacno=q[0].sa_transacno,
                treatment_parentcode=q[0].treatment_parentcode).order_by('sa_date','sa_time','id').last()
                if q[0].treatment_parentcode not in checklst:
                    reverse_amt = 0
                    reverse_amt += q[0].unit_amount
                    checklst.append(q[0].treatment_parentcode)
                    queryset = TreatmentAccount.objects.filter(pk=acc_ids.pk)
                    if queryset:
                        serializer = self.get_serializer(queryset, many=True)
                        for data in serializer.data:
                            if data['balance']:
                                data['balance'] = "{:.2f}".format(float(data['balance']))
                            if data["outstanding"]:    
                                data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                            dict_v = dict(data)
                            lst.append(dict_v) 
                else:
                    if q[0].treatment_parentcode in checklst:
                        reverse_amt += q[0].unit_amount
    
                for l in lst:
                    if str(l['treatment_parentcode']) == q[0].treatment_parentcode:
                        l['reverse_price'] = "{:.2f}".format(float(reverse_amt))
                        
            if lst != []:
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': lst}
                return Response(result, status=status.HTTP_200_OK)     
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


class ReverseTrmtReasonAPIView(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ReverseTrmtReason.objects.filter(is_active=True).order_by('id')
    serializer_class = ReverseTrmtReasonSerializer

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


def sa_transacno_update_void(self, site, fmspw):
    # return True
    sacontrol_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw.loginsite.pk).first()
    if not sacontrol_obj:
        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
    # haudre = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('sa_transacno')
    haudre = PosTaud.objects.filter(ItemSIte_Codeid__pk=site.pk).values('sa_transacno').distinct().order_by('-pk','-sa_transacno')[:2]
    haudfinal = list(set([r['sa_transacno'] for r in haudre]))
    code_site = site.itemsite_code
    prefix_s = sacontrol_obj.control_prefix

    silicon = 5
    system_setup = Systemsetup.objects.filter(title='Controlnoslice',value_name='Controlnoslice',isactive=True).first()
    if system_setup and system_setup.value_data: 
        silicon = int(system_setup.value_data)
      

    slst = []
    if haudfinal != []:
        for fh in haudfinal:
            # Yoonus remove MC1 and Mc2
            fhstr = fh 
            if 'MC1' in fh:
                fhstr = fh.replace("MC1","")
            if 'MC2' in fh:    
                fhstr = fh.replace("MC2","")
            if 'T1' in fh:    
                fhstr = fh.replace("T1","")
            if 'T2' in fh:     
                fhstr = fh.replace("T2","")
            if 'T3' in fh:     
                fhstr = fh.replace("T3","")

            # fhstr = int(fh[silicon:])
            fhstr = int(fhstr[silicon:])
            # fhstr = fh.replace(prefix_s,"")
            # fhnew_str = fhstr.replace(code_site, "")
            slst.append(fhstr)
            slst.sort(reverse=True)

        # print(slst,"slst")
        sa_id = int(slst[0]) + 1
        # sa_id = int(slst[0][-6:]) + 1

        sacontrol_obj.control_no = str(sa_id)
        sacontrol_obj.save() 
    return True                      


class VoidViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = PosHaud.objects.filter(isvoid=False).order_by('-pk')
    serializer_class = VoidSerializer

    def get_queryset(self):
        cust_code = self.request.GET.get('cust_code',None)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        customer = Customer.objects.filter(pk=cust_code,cust_isactive=True).order_by('pk').last()

        # void = False
        # system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
        # value_name='Other Outlet Customer Listings',isactive=True).first()

        # system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Void',
        # value_name='Other Outlet Customer Void',isactive=True).first()
        # if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
        #     if customer.site_code != site.itemsite_code or customer.site_code == site.itemsite_code:
        #         void = True
        # else:
        #     if customer.site_code == site.itemsite_code:
        #         void = True
    
        # year = date.today().year
        # month = date.today().month
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)
        transac_no = self.request.GET.get('transac_no',None)
        
        cust_name = self.request.GET.get('cust_name',None)
        queryset = PosHaud.objects.none()

        # if void == True:
        # queryset = PosHaud.objects.filter(isvoid=False,
        # ItemSite_Codeid__pk=site.pk).order_by('-pk')
        queryset = PosHaud.objects.filter(isvoid=False,
        ).order_by('-pk')
        if not from_date and not to_date and not transac_no and not cust_code and not cust_name:
            queryset = queryset
        else:
            if from_date and to_date: 
                queryset = queryset.filter(Q(sa_date__date__gte=from_date,sa_date__date__lte=to_date)).order_by('-pk')
            
            if transac_no:
                queryset = queryset.filter(sa_transacno_ref__icontains=transac_no).order_by('-pk')
            if cust_code:
                # customer = Customer.objects.filter(pk=cust_code,cust_isactive=True,site_code=site.itemsite_code).last()
                customer = Customer.objects.filter(pk=cust_code,cust_isactive=True).last()
                if customer:
                    queryset = queryset.filter(sa_custno__icontains=customer.cust_code).order_by('-pk')
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Logined Site Customer Doesn't Exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if cust_name:
                queryset = queryset.filter(sa_custname__icontains=cust_name).order_by('-pk')
        return queryset

    def list(self, request):
        try:
            if str(self.request.GET.get('cust_code',None)) != "undefined":
                if isinstance(int(self.request.GET.get('cust_code',None)), int):
                    cust_code = self.request.GET.get('cust_code',None)
                    cust_obj = Customer.objects.filter(pk=cust_code,cust_isactive=True).last()
                    serializer_class = VoidSerializer
                    queryset = self.filter_queryset(self.get_queryset())
                    total = len(queryset)
                    state = status.HTTP_200_OK
                    message = "Listed Succesfully"
                    error = False
                    data = None
                    result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                    v = result.get('data')
                    d = v.get('dataList')
                    lst = []
                    for dat in d:
                        dict_d = dict(dat)
                        if dict_d['sa_date']:
                            splt = str(dict_d['sa_date']).split('T')
                            dict_d['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        lst.append(dict_d)
                    v['dataList'] =  lst  
                    result['cust'] = {'cust_name': cust_obj.cust_name if cust_obj and cust_obj.cust_name else "",
                    'cust_refer' : cust_obj.cust_refer if cust_obj and cust_obj.cust_refer else ""}
                    return Response(result, status=status.HTTP_200_OK)   
            else:
                result = {'status': status.HTTP_200_OK,"message":"No Data",'error': False, "data":[]}
                return Response(data=result, status=status.HTTP_200_OK)   
        except Exception as e:
           invalid_message = str(e)
           return general_error_response(invalid_message)
               

    @action(detail=False, methods=['get'], name='Details', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def Details(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            poshdr_id = self.request.GET.get('poshdr_id',None)
            # if not isinstance(poshdr_id, int):
            #     result = {'status': status.HTTP_200_OK,"message":"Poshaud ID Should be Integer only!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_200_OK)

            # haud_obj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
            # ItemSite_Codeid__pk=site.pk).first()
            haud_obj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
            ).first()
            if haud_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"PosHaud ID Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            # cust_obj = Customer.objects.filter(cust_code=haud_obj.sa_custno,cust_isactive=True,
            # site_code=site.itemsite_code).first()
            cust_obj = Customer.objects.filter(cust_code=haud_obj.sa_custno,cust_isactive=True).order_by('-pk').first()

            # daud_ids = PosDaud.objects.filter(sa_transacno=haud_obj.sa_transacno,
            # ItemSite_Codeid__pk=site.pk) 
            daud_ids = PosDaud.objects.filter(sa_transacno=haud_obj.sa_transacno,
            )
            if daud_ids:
                serializer = PosDaudDetailsSerializer(daud_ids, many=True)
                for data in serializer.data:
                    data['dt_amt'] = "{:.2f}".format(float(data['dt_amt']))
                    data['cust_noid'] = cust_obj.pk
                    data['cart_id'] = haud_obj.cart_id

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
           invalid_message = str(e)
           return general_error_response(invalid_message)
                   

    @transaction.atomic
    def create(self, request):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
            
                poshdr_id = self.request.GET.get('poshdr_id',None)
                # poshdrid = poshdr_id.split(',')
                # for i in poshdrid:
                # haud_obj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
                # ItemSite_Codeid__pk=site.pk).first()
                haud_obj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
                ).first()
                if haud_obj is None:
                    result = {'status': status.HTTP_200_OK,"message":"PosHaud ID Does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK)

                gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()

                # for p in poshdrid:
                # haudobj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
                # ItemSite_Codeid__pk=site.pk).first()
                haudobj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
                ).first()
                if haudobj.cart_id:
                    ids_cart = ItemCart.objects.filter(isactive=True,cart_id=haudobj.cart_id,
                    sitecode=site.itemsite_code,cart_date=date.today(),
                    cust_noid__pk=haud_obj.sa_custnoid.pk).exclude(type__in=type_tx)
                    if ids_cart:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Cart is Created!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        haudobj.cart_id = None
                        haudobj.save()
                        ids_cartold = ItemCart.objects.filter(cart_id=haudobj.cart_id,cart_status="Inprogress",
                        sitecode=site.itemsite_code,cust_noid__pk=haud_obj.sa_custnoid.pk).exclude(type__in=type_tx).delete()

                # daud_ids = PosDaud.objects.filter(sa_transacno=haudobj.sa_transacno,
                # ItemSite_Codeid__pk=site.pk) 
                daud_ids = PosDaud.objects.filter(sa_transacno=haudobj.sa_transacno,
                )
                lineno = 0
                control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                silicon = 6
                system_setup = Systemsetup.objects.filter(title='ICControlnoslice',value_name='ICControlnoslice',isactive=True).first()
                if system_setup and system_setup.value_data: 
                    silicon = int(system_setup.value_data)
          
                
                #cartre = ItemCart.objects.filter(sitecodeid=site).order_by('cart_id')
                cartre = ItemCart.objects.filter(sitecodeid=site).order_by('-cart_id')[:2]
                final = list(set([r.cart_id for r in cartre]))
                # print(final,len(final),"final")
                code_site = site.itemsite_code
                prefix = control_obj.control_prefix

                lst = []
                if final != []:
                    for f in final:
                        fhstr = int(f[silicon:])
                        # newstr = f.replace(prefix,"")
                        # new_str = newstr.replace(code_site, "")
                        lst.append(fhstr)
                        lst.sort(reverse=True)

                    # print(lst,"lst")
                    c_no = int(lst[0]) + 1
                    # c_no = int(lst[0][-6:]) + 1

                    cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(c_no)
                else:
                    cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)

                haudobj.cart_id = cart_id
                haudobj.save()
                
                cart_lst = []
                # print(daud_ids, "daud_ids")
                for d in daud_ids:
                    # print(d.itemcart,"d.itemcart")
                    if d.itemcart:
                        lineno += 1
                        if lineno == 1:
                            check = "New"
                        else:
                            check = "Old"

                        cust_obj = Customer.objects.filter(pk=d.itemcart.cust_noid.pk,cust_isactive=True).first()
                        # stock_obj = Stock.objects.filter(pk=d.itemcart.itemcodeid.pk,item_isactive=True).first()
                        stock_obj = Stock.objects.filter(pk=d.itemcart.itemcodeid.pk).first()
                        
                        tax_value = 0.0
                        if stock_obj.is_have_tax == True:
                            tax_value = gst.item_value if gst and gst.item_value else 0.0
                        
                        if d.itemcart.type == "Deposit":
                            type = "VT-Deposit"
                        elif d.itemcart.type == "Top Up":
                            type = "VT-Top Up" 
                        elif d.itemcart.type == "Sales":
                            type = "VT-Sales"
                        else:
                            type = d.itemcart.type            

                        cart = ItemCart(cart_date=date.today(),phonenumber=cust_obj.cust_phone2,
                        customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                        itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=d.itemcart.itemdesc if d.itemcart and d.itemcart.itemdesc else stock_obj.item_desc,
                        quantity=d.itemcart.quantity,price="{:.2f}".format(float(d.itemcart.price)),
                        sitecodeid=site,sitecode=site.itemsite_code,
                        cart_status="Inprogress",cart_id=cart_id,item_uom=d.itemcart.item_uom,
                        tax="{:.2f}".format(tax_value),check=check,ratio=d.itemcart.ratio,
                        discount=d.itemcart.discount,discount_amt=d.itemcart.discount_amt,
                        additional_discount=d.itemcart.additional_discount,
                        additional_discountamt=d.itemcart.additional_discountamt,
                        discount_price=d.itemcart.discount_price,total_price=d.itemcart.total_price,
                        trans_amt=d.itemcart.trans_amt,deposit=d.itemcart.deposit,type=type,
                        itemstatus=d.itemcart.itemstatus,remark=d.itemcart.remark,
                        discreason_txt=d.itemcart.discreason_txt,focreason=d.itemcart.focreason,
                        holditemqty=d.itemcart.holditemqty,holdreason=d.itemcart.holdreason,
                        done_sessions=d.itemcart.done_sessions,treatment_account=d.itemcart.treatment_account,
                        treatment=d.itemcart.treatment,deposit_account=d.itemcart.deposit_account,
                        prepaid_account=d.itemcart.prepaid_account)
                        cart.save()
                        # print("saved cart")
                        for s in d.itemcart.sales_staff.all(): 
                            cart.sales_staff.add(s)

                        for se in d.itemcart.service_staff.all(): 
                            cart.service_staff.add(se)

                        for h in d.itemcart.helper_ids.all(): 
                            cart.helper_ids.add(h)    
                        
                        for dis in d.itemcart.disc_reason.all(): 
                            cart.disc_reason.add(dis)
                        
                        for po in d.itemcart.pos_disc.all(): 
                            cart.pos_disc.add(po)

                        if cart.pk:
                            if cart.pk not in cart_lst:
                                cart_lst.append(cart.pk)
                # print(len(cart_lst),"lencart")
                # print(len(daud_ids),"lendaud")
                if cart_lst != [] and len(cart_lst) == len(daud_ids):
                    result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False,'data':cart_id}
                    return Response(data=result, status=status.HTTP_200_OK)
                else:
                    return general_error_response("posdaud records not available")
                    
        except Exception as e:
           invalid_message = str(e)
           return general_error_response(invalid_message)
                     
    
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def VoidReturn(self, request):
        try:
            with transaction.atomic():
                global type_tx
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
                cart_date = timezone.now().date()

                cart_id = self.request.GET.get('cart_id',None)
                if not cart_id:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID parms not given!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                
                #This Transaction already VOID, no permission allow
                cartobj_ids = ItemCart.objects.filter(isactive=True,cart_id=cart_id,
                sitecode=site.itemsite_code,cart_date=date.today(),cart_status="Inprogress").exclude(type__in=type_tx)
                if not cartobj_ids or cartobj_ids is None:
                    result = {'status': status.HTTP_200_OK,"message":"Cart ID Does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK)

                cartnew_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid__pk=site.pk,
                customercode=cartobj_ids[0].customercode).exclude(type__in=type_tx)
                if cartnew_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done for this Customer!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    

                gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()

                # haudobj = PosHaud.objects.filter(cart_id=cart_id,isvoid=False,
                # ItemSite_Codeid__pk=site.pk,sa_custnoid=cartobj_ids[0].cust_noid).first()
                haudobj = PosHaud.objects.filter(cart_id=cart_id,isvoid=False,
                sa_custnoid=cartobj_ids[0].cust_noid).first()
              
                if not haudobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"sa transacno does not exist in Poshaud!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                # daud_ids = PosDaud.objects.filter(sa_transacno=haudobj.sa_transacno,
                # ItemSite_Codeid__pk=site.pk)
                daud_ids = PosDaud.objects.filter(sa_transacno=haudobj.sa_transacno,
                )
                # taud_ids = PosTaud.objects.filter(sa_transacno=haudobj.sa_transacno,
                # ItemSIte_Codeid__pk=site.pk)
                taud_ids = PosTaud.objects.filter(sa_transacno=haudobj.sa_transacno,
                )
                multi_ids = Multistaff.objects.filter(sa_transacno=haudobj.sa_transacno)

                for dj in daud_ids:
                    cart_obj = ItemCart.objects.filter(isactive=True,cart_id=cart_id,lineno=dj.dt_lineno,
                    sitecode=site.itemsite_code,cart_date=date.today(),cart_status="Inprogress",
                    cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx).first()
                    if not cart_obj:
                        raise Exception("Item Cart ID Does not exist!!")

                        

                control_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                voidreason_id = self.request.GET.get('voidreason_id',None)
                void_obj = VoidReason.objects.filter(pk=voidreason_id,isactive=True)
                if void_obj is None:
                    raise Exception("VoidReason ID Does not exist!!")
                      

                #haudre = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('sa_transacno')
                # haudre = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('-id')[:2]
                # haudre = PosTaud.objects.filter(ItemSIte_Codeid__pk=site.pk).values('sa_transacno').distinct().order_by('-pk','-sa_transacno')[:2]
                # final = list(set([r['sa_transacno'] for r in haudre]))
                # # print(final,len(final),"final")
                # saprefix = control_obj.control_prefix
                # code_site = site.itemsite_code
        
                # lst = []
                # if final != []:
                #     for f in final:
                #         # print(f,"ff")
                #         newstr = f.replace(saprefix,"")
                #         new_str = newstr.replace(code_site, "")
                #         lst.append(new_str)
                #         lst.sort(reverse=True)

                #     # print(lst,"lst")
                #     sa_no = int(lst[0]) + 1
                #     # print(lst[0][-6:],"lst[0][-6:]")
                #     # sa_no = int(lst[0][-6:]) + 1
                #     # print(sa_no,"sa_no")


                #     sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(sa_no)
                #     # print(sa_transacno,"ref")
                # else:
                #     sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)

                refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference VOID No",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                if not refcontrol_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference VOID Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                tp_controlobj = ControlNo.objects.filter(control_description__iexact="TopUp",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                if not tp_controlobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"TopUp Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                
                sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                control_obj.control_no = int(control_obj.control_no) + 1
                control_obj.save() 

                # sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
                # poshaud_ids = PosHaud.objects.filter(sa_transacno=sa_transacno,sa_custno=haudobj.sa_custno,
                # ItemSite_Codeid__pk=site.pk,sa_transacno_ref=sa_transacno_ref)
                # if poshaud_ids:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Void sa transacno Already Created!!",'error': True} 
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                # print("here1")

                sa_count = 1

                while sa_count > 0:
                    poshaud_v = PosHaud.objects.filter(sa_transacno=sa_transacno)
                    posdaud_v = PosDaud.objects.filter(sa_transacno=sa_transacno)
                    postaud_v = PosTaud.objects.filter(sa_transacno=sa_transacno)
                
                    if poshaud_v or posdaud_v or postaud_v:    
                        newcontrol_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw.loginsite.pk).first()
                        sa_transacno = str(newcontrol_obj.control_prefix)+str(newcontrol_obj.Site_Codeid.itemsite_code)+str(newcontrol_obj.control_no)
                        newcontrol_obj.control_no = int(newcontrol_obj.control_no) + 1
                        newcontrol_obj.save() 
                        sa_count += 1
                    else:
                        sa_count = 0   


                sa_ref_count = 1    
                if refcontrol_obj:
                    satransacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
                    
                    while sa_ref_count > 0:
                        poshaud_vref = PosHaud.objects.filter(sa_transacno_ref=satransacno_ref)
                        if poshaud_vref:
                            refcontrol_obj.control_no = int(refcontrol_obj.control_no) + 1
                            refcontrol_obj.save()
                            satransacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
                            sa_ref_count += 1
                        else:
                            sa_ref_count = 0

 
                poshaudids = PosHaud.objects.filter(sa_transacno=sa_transacno,sa_custno=haudobj.sa_custno)
                if poshaudids:
                    raise Exception("PosHaud Void sa transacno Already Created!!")
                    

                pos_haud_ids = PosHaud.objects.filter(sa_transacno=sa_transacno,sa_custno=haudobj.sa_custno,
                ItemSite_Codeid__pk=site.pk)
                if pos_haud_ids:
                    raise Exception("PosHaud Void sa transacno Already Created!!")
                   
                   
                posdaud_ids = PosDaud.objects.filter(sa_transacno=sa_transacno,
                ItemSite_Codeid__pk=site.pk)
                if posdaud_ids:
                    raise Exception("PosDaud Already Created!!")
                   
                for ctl in cartnew_ids:
                    #,itemcart__pk=ctl.pk
                    pos_daud_ids = PosDaud.objects.filter(sa_transacno=sa_transacno,dt_itemnoid__pk=ctl.itemcodeid.pk,
                    ItemSite_Codeid__pk=site.pk,dt_lineno=ctl.lineno)
                    if pos_daud_ids:
                        raise Exception("PosDaud Void Already Created!!")
                       
                
                     
                finalsatrasc  = False
                if haudobj.sa_transacno_type in ['Receipt','Non Sales','Redeem Service']:
                    for i in daud_ids:
                        if int(i.itemcart.itemcodeid.item_div) == 5:
                            if i.itemcart.type == 'Deposit':
                                check_ids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,
                                cust_code=haudobj.sa_custno,line_no=i.dt_lineno,use_amt__gt=0,sa_status="SA")
                                if check_ids:
                                    msg = "Can't do void prepaid product line no {0} has use amount".format(str(i.dt_lineno))
                                    raise Exception(msg)
                        
                        if int(i.itemcart.itemcodeid.item_div) == 1:
                            if i.itemcart.type == 'Deposit':
                                close_ids = Holditemdetail.objects.filter(sa_transacno=haudobj.sa_transacno,status='CLOSE',hi_lineno=i.dt_lineno)
                                if close_ids:
                                    pmsg = "Can't do void retail product line no {0} has hold item issued close record is there".format(str(i.dt_lineno))
                                    raise Exception(pmsg)

                                open_hoids = Holditemdetail.objects.filter(sa_transacno=haudobj.sa_transacno,hi_lineno=i.dt_lineno)
                                if len(open_hoids) > 1:
                                    pmsg = "Can't do void retail product line no {0} has hold item issued record is there".format(str(i.dt_lineno))
                                    raise Exception(pmsg)

                                void_hoids = Holditemdetail.objects.filter(sa_transacno=haudobj.sa_transacno,status='VOID',hi_lineno=i.dt_lineno)
                                if void_hoids:
                                    p_msg = "Can't do void retail product line no {0} has hold item already voided".format(str(i.dt_lineno))
                                    raise Exception(p_msg)
                        
                        if int(i.itemcart.itemcodeid.item_div) == 3:
                            if i.itemcart.type == 'Deposit':
                                
                                ihelper_ids = list(set(ItemHelper.objects.filter(helper_transacno=haudobj.sa_transacno,
                                line_no=i.dt_lineno).values_list('item_code', flat=True).distinct()))
                                # print(ihelper_ids,"ihelper_ids")
                                donetreatids = Treatment.objects.filter(sa_transacno=haudobj.sa_transacno,
                                cust_code=haudobj.sa_custno,status='Done',dt_lineno=i.dt_lineno).filter(~Q(treatment_code__in=ihelper_ids))
                                # print(donetreatids,"donetreatids")
                                if donetreatids:
                                    p_msg = "Can't do void Service line no {0} has Treatment Redeem Done status".format(str(i.dt_lineno))
                                    raise Exception(p_msg)




                    # print(sa_transacno,"sa_transacno")
                    for t in taud_ids:
                          
                        taud = PosTaud(sa_transacno=sa_transacno,pay_groupid=t.pay_groupid,pay_group=t.pay_group,
                        pay_typeid=t.pay_typeid,pay_type=t.pay_type,pay_desc=t.pay_desc,pay_tendamt=t.pay_tendamt,
                        pay_tendrate=t.pay_tendrate,pay_tendcurr=t.pay_tendcurr,pay_amt=-t.pay_amt,pay_amtrate=t.pay_amtrate,
                        pay_amtcurr=t.pay_amtcurr,pay_rem1=t.pay_rem1,pay_rem2=t.pay_rem2,pay_rem3=t.pay_rem3,pay_rem4=t.pay_rem4,
                        pay_status=t.pay_status,pay_actamt=-t.pay_actamt,ItemSIte_Codeid=t.ItemSIte_Codeid,
                        itemsite_code=t.itemsite_code,paychange=t.paychange,dt_lineno=t.dt_lineno,
                        pay_gst_amt_collect=-t.pay_gst_amt_collect,pay_gst=-t.pay_gst,posdaudlineno=t.posdaudlineno,
                        billed_by=t.billed_by,subtotal=-t.subtotal,tax=-t.tax,
                        discount_amt=-t.discount_amt,billable_amount=-t.billable_amount,credit_debit=t.credit_debit,
                        points=t.points,prepaid=t.prepaid,pay_premise=t.pay_premise,is_voucher=t.is_voucher,
                        )
                        taud.save()
                        taud.sa_date = cart_date
                        taud.save()

                        #prepaid   
                        if str(t.pay_type).upper() == 'PP':
                            spltn = str(t.pay_rem1).split("-")
                            ppno = spltn[0]
                            lineno = spltn[1]

                            depoprepaid_ids = PrepaidAccount.objects.filter(pp_no=ppno,line_no=lineno,
                            cust_code=haudobj.sa_custno,sa_status='DEPOSIT').order_by('-pk').first()

                            last_preids = PrepaidAccount.objects.filter(pp_no=ppno,line_no=lineno,
                            cust_code=haudobj.sa_custno).order_by('-pk').first()
                            if last_preids:
                                last_preids.status=False
                                last_preids.save()

                                remain = float(last_preids.remain) + float(t.pay_amt)

                                prepacc = PrepaidAccount(pp_no=last_preids.pp_no,pp_type=last_preids.pp_type,
                                pp_desc=last_preids.pp_desc,exp_date=last_preids.exp_date,cust_code=last_preids.cust_code,
                                cust_name=last_preids.cust_name,pp_amt=last_preids.pp_amt,pp_total=last_preids.pp_total,
                                pp_bonus=last_preids.pp_bonus,transac_no=sa_transacno,item_no=depoprepaid_ids.item_no if depoprepaid_ids and depoprepaid_ids.item_no else None,use_amt=0,
                                remain=remain,ref1=last_preids.ref1,ref2=last_preids.ref2,status=True,site_code=site.itemsite_code,sa_status="VT",exp_status=last_preids.exp_status,
                                voucher_no=last_preids.voucher_no,isvoucher=last_preids.isvoucher,has_deposit=last_preids.has_deposit,topup_amt=0,
                                outstanding=last_preids.outstanding if last_preids and last_preids.outstanding is not None and last_preids.outstanding > 0 else 0,active_deposit_bonus=last_preids.active_deposit_bonus,topup_no="",topup_date=None,
                                line_no=last_preids.line_no,staff_name=None,staff_no=None,
                                pp_type2=last_preids.pp_type2,condition_type1=last_preids.condition_type1,pos_daud_lineno=last_preids.line_no,Cust_Codeid=last_preids.Cust_Codeid,Site_Codeid=last_preids.Site_Codeid,
                                Item_Codeid=depoprepaid_ids.Item_Codeid if depoprepaid_ids and depoprepaid_ids.Item_Codeid else None,
                                item_code=depoprepaid_ids.item_code if depoprepaid_ids and depoprepaid_ids.item_code else None)
                                prepacc.save()
                                prepacc.sa_date = cart_date
                                prepacc.start_date = cart_date
                                prepacc.save()

                                pacc_ids = PrepaidAccountCondition.objects.filter(pp_no=ppno,
                                pos_daud_lineno=lineno).only('pp_no','pos_daud_lineno').first()
                                if pacc_ids:                                
                                    acc = PrepaidAccountCondition.objects.filter(pk=pacc_ids.pk).update(use_amt=0,remain=remain)

                            vtlast_preids = PrepaidAccount.objects.filter(pp_no=ppno,line_no=lineno,
                            cust_code=haudobj.sa_custno,transac_no=haudobj.sa_transacno).order_by('-pk')
                            if vtlast_preids:
                                for v in vtlast_preids:
                                    v.sa_status = "VT"
                                    v.save()

                            # # pac_ids = PrepaidAccount.objects.filter(transac_no=haudobj.sa_transacno,sa_status='SA',
                            # # cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                            # pac_ids = PrepaidAccount.objects.filter(transac_no=t.sa_transacno,sa_status='SA',
                            # cust_code=haudobj.sa_custno)
                            # # pac_ids = PrepaidAccount.objects.filter(Q(pp_no=d.sa_transacno) | Q(topup_no=d.sa_transacno) | Q(topup_no=d.sa_transacno),
                            # # sa_status='SA',cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                            # # print(pac_ids,"pac_ids")
                            # for pa in pac_ids:
                            #     remain = float(pa.remain) + float(pa.use_amt)
                            #     # pac_lastid = PrepaidAccount.objects.filter(pp_no=pa.pp_no,line_no=pa.line_no,
                            #     # cust_code=haudobj.sa_custno,site_code=site.itemsite_code,status=True).first()
                            #     pac_lastid = PrepaidAccount.objects.filter(pp_no=pa.pp_no,line_no=pa.line_no,
                            #     cust_code=haudobj.sa_custno,status=True).first()


                            #     if pac_lastid:
                            #         # print(pac_lastid.pp_no,"pp_no")
                            #         remain = float(pac_lastid.remain) + float(pa.use_amt)
                            #         # PrepaidAccount.objects.filter(pk=pac_lastid.pk).update(status=False)
                            #         PrepaidAccount.objects.filter(pp_no=pa.pp_no,line_no=pa.line_no).update(status=False)

                            #     pacc_ids = PrepaidAccountCondition.objects.filter(pp_no=pa.pp_no,
                            #     pos_daud_lineno=pa.line_no).only('pp_no','pos_daud_lineno').first()
                            #     if pacc_ids:                                
                            #         cuseamt = float(pacc_ids.use_amt) - float(pa.use_amt)
                            #         acc = PrepaidAccountCondition.objects.filter(pk=pacc_ids.pk).update(use_amt=cuseamt,remain=remain)

                            #     useamt = 0 - float(pa.use_amt)
                            #     prepacc = PrepaidAccount(pp_no=pa.pp_no,pp_type=pa.pp_type,
                            #     pp_desc=pa.pp_desc,exp_date=pa.exp_date,cust_code=pa.cust_code,
                            #     cust_name=pa.cust_name,pp_amt=pa.pp_amt,pp_total=pa.pp_total,
                            #     pp_bonus=pa.pp_bonus,transac_no=pa.transac_no,item_no=pa.item_no,use_amt=useamt,
                            #     remain=remain,ref1=pa.ref1,ref2=pa.ref2,status=True,site_code=site.itemsite_code,sa_status="VT",exp_status=pa.exp_status,
                            #     voucher_no=pa.voucher_no,isvoucher=pa.isvoucher,has_deposit=pa.has_deposit,topup_amt=0,
                            #     outstanding=pa.outstanding if pa and pa.outstanding is not None and pa.outstanding > 0 else 0,active_deposit_bonus=pa.active_deposit_bonus,topup_no="",topup_date=None,
                            #     line_no=pa.line_no,staff_name=None,staff_no=None,
                            #     pp_type2=pa.pp_type2,condition_type1=pa.condition_type1,pos_daud_lineno=pa.line_no,Cust_Codeid=pa.Cust_Codeid,Site_Codeid=pa.Site_Codeid,
                            #     Item_Codeid=pa.Item_Codeid,item_code=pa.item_code)
                            #     prepacc.save()

                                

                        #print(t.pay_desc,"pay_desc")
                        #creditnote
                        if str(t.pay_type).upper() == 'CN':
                            crdobj = CreditNote.objects.filter(credit_code=t.pay_rem1,cust_code=haudobj.sa_custno).first()
                            #print(haudobj.sa_custno,"customer")
                            if crdobj:
                                crbalance = float(crdobj.balance) + float(t.pay_amt)
                                #print(crbalance,"crbalance")
                                if crbalance == 0.0:
                                    crstatus = "CLOSE"
                                elif crbalance < 0.0:
                                    crstatus = "CLOSE" 
                                    crbalance = 0.0   
                                elif crbalance > 0.0:
                                    crstatus = "OPEN"    
                                CreditNote.objects.filter(pk=crdobj.pk).update(balance=crbalance,status=crstatus)
                        
                        #voucher
                        if str(t.pay_type).upper() == 'VC':
                            crdobj = VoucherRecord.objects.filter(voucher_no=t.pay_rem1,cust_code=haudobj.sa_custno).first()
                            #print(t.pay_rem1,"Voucher Reset")
                            if crdobj:
                                VoucherRecord.objects.filter(pk=crdobj.pk).update(isvalid=True,used=False)


                    for m in multi_ids:
                        multi =  Multistaff(sa_transacno=sa_transacno,item_code=m.item_code,emp_code=m.emp_code,
                        ratio=m.ratio,salesamt=-float("{:.2f}".format(float(m.salesamt))) if m.salesamt else 0,type=m.type,isdelete=m.isdelete,role=m.role,dt_lineno=m.dt_lineno,
                        level_group_code=m.level_group_code) 
                        multi.save()
                    
                    for d in daud_ids:
                        cart_obj = ItemCart.objects.filter(isactive=True,cart_id=cart_id,lineno=d.dt_lineno,
                        sitecode=site.itemsite_code,cart_date=date.today(),cart_status="Inprogress",
                        cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx).first()
                        
                        topup_outstanding = d.topup_outstanding
                        if d.itemcart.type == 'Top Up':
                            topup_outstanding = d.topup_outstanding + d.dt_price

                        sales = "";service = ""
                        if cart_obj.sales_staff.all():
                            for i in cart_obj.sales_staff.all():
                                if sales == "":
                                    sales = sales + i.display_name
                                elif not sales == "":
                                    sales = sales +","+ i.display_name
                        if cart_obj.service_staff.all(): 
                            for s in cart_obj.service_staff.all():
                                if service == "":
                                    service = service + s.display_name
                                elif not service == "":
                                    service = service +","+ s.display_name 
                        
                        if d.record_detail_type == "TD":
                            daud_staffs = "/"+" "+ service
                        else:
                            daud_staffs = sales +" "+"/"+" "+ service

                        
                        daud = PosDaud(sa_transacno=sa_transacno,dt_status="VT",dt_itemnoid=d.dt_itemnoid,
                        dt_itemno=d.dt_itemno,dt_itemdesc=d.dt_itemdesc,dt_price=d.dt_price,dt_promoprice="{:.2f}".format(float(d.dt_promoprice)),
                        dt_amt=-float("{:.2f}".format(float(d.dt_amt))),dt_qty=-d.dt_qty,dt_discamt=-d.dt_discamt if float(d.dt_discamt) > 0.0 else d.dt_discamt,
                        dt_discpercent=-d.dt_discpercent if float(d.dt_discpercent) > 0.0 else d.dt_discpercent,
                        dt_discdesc=d.dt_discdesc,dt_discno=d.dt_discno,dt_remark=d.dt_remark,dt_Staffnoid=d.dt_Staffnoid,
                        dt_staffno=d.dt_staffno,dt_staffname=d.dt_staffname,dt_discuser="",
                        dt_combocode=d.dt_combocode,ItemSite_Codeid=d.ItemSite_Codeid,itemsite_code=d.itemsite_code,
                        dt_lineno=d.dt_lineno,
                        dt_uom=d.dt_uom,isfoc=d.isfoc,item_remarks=None,
                        dt_transacamt="{:.2f}".format(float(d.dt_transacamt)),dt_deposit=-float("{:.2f}".format(float(d.dt_deposit))) if d.dt_deposit else 0,
                        holditemqty=d.holditemqty,st_ref_treatmentcode='',
                        item_status_code=d.item_status_code,first_trmt_done=d.first_trmt_done,first_trmt_done_staff_code=d.first_trmt_done_staff_code,
                        first_trmt_done_staff_name=d.first_trmt_done_staff_name,record_detail_type=d.record_detail_type,
                        trmt_done_staff_code=d.trmt_done_staff_code,trmt_done_staff_name=d.trmt_done_staff_name,
                        trmt_done_id=d.trmt_done_id,trmt_done_type=d.trmt_done_type,topup_service_trmt_code=d.topup_service_trmt_code,
                        topup_product_treat_code=d.topup_product_treat_code,topup_prepaid_trans_code=d.topup_prepaid_trans_code,
                        topup_prepaid_type_code=d.topup_prepaid_type_code,
                        gst_amt_collect=-float("{:.2f}".format(float(d.gst_amt_collect))) if d.gst_amt_collect else 0,
                        topup_prepaid_pos_trans_lineno=d.topup_prepaid_pos_trans_lineno,
                        topup_outstanding=topup_outstanding if topup_outstanding is not None and topup_outstanding > 0 else 0,
                        itemcart=cart_obj,
                        staffs=daud_staffs)
                        
                        daud.save()
                        daud.sa_date = cart_date
                        daud.save()


                        if int(d.itemcart.itemcodeid.item_div) == 3:
                            if d.itemcart.type == 'Deposit':
                                donetreat_ids = Treatment.objects.filter(sa_transacno=haudobj.sa_transacno,
                                cust_code=haudobj.sa_custno,status='Done',dt_lineno=d.dt_lineno)
                                for treat_obj in donetreat_ids:   

                                    ihelper_ids = ItemHelper.objects.filter(helper_transacno=haudobj.sa_transacno,
                                    item_code=treat_obj.treatment_code)
                                    for hlp in ihelper_ids:
                                        itmp = ItemHelper(item_code=hlp.item_code,item_name=hlp.item_name,line_no=hlp.line_no,
                                        sa_transacno=hlp.sa_transacno,amount=-hlp.amount,helper_name=hlp.helper_name,
                                        helper_code=hlp.helper_code,site_code=hlp.site_code,share_amt=-hlp.share_amt,
                                        helper_transacno=sa_transacno,
                                        wp1=hlp.wp1,wp2=hlp.wp2,wp3=hlp.wp3,times=hlp.times,
                                        treatment_no=hlp.treatment_no)
                                        itmp.save()
                                        ItemHelper.objects.filter(id=itmp.id).update(sa_date= date.today())
                                       

                                    # accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
                                    # treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
                                    # type="Sales").order_by('id').first()
                                    accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
                                    treatment_parentcode=treat_obj.treatment_parentcode,ref_no=treat_obj.treatment_code,
                                    type="Sales").order_by('id').first()


                                    if accids:
                                        usagelevel_ids = Usagelevel.objects.filter(service_code=treat_obj.service_itembarcode,
                                        isactive=True).order_by('-pk')
                                        for i in usagelevel_ids:
                                            # instance = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                                            # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno,line_no=1,
                                            # usage_status="Usage",uom=i.uom,item_code=i.item_code).order_by('line_no').first() 
                                            instance = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                                            sa_transacno=accids.sa_transacno,line_no=1,
                                            usage_status="Usage",uom=i.uom,item_code=i.item_code).order_by('line_no').first() 


                                            # print(instance,"instance")
                                            if instance :
                                                now = datetime.datetime.now()
                                                s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))
                                
                                                instance.isactive = False
                                                instance.usage_update = s1
                                                instance.save()
                                                # useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                                                # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno,uom=i.uom,item_code=i.item_code).order_by('line_no') 
                                                useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                                                sa_transacno=accids.sa_transacno,uom=i.uom,item_code=i.item_code).order_by('line_no') 

                                                rec = useids.last()
                                                lineno = float(rec.line_no) + 1    

                                            
                                                TreatmentUsage(treatment_code=instance.treatment_code,item_code=instance.item_code,
                                                item_desc=instance.item_desc,qty=-instance.qty,uom=instance.uom,site_code=instance.site_code,
                                                usage_status="Void TD",line_no=lineno,void_line_ref=1,usage_update=s1,
                                                sa_transacno=instance.sa_transacno,isactive=False).save()
                                                
                                                #ItemBatch
                                                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                                                item_code=instance.item_code[:-4],uom=instance.uom).order_by('pk').last()
                                                
                                                if batch_ids:
                                                    addamt = batch_ids.qty + instance.qty
                                                    batch_ids.qty = addamt
                                                    batch_ids.updated_at = timezone.now()
                                                    batch_ids.save()

                                                    #Stktrn
                                                
                                                    currenttime = timezone.now()
                                                    currentdate = timezone.now().date()

                                                    post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                                                    
                                                
                                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                                                    itemcode=instance.item_code,store_no=site.itemsite_code,
                                                    tstore_no=None,fstore_no=None,trn_docno=instance.treatment_code,
                                                    trn_type="Void Usage",trn_db_qty=None,trn_cr_qty=None,
                                                    trn_qty=instance.qty,trn_balqty=addamt,trn_balcst=None,
                                                    trn_amt=None,trn_cost=None,trn_ref=None,
                                                    hq_update=0,line_no=instance.line_no,item_uom=instance.uom,
                                                    item_batch=None,mov_type=None,item_batch_cost=None,
                                                    stock_in=None,trans_package_line_no=None,trn_post=currentdate,
                                                    trn_date=currentdate).save()
                                

                                #acc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Deposit',
                                #cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                                acc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Deposit',
                                cust_code=haudobj.sa_custno,dt_lineno=d.dt_lineno)
                                for acc in acc_ids:
                                    TreatmentAccount.objects.filter(pk=acc.pk).update(sa_status="VOID",updated_at=timezone.now())   
                                
                                #treat_ids = Treatment.objects.filter(sa_transacno=haudobj.sa_transacno,
                                #cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                                treat_ids = Treatment.objects.filter(sa_transacno=haudobj.sa_transacno,
                                cust_code=haudobj.sa_custno,dt_lineno=d.dt_lineno)
                                for trt in treat_ids:
                                    Treatment.objects.filter(pk=trt.pk).update(status="Cancel",sa_status="VOID")

                                
                                
                                #sal_acc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                                #cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                                sal_acc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                                cust_code=haudobj.sa_custno,dt_lineno=d.dt_lineno)
                                for sal in sal_acc_ids:
                                    TreatmentAccount.objects.filter(pk=sal.pk).update(description=d.itemcart.itemcodeid.item_name,sa_status="VOID",updated_at=timezone.now())   
                                    appt_ids = Appointment.objects.filter(sa_transacno=sal.ref_transacno,
                                    treatmentcode=sal.ref_no,itemsite_code=site.itemsite_code).update(appt_status="Cancelled")
                                    master_ids = Treatment_Master.objects.filter(sa_transacno=sal.ref_transacno,
                                    treatment_code=sal.ref_no,site_code=site.itemsite_code).update(status="Cancel")
                                
                                if treat_ids:
                                    p_ids = list(set(treat_ids.values_list('treatment_parentcode', flat=True).distinct()))
                                    if p_ids:
                                        for p in p_ids:
                                            searc_ids = TreatmentPackage.objects.filter(treatment_parentcode=p).first()
                                            if searc_ids:
                                                stptdone_ids = Treatment.objects.filter(treatment_parentcode=p,status="Done").order_by('pk').count()
                                                stptcancel_ids = Treatment.objects.filter(treatment_parentcode=p,status="Cancel").order_by('pk').count()
                                                stptopen_ids = Treatment.objects.filter(treatment_parentcode=p,status="Open").order_by('pk').count()
                                                
                                                trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=p).order_by('-sa_date','-sa_time','-id').first()
                                              
                                                
                                                searc_ids.open_session = stptopen_ids
                                                searc_ids.done_session = stptdone_ids
                                                searc_ids.cancel_session = stptcancel_ids
                                                
                                                searc_ids.balance = "{:.2f}".format(float(trmtAccObj.balance)) 
                                                searc_ids.outstanding = "{:.2f}".format(float(trmtAccObj.outstanding))
                                                # searc_ids.treatmentids = treatmids
                                                searc_ids.save()
                                                treatmids = list(set(Treatment.objects.filter(
                                                treatment_parentcode=p).filter(~Q(status="Open")).only('pk').order_by('pk').values_list('pk', flat=True).distinct()))

                                                Treatmentids.objects.filter(treatment_parentcode=p,
                                                treatment_int__in=treatmids).delete()
                                                
                                                p_ids = list(set(Treatmentids.objects.filter(treatment_parentcode=p).values_list('treatment_int', flat=True).distinct()))
                                                op_ids = list(Treatment.objects.filter(
                                                treatment_parentcode=p).filter(Q(status="Open"),~Q(pk__in=p_ids)).only('pk').order_by('pk').values_list('pk', flat=True).distinct())
                                                if op_ids:
                                                    for j in op_ids:
                                                        stf_ids = Treatmentids.objects.filter(treatment_int=j)
                                                        if not stf_ids: 
                                                            Treatmentids(treatment_parentcode=p,
                                                                        treatment_int=j).save()
                           
                
     

                                if d.dt_itemnoid.item_type == 'PACKAGE':
                                    #prepaid

                                    pacc_ids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,sa_status='DEPOSIT',
                                    cust_code=haudobj.sa_custno,line_no=d.dt_lineno)

                                    check_ids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,
                                    cust_code=haudobj.sa_custno,line_no=d.dt_lineno,use_amt__gt=0,sa_status="SA")
                                    if not check_ids: 
                                        for pa in pacc_ids:
                                            PrepaidAccount.objects.filter(pk=pa.pk).update(remain=0.0,status=False,sa_status="VT",updated_at=timezone.now(),
                                            cust_code=haudobj.sa_custno)

                                        paccids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,
                                        cust_code=haudobj.sa_custno,line_no=d.dt_lineno)

                                        for p in paccids:
                                            PrepaidAccount.objects.filter(pk=p.pk).update(status=False)
                                    
                                    #product

                                    dacc_ids = DepositAccount.objects.filter(sa_transacno=haudobj.sa_transacno,sa_status='SA',type='Deposit',
                                    cust_code=haudobj.sa_custno,dt_lineno=d.dt_lineno)
                        
                                    for depo in dacc_ids:
                                        tpcontrolobj = ControlNo.objects.filter(control_description__iexact="TopUp",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                                        
                                        tp_code = str(tpcontrolobj.control_prefix)+str(tpcontrolobj.Site_Codeid.itemsite_code)+str(tpcontrolobj.control_no)
                                    
                                        balance = depo.balance - depo.amount
                                        desc = "Cancel"+" "+"Product Amount : "+str("{:.2f}".format(float(depo.amount)))
                                        deps =DepositAccount(cust_code=depo.cust_code,type="CANCEL",amount=-float("{:.2f}".format(float(depo.amount))) if depo.amount else 0,balance="{:.2f}".format(float(balance)),
                                        user_name=depo.user_name,qty=depo.qty,outstanding=0.0,deposit="{:.2f}".format(float(depo.deposit)),
                                        cas_name=fmspw[0].pw_userlogin,sa_staffno=depo.sa_staffno,sa_staffname=depo.sa_staffname,
                                        deposit_type=depo.deposit_type,sa_transacno=depo.sa_transacno,description=desc,
                                        sa_status="VT",item_barcode=depo.item_barcode,item_description=depo.item_description,
                                        treat_code=depo.treat_code,void_link=depo.void_link,lpackage=depo.lpackage,
                                        package_code=depo.package_code,dt_lineno=depo.dt_lineno,Cust_Codeid=depo.Cust_Codeid,
                                        Site_Codeid=depo.Site_Codeid,site_code=depo.site_code,Item_Codeid=depo.Item_Codeid,
                                        item_code=depo.item_code,ref_transacno=depo.ref_transacno,ref_productcode=depo.ref_productcode,
                                        ref_code=tp_code)
                                        deps.save()
                                        deps.sa_date = cart_date
                                        deps.save()

                                        tpcontrolobj.control_no = int(tpcontrolobj.control_no) + 1
                                        tpcontrolobj.save()

                                    open_hoids = Holditemdetail.objects.filter(sa_transacno=haudobj.sa_transacno,hi_lineno=d.dt_lineno)
                                    for o in open_hoids:
                                        o.status = 'VOID'
                                        o.holditemqty = 0
                                        o.save()
                                      
                                    packdtl_ids = PackageDtl.objects.filter(package_code=d.dt_itemnoid.item_code,isactive=True)
                                    if packdtl_ids: 
                                        for pa in packdtl_ids:
                                            packdtl_code = str(pa.code)
                                            itm_code = packdtl_code[:-4]
                                            # print(itm_code,"itm_code")
                                            itmstock = Stock.objects.filter(item_code=itm_code).first()
                                            if itmstock:
                                                if int(itmstock.Item_Divid.itm_code) == 1:
                                                    #ItemBatch
                                                    batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                                                    item_code=itmstock.item_code,uom=pa.uom).order_by('pk').last()
                                                    if batch_ids:
                                                        addamt = batch_ids.qty + pa.qty
                                                        batch_ids.qty = addamt
                                                        batch_ids.save()
                                                        currenttime = timezone.now()
                                                        currentdate = timezone.now().date()
                                                        post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)

                                                        pa_trasac = pa.price * pa.qty
                                                        stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(itmstock.item_code)+"0000",
                                                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                                                        trn_type="VT",trn_db_qty=None,trn_cr_qty=None,trn_qty=pa.qty,trn_balqty=addamt,
                                                        trn_balcst=0,
                                                        trn_amt="{:.2f}".format(float(pa_trasac)),
                                                        trn_cost=0,trn_ref=None,
                                                        hq_update=0,
                                                        line_no=d.dt_lineno,item_uom=pa.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                        stock_in=None,trans_package_line_no=None,trn_post=currentdate,
                                                        trn_date=currentdate).save()

                                    #voucher
                                    voucher_ids = VoucherRecord.objects.filter(sa_transacno=haudobj.sa_transacno,
                                    cust_code=haudobj.sa_custno,dt_lineno=d.dt_lineno).order_by('pk')
                                    
                                    for vcc in voucher_ids:
                                        VoucherRecord.objects.filter(pk=vcc.pk).update(value=-vcc.value,updated_at=timezone.now(),isvalid=False)
            


                                
                            elif d.itemcart.type == 'Top Up':
                                #tacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Top Up',
                                #cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                                tacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Top Up',
                                cust_code=haudobj.sa_custno,treatment_parentcode=d.topup_service_trmt_code).first()

                                # for ac in tacc_ids:
                                if tacc_ids:
                                    ac = tacc_ids

                                    olaccids = TreatmentAccount.objects.filter(ref_transacno=ac.ref_transacno,
                                    treatment_parentcode=ac.treatment_parentcode).order_by('-id').first()
                                
                                    balance = olaccids.balance - ac.amount
                                    outstanding = olaccids.outstanding + ac.amount
                                    trt = TreatmentAccount(Cust_Codeid=ac.Cust_Codeid,cust_code=ac.cust_code,
                                    description=ac.description,ref_no=sa_transacno,type=ac.type,amount=-float("{:.2f}".format(float(ac.amount))) if ac.amount else 0,
                                    balance="{:.2f}".format(float(balance)),user_name=ac.user_name,User_Nameid=ac.User_Nameid,
                                    ref_transacno=ac.ref_transacno,sa_transacno=sa_transacno,qty=-ac.qty,
                                    outstanding="{:.2f}".format(float(outstanding)) if outstanding is not None and outstanding > 0 else 0,deposit=-float("{:.2f}".format(float(ac.deposit))) if ac.deposit else 0,treatment_parentcode=ac.treatment_parentcode,
                                    sa_status="VT",cas_name=ac.cas_name,sa_staffno=ac.sa_staffno,
                                    sa_staffname=ac.sa_staffname,
                                    dt_lineno=ac.dt_lineno,package_code=ac.package_code,Site_Codeid=ac.Site_Codeid,
                                    site_code=ac.site_code,itemcart=cart_obj)
                                    trt.save()
                                    trt.sa_date = cart_date
                                    trt.save()

                                    searcids = TreatmentPackage.objects.filter(treatment_parentcode=ac.treatment_parentcode).first()
                                    if searcids:
                                        trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=ac.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                                        searcids.balance = "{:.2f}".format(float(trmtAccObj.balance)) 
                                        searcids.outstanding = "{:.2f}".format(float(trmtAccObj.outstanding))
                                        searcids.save()
                                
                            elif d.itemcart.type == 'Sales':
                                #sacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                                #cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                                sacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                                cust_code=haudobj.sa_custno,treatment_parentcode=d.itemcart.treatment.treatment_parentcode)
                                # description = d.itemcart.itemcodeid.item_name+" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)
                                if d.itemcart and d.itemcart.itemdesc:
                                    description = d.itemcart.itemdesc+" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)
                                else:
                                    description = d.itemcart.itemcodeid.item_name+" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)

                                for i in d.itemcart.multi_treat.all():
                                    # if i.type in ['FFi','FFd']:
                                    #     if i.treatment_limit_times is not None and int(i.treatment_limit_times) == 0:
                                    #         # Treatment.objects.filter(pk=i.pk).update(course=description,status="Cancel",
                                    #         # trmt_room_code=None,treatment_count_done=0)
                                            
                                    #         # i.treatment_code = str(i.treatment_code)+"-"+"VT"
                                    #         # i.times =  str(i.times)+"-"+"VT"
                                    #         # i.treatment_no =  str(i.treatment_no)+"-"+"VT"
                                    #         i.course = description
                                    #         i.status = "Cancel"
                                    #         i.trmt_room_code = None
                                    #         i.treatment_count_done = 0
                                    #         i.save()
                                    #         ex_ids = Treatment.objects.filter(~Q(pk=i.pk),~Q(status='Cancel')).filter(treatment_parentcode=d.itemcart.treatment.treatment_parentcode,times__gt=i.times).order_by('pk')
                                    #         for e in ex_ids:
                                    #             tim = str(int(e.times) -1).zfill(2)
                                    #             tr_no = str(int(e.treatment_no) -1).zfill(2)
                                    #             e.times = tim
                                    #             e.treatment_no = tr_no
                                    #             e.treatment_code = str(d.itemcart.treatment.treatment_parentcode)+"-"+str(tim)
                                    #             e.save() 
                                    #         op_obj =Treatment.objects.filter(treatment_parentcode=i.treatment_parentcode,status='Open').order_by('-pk').first()    
                                    #         if op_obj:
                                    #             op_obj.unit_amount = i.unit_amount
                                    #             op_obj.save()
                                    #     else:
                                    #         Treatment.objects.filter(pk=i.pk).update(course=description,status="Open",
                                    #         trmt_room_code=None,treatment_count_done=0)

                                    # else:
                                    Treatment.objects.filter(pk=i.pk).update(course=description,status="Open",
                                    trmt_room_code=None,treatment_count_done=0)

                                    TmpItemHelper.objects.filter(treatment__pk=i.pk).delete()
                                    
                                    # ihelper_ids = ItemHelper.objects.filter(helper_transacno=haudobj.sa_transacno,site_code=site.itemsite_code)
                                    ihelper_ids = ItemHelper.objects.filter(helper_transacno=haudobj.sa_transacno,
                                    item_code=i.treatment_code)
                                    for hlp in ihelper_ids:
                                        itmp = ItemHelper(item_code=hlp.item_code,item_name=hlp.item_name,line_no=hlp.line_no,
                                        sa_transacno=hlp.sa_transacno,amount=-hlp.amount,helper_name=hlp.helper_name,
                                        helper_code=hlp.helper_code,site_code=hlp.site_code,share_amt=-hlp.share_amt,
                                        helper_transacno=sa_transacno,
                                        wp1=hlp.wp1,wp2=hlp.wp2,wp3=hlp.wp3,times=hlp.times,
                                        treatment_no=hlp.treatment_no)
                                        itmp.save()
                                        ItemHelper.objects.filter(id=itmp.id).update(sa_date= date.today())
                                      

                                    treat_obj = i
                                    accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
                                    treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
                                    type="Sales").order_by('id').first()

                                    if accids:
                                        usagelevel_ids = Usagelevel.objects.filter(service_code=treat_obj.service_itembarcode,
                                        isactive=True).order_by('-pk')
                                        for i in usagelevel_ids:
                                            # instance = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                                            # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno,line_no=1,
                                            # usage_status="Usage",uom=i.uom,item_code=i.item_code).order_by('line_no').first() 
 
                                            instance = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                                            sa_transacno=accids.sa_transacno,line_no=1,
                                            usage_status="Usage",uom=i.uom,item_code=i.item_code).order_by('line_no').first() 

                                            # print(instance,"instance")
                                            if instance:
                                                now = datetime.datetime.now()
                                                s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))
                                
                                                instance.isactive = False
                                                instance.usage_update = s1
                                                instance.save()

                                                # useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                                                # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno,uom=i.uom,item_code=i.item_code).order_by('line_no') 
                                                
                                                useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                                                sa_transacno=accids.sa_transacno,uom=i.uom,item_code=i.item_code).order_by('line_no') 


                                                rec = useids.last()
                                                lineno = float(rec.line_no) + 1    

                                            
                                                TreatmentUsage(treatment_code=instance.treatment_code,item_code=instance.item_code,
                                                item_desc=instance.item_desc,qty=-instance.qty,uom=instance.uom,site_code=instance.site_code,
                                                usage_status="Void TD",line_no=lineno,void_line_ref=1,usage_update=s1,
                                                sa_transacno=instance.sa_transacno,isactive=False).save()
                                                
                                                #ItemBatch
                                                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                                                item_code=instance.item_code[:-4],uom=instance.uom).order_by('pk').last()
                                                
                                                if batch_ids:
                                                    addamt = batch_ids.qty + instance.qty
                                                    batch_ids.qty = addamt
                                                    batch_ids.updated_at = timezone.now()
                                                    batch_ids.save()

                                                    #Stktrn
                                                
                                                    currenttime = timezone.now()
                                                    currentdate = timezone.now().date()

                                                    post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                                                    
                                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                                                    itemcode=instance.item_code,store_no=site.itemsite_code,
                                                    tstore_no=None,fstore_no=None,trn_docno=instance.treatment_code,
                                                    trn_type="Void Usage",trn_db_qty=None,trn_cr_qty=None,
                                                    trn_qty=instance.qty,trn_balqty=addamt,trn_balcst=None,
                                                    trn_amt=None,trn_cost=None,trn_ref=None,
                                                    hq_update=0,line_no=instance.line_no,item_uom=instance.uom,
                                                    item_batch=None,mov_type=None,item_batch_cost=None,
                                                    stock_in=None,trans_package_line_no=None,trn_post=currentdate,
                                                    trn_date=currentdate).save()

                                
                                for sa in sacc_ids:
                                    # print(sa,"SAAAAAAAAAAAAAAAAAAAAA")
                                    # master_ids = Treatment_Master.objects.filter(sa_transacno=sa.ref_transacno,
                                    # treatment_code=sa.ref_no,site_code=site.itemsite_code).update(status="Cancel")
                                    
                                    master_ids = Treatment_Master.objects.filter(sa_transacno=sa.ref_transacno,
                                    treatment_code=sa.ref_no).update(status="Cancel")
                                    

                                    # appt_ids = Appointment.objects.filter(sa_transacno=sa.ref_transacno,
                                    # treatmentcode=sa.ref_no,itemsite_code=site.itemsite_code).update(appt_status="Cancelled")
        
                                    appt_ids = Appointment.objects.filter(sa_transacno=sa.ref_transacno,
                                    treatmentcode=sa.ref_no).update(appt_status="Cancelled")
        
                                    TreatmentAccount.objects.filter(pk=sa.pk).update(sa_status='VOID')
                                    # type__in=('Deposit', 'Top Up')
                                    olacc_ids = TreatmentAccount.objects.filter(ref_transacno=sa.ref_transacno,
                                    treatment_parentcode=sa.treatment_parentcode,cust_code=haudobj.sa_custno).order_by('id').last()
                                    
                                    PackageAuditingLog(treatment_parentcode=sa.treatment_parentcode,
                                    user_loginid=fmspw[0],package_type="Void",pa_qty=sa.qty if sa.qty else None).save()    

                                    tretac = TreatmentAccount(Cust_Codeid=sa.Cust_Codeid,cust_code=sa.cust_code,
                                    description=description,ref_no=sa.ref_no,type=sa.type,amount="{:.2f}".format(float(abs(sa.amount))),
                                    balance="{:.2f}".format(float(olacc_ids.balance + abs(sa.amount))),user_name=sa.user_name,User_Nameid=sa.User_Nameid,
                                    ref_transacno=sa.ref_transacno,sa_transacno=sa_transacno,qty=sa.qty,
                                    outstanding="{:.2f}".format(float(olacc_ids.outstanding)) if olacc_ids and olacc_ids.outstanding is not None and olacc_ids.outstanding > 0 else 0,deposit=-float("{:.2f}".format(float(sa.deposit))) if sa.deposit else 0,treatment_parentcode=sa.treatment_parentcode,
                                    sa_status="SA",cas_name=fmspw[0].pw_userlogin,sa_staffno=sa.sa_staffno,
                                    sa_staffname=sa.sa_staffname,
                                    dt_lineno=sa.dt_lineno,package_code=sa.package_code,Site_Codeid=sa.Site_Codeid,
                                    site_code=sa.site_code,itemcart=cart_obj)
                                    tretac.save()
                                    tretac.sa_date = cart_date
                                    tretac.save()
                                
                                if d.itemcart.multi_treat.all().exists():        
                                    ct = d.itemcart.multi_treat.all()[0]
                                    searcids = TreatmentPackage.objects.filter(treatment_parentcode=ct.treatment_parentcode).first()
                                    if searcids:
                                        if ct.type in ['FFi','FFd']:
                                            ef_done_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('pk').count()
                                            ef_open_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Open").order_by('pk')
                                            if ct.treatment_limit_times is not None:
                                                if int(ct.treatment_limit_times) == 0:
                                                    if not ef_open_ids:
                                                        # if ct.treatment_limit_times > ef_done_ids or ct.treatment_limit_times == 0:
                                                            efd_treat_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('-pk').first()
                                                            times_ve = str(int(efd_treat_ids.times) + 1).zfill(2)
                                                            treatment_coder = ct.treatment_parentcode+"-"+times_ve
                                                        
                                                            treatids = Treatment(treatment_code=treatment_coder,course=searcids.course,times=times_ve,
                                                            treatment_no=times_ve,price=searcids.totalprice,treatment_date=date.today(),
                                                            cust_name=ct.cust_name,Cust_Codeid=ct.Cust_Codeid,
                                                            cust_code=ct.cust_code,status="Open",unit_amount=0,
                                                            Item_Codeid=searcids.Item_Codeid,item_code=str(searcids.Item_Codeid.item_code)+"0000",treatment_parentcode=ct.treatment_parentcode,
                                                            sa_transacno=ct.sa_transacno,
                                                            sa_status=ct.sa_status,
                                                            remarks=ct.remarks,duration=ct.duration,
                                                            dt_lineno=ct.dt_lineno,expiry=ct.expiry,package_code=ct.package_code,
                                                            Site_Codeid=ct.Site_Codeid,site_code=ct.site_code,type=ct.type,treatment_limit_times=ct.treatment_limit_times,
                                                            service_itembarcode=ct.service_itembarcode,isfoc=ct.isfoc,Trmt_Room_Codeid=ct.Trmt_Room_Codeid,
                                                            trmt_room_code=ct.trmt_room_code,trmt_is_auto_proportion=ct.trmt_is_auto_proportion,
                                                            treatment_account=ct.treatment_account)
                                                            treatids.save()
                                                            treatids.treatment_date = date.today()
                                                            treatids.save()
                                                            if treatids:
                                                                stfd_ids = Treatmentids.objects.filter(treatment_int=treatids.pk)
                                                                if not stfd_ids: 
                                                                    t_id =  Treatmentids(treatment_parentcode=ct.treatment_parentcode,
                                                                    treatment_int=treatids.pk).save()
                                                    

                                       
                                    
                                        stptdone_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('pk').count()
                                        stptcancel_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Cancel").order_by('pk').count()
                                        stptopen_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Open").order_by('pk').count()
                                        
                                        trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                                        
                                        
                                        searcids.open_session = stptopen_ids
                                        searcids.done_session = stptdone_ids
                                        searcids.cancel_session = stptcancel_ids

                                        searcids.balance = "{:.2f}".format(float(trmtAccObj.balance)) 
                                        searcids.outstanding = "{:.2f}".format(float(trmtAccObj.outstanding))
                                        # searcids.treatmentids = treatmids
                                        searcids.save()
                                        treatmids = list(set(Treatment.objects.filter(
                                        treatment_parentcode=ct.treatment_parentcode).filter(~Q(status="Open")).only('pk').order_by('pk').values_list('pk', flat=True).distinct()))

                                        Treatmentids.objects.filter(treatment_parentcode=ct.treatment_parentcode,
                                        treatment_int__in=treatmids).delete() 

                                        p_ids = list(set(Treatmentids.objects.filter(treatment_parentcode=ct.treatment_parentcode).values_list('treatment_int', flat=True).distinct()))
                                        op_ids = list(Treatment.objects.filter(
                                        treatment_parentcode=ct.treatment_parentcode).filter(Q(status="Open"),~Q(pk__in=p_ids)).only('pk').order_by('pk').values_list('pk', flat=True).distinct())
                                        if op_ids:
                                            for j in op_ids:
                                                stf_ids = Treatmentids.objects.filter(treatment_int=j)
                                                if not stf_ids: 
                                                    Treatmentids(treatment_parentcode=ct.treatment_parentcode,
                                                                treatment_int=j).save()
                    
        
  

                                
                                
                           
                        elif int(d.itemcart.itemcodeid.item_div) == 1:
                            if d.itemcart.type == 'Deposit':

                                if d.itemcart.batch_sno:
                                    batchso_ids = ItemBatchSno.objects.filter(batch_sno__icontains=d.itemcart.batch_sno,
                                    availability=False,site_code=d.itemsite_code).first()
                                    if batchso_ids:
                                        batchso_ids.availability = True
                                        batchso_ids.save()
                                    
                            
                                dacc_ids = DepositAccount.objects.filter(sa_transacno=haudobj.sa_transacno,sa_status='SA',type='Deposit',
                                cust_code=haudobj.sa_custno,dt_lineno=d.dt_lineno)
                    
                                for depo in dacc_ids:
                                    tpcontrolobj = ControlNo.objects.filter(control_description__iexact="TopUp",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                                    
                                    tp_code = str(tpcontrolobj.control_prefix)+str(tpcontrolobj.Site_Codeid.itemsite_code)+str(tpcontrolobj.control_no)
                                
                                    balance = depo.balance - depo.amount
                                    desc = "Cancel"+" "+"Product Amount : "+str("{:.2f}".format(float(depo.amount)))
                                    dact = DepositAccount(cust_code=depo.cust_code,type="CANCEL",amount=-float("{:.2f}".format(float(depo.amount))) if depo.amount else 0,balance="{:.2f}".format(float(balance)),
                                    user_name=depo.user_name,qty=depo.qty,outstanding=0.0,deposit="{:.2f}".format(float(depo.deposit)),
                                    cas_name=fmspw[0].pw_userlogin,sa_staffno=depo.sa_staffno,sa_staffname=depo.sa_staffname,
                                    deposit_type=depo.deposit_type,sa_transacno=depo.sa_transacno,description=desc,
                                    sa_status="VT",item_barcode=depo.item_barcode,item_description=depo.item_description,
                                    treat_code=depo.treat_code,void_link=depo.void_link,lpackage=depo.lpackage,
                                    package_code=depo.package_code,dt_lineno=depo.dt_lineno,Cust_Codeid=depo.Cust_Codeid,
                                    Site_Codeid=depo.Site_Codeid,site_code=depo.site_code,Item_Codeid=depo.Item_Codeid,
                                    item_code=depo.item_code,ref_transacno=depo.ref_transacno,ref_productcode=depo.ref_productcode,
                                    ref_code=tp_code)
                                    dact.save()
                                    dact.sa_date = cart_date
                                    dact.save()

                                    tpcontrolobj.control_no = int(tpcontrolobj.control_no) + 1
                                    tpcontrolobj.save()

                                open_hoids = Holditemdetail.objects.filter(sa_transacno=haudobj.sa_transacno,hi_lineno=d.dt_lineno)
                                if len(open_hoids) == 1 and open_hoids[0].status == 'OPEN':
                                    open_hoids[0].status = 'VOID'
                                    open_hoids[0].holditemqty = 0
                                    open_hoids[0].save()
                                    

                                #    DepositAccount.objects.filter(pk=depo.pk).update(sa_status="VT",item_description="Cancel"+depo.item_description,updated_at=timezone.now())

                                #ItemBatch
                                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                                item_code=d.dt_itemnoid.item_code,uom=d.dt_uom).order_by('pk').last()
                                if batch_ids:
                                    addamt = batch_ids.qty + d.dt_qty
                                    batch_ids.qty = addamt
                                    batch_ids.save()
                                    currenttime = timezone.now()
                                    currentdate = timezone.now().date()
                                    post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)

                                    #Stktrn
                                    # stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                                    # itemcode=d.dt_itemno,item_uom=d.dt_uom,trn_docno=haudobj.sa_transacno,
                                    # line_no=d.dt_lineno).last() 
                                    # stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                                    # itemcode=d.dt_itemno,item_uom=d.dt_uom).last() 
                                    

                                    # if stktrn_ids:
                                    #     amt_add = stktrn_ids.trn_balqty - stktrn_ids.trn_qty


                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(d.dt_itemnoid.item_code)+"0000",
                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                                    trn_type="VT",trn_db_qty=None,trn_cr_qty=None,trn_qty=d.dt_qty,trn_balqty=addamt,
                                    trn_balcst=0,
                                    trn_amt="{:.2f}".format(float(d.dt_deposit)),
                                    trn_cost=0,trn_ref=None,
                                    hq_update=0,
                                    line_no=d.dt_lineno,item_uom=d.dt_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                    stock_in=None,trans_package_line_no=None,
                                    trn_post=currentdate,trn_date=currentdate).save()

                                   
                            elif d.itemcart.type == 'Top Up':
                                dtacc_ids = DepositAccount.objects.filter(ref_code=haudobj.sa_transacno,sa_status='SA',type='Top Up',
                                cust_code=haudobj.sa_custno,treat_code=d.topup_product_treat_code).first()
                            
                                # for dt in dtacc_ids:
                                if dtacc_ids:
                                    dt = dtacc_ids
                                    depacc_ids = DepositAccount.objects.filter(sa_transacno=dt.sa_transacno,
                                    treat_code=dt.treat_code).order_by('-id').first()

                                    balance = depacc_ids.balance - dt.amount
                                    outstanding = depacc_ids.outstanding + dt.amount

                                    dpt = DepositAccount(cust_code=dt.cust_code,type=dt.type,amount=-float("{:.2f}".format(float(dt.amount))) if dt.amount else 0,
                                    balance="{:.2f}".format(float(balance)),user_name=dt.user_name,qty=-dt.qty,outstanding="{:.2f}".format(float(outstanding)) if outstanding is not None and outstanding > 0 else 0,
                                    deposit="{:.2f}".format(float(dt.deposit)),cas_name=dt.cas_name,sa_staffno=dt.sa_staffno,
                                    sa_staffname=dt.sa_staffname,deposit_type=dt.deposit_type,sa_transacno=dt.sa_transacno,
                                    description=dt.description,ref_code=sa_transacno,sa_status="VT",item_barcode=dt.item_barcode,
                                    item_description=dt.item_description,treat_code=dt.treat_code,void_link=dt.void_link,
                                    lpackage=dt.lpackage,package_code=dt.package_code,dt_lineno=dt.dt_lineno,Cust_Codeid=dt.Cust_Codeid,
                                    Site_Codeid=dt.Site_Codeid,site_code=dt.site_code,Item_Codeid=dt.Item_Codeid,item_code=dt.item_code,
                                    ref_transacno=dt.ref_transacno,ref_productcode=dt.ref_productcode)
                                    dpt.save()
                                    dpt.sa_date = cart_date
                                    dpt.save()



                        elif int(d.itemcart.itemcodeid.item_div) == 5:
                            if d.itemcart.type == 'Deposit':
                                pacc_ids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,sa_status='DEPOSIT',
                                cust_code=haudobj.sa_custno,line_no=d.dt_lineno)

                                check_ids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,
                                cust_code=haudobj.sa_custno,line_no=d.dt_lineno,use_amt__gt=0,sa_status="SA")
                                if not check_ids: 
                                    for pa in pacc_ids:
                                        PrepaidAccount.objects.filter(pk=pa.pk).update(remain=0.0,status=False,sa_status="VT",updated_at=timezone.now(),
                                        cust_code=haudobj.sa_custno)

                                    paccids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,
                                    cust_code=haudobj.sa_custno,line_no=d.dt_lineno)

                                    for p in paccids:
                                        PrepaidAccount.objects.filter(pk=p.pk).update(status=False)
                            elif d.itemcart.type == 'Top Up':
                                ptacc_ids = PrepaidAccount.objects.filter(topup_no=haudobj.sa_transacno,sa_status='TOPUP',
                                cust_code=haudobj.sa_custno,line_no=d.itemcart.prepaid_account.line_no).first()
                                
                                # for pt in ptacc_ids:
                                if ptacc_ids:
                                    pt = ptacc_ids
                                    
                                    
                                    pre_acc_ids = PrepaidAccount.objects.filter(pp_no=pt.pp_no,
                                    line_no=pt.line_no).order_by('-id').first()

                                    PrepaidAccount.objects.filter(pk=pre_acc_ids.pk).update(status=False,updated_at=timezone.now())
                                
                                    if pre_acc_ids and pre_acc_ids.outstanding == 0.0:
                                        or_remain = pre_acc_ids.remain - pre_acc_ids.pp_bonus
                                    else:
                                        or_remain = pre_acc_ids.remain    
                                    
                                    outstanding = pre_acc_ids.outstanding + pt.topup_amt
                                    remain = or_remain - pt.topup_amt

                                    pcts = PrepaidAccount(pp_no=pt.pp_no,pp_type=pt.pp_type,pp_desc=pt.pp_desc,exp_date=pt.exp_date,
                                    cust_code=pt.cust_code,cust_name=pt.cust_name,pp_amt=pt.pp_amt,pp_bonus=pt.pp_bonus,
                                    pp_total=pt.pp_total,transac_no=pt.transac_no,item_no=pt.item_no,use_amt=pt.use_amt,
                                    remain=remain,ref1=pt.ref1,ref2=pt.ref2,status=True,site_code=pt.site_code,
                                    sa_status='TOPUP',exp_status=pt.exp_status,voucher_no=pt.voucher_no,isvoucher=pt.isvoucher,
                                    has_deposit=pt.has_deposit,topup_amt=-pt.topup_amt,outstanding=outstanding if outstanding is not None and outstanding > 0 else 0,
                                    active_deposit_bonus=pt.active_deposit_bonus,topup_no=sa_transacno,topup_date=pt.topup_date,
                                    line_no=pt.line_no,staff_name=pt.staff_name,staff_no=pt.staff_no,pp_type2=pt.pp_type2,
                                    condition_type1=pt.condition_type1,pos_daud_lineno=pt.pos_daud_lineno,mac_uid_ref=pt.mac_uid_ref,
                                    lpackage=pt.lpackage,package_code=pt.package_code,package_code_lineno=pt.package_code_lineno,
                                    prepaid_disc_type=pt.prepaid_disc_type,prepaid_disc_percent=pt.prepaid_disc_percent,
                                    Cust_Codeid=pt.Cust_Codeid,Site_Codeid=pt.Site_Codeid,Item_Codeid=pt.Item_Codeid,
                                    item_code=pt.item_code)
                                    pcts.save()
                                    pcts.sa_date = cart_date 
                                    pcts.start_date = cart_date
                                    pcts.save()


                        elif int(d.itemcart.itemcodeid.item_div) == 4:
                            if d.itemcart.type == 'Deposit':
                                # voucher_ids = VoucherRecord.objects.filter(sa_transacno=haudobj.sa_transacno,
                                # cust_code=haudobj.sa_custno,site_code=site.itemsite_code).order_by('pk')

                                voucher_ids = VoucherRecord.objects.filter(sa_transacno=haudobj.sa_transacno,
                                cust_code=haudobj.sa_custno,dt_lineno=d.dt_lineno).order_by('pk')
                                
                                
                                for vcc in voucher_ids:
                                    VoucherRecord.objects.filter(pk=vcc.pk).update(value=-vcc.value,updated_at=timezone.now(),isvalid=False)
        

                    v_refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference VOID No",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                
                    sa_transacno_ref = str(v_refcontrol_obj.control_prefix)+str(v_refcontrol_obj.Site_Codeid.itemsite_code)+str(v_refcontrol_obj.control_no)
                    v_refcontrol_obj.control_no = int(v_refcontrol_obj.control_no) + 1
                    v_refcontrol_obj.save()

                    h = haudobj 
                    # void_obj[0].reason_desc if void_obj else None
                    PosHaud.objects.filter(pk=h.pk).update(isvoid=True,void_refno=sa_transacno)
                    total_outstanding = h.total_outstanding + h.sa_transacamt
                    haud = PosHaud(cas_name=fmspw[0].pw_userlogin,sa_transacno=sa_transacno,sa_status="VT",
                    sa_totamt=-float("{:.2f}".format(float(h.sa_totamt))),sa_totqty=-h.sa_totqty,sa_totdisc=-float("{:.2f}".format(float(h.sa_totdisc))) if h.sa_totdisc else 0,
                    sa_totgst=-float("{:.2f}".format(float(h.sa_totgst))) if h.sa_totgst else None,sa_staffnoid=h.sa_staffnoid,
                    sa_staffno=h.sa_staffno,sa_staffname=h.sa_staffname,sa_custnoid=h.sa_custnoid,sa_custno=h.sa_custno,
                    sa_custname=h.sa_custname,sa_discuser=h.sa_discuser,
                    sa_discamt=-float("{:.2f}".format(float(h.sa_discamt))) if h.sa_discamt else 0,sa_disctotal=-float("{:.2f}".format(float(h.sa_disctotal))) if h.sa_disctotal else 0,
                    ItemSite_Codeid=h.ItemSite_Codeid,itemsite_code=h.itemsite_code,
                    sa_depositamt=-h.sa_depositamt,isvoid=True,void_refno=h.sa_transacno,
                    payment_remarks=h.payment_remarks,
                    sa_transacamt=h.sa_transacamt,
                    holditemqty=h.holditemqty,walkin=h.walkin,sa_round="{:.2f}".format(float(h.sa_round)) if h.sa_round else None,
                    total_outstanding="{:.2f}".format(float(total_outstanding)) if total_outstanding is not None and total_outstanding > 0 else 0,trans_user_login=h.trans_user_login,
                    trans_user_loginid=h.trans_user_loginid,sa_transacno_ref=sa_transacno_ref,
                    sa_transacno_type='Void Transaction',sa_transacno_title="VOID",
                    issuestrans_user_login=h.trans_user_login,trans_remark=void_obj[0].reason_desc if void_obj and void_obj[0].reason_desc else None)
                    haud.save()
                    haud.sa_date = cart_date 
                    haud.save()

                    if haud.pk:
                        # control_obj.control_no = int(control_obj.control_no) + 1
                        # control_obj.save()
                        
                        finalsatrasc = haud.sa_transacno

                    cart_ids = ItemCart.objects.filter(isactive=True,cart_id=cart_id,cart_status="Inprogress",
                    sitecode=site.itemsite_code,cart_date=date.today(),cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx)
                    for cart in cart_ids:
                        ItemCart.objects.filter(pk=cart.pk).update(cart_status='Completed',quantity=-cart.quantity)
                    
                    cust_obj = haud.sa_custnoid ; now_point = 0;

                    if cust_obj and cust_obj.cust_point_value == None: 
                        now_point = 0
                    else:
                        if cust_obj and cust_obj.cust_point_value and cust_obj.cust_point_value > 0:
                            now_point = cust_obj.cust_point_value

                    #custpmer points revert back under Reward Policy
                    custpts_ids = CustomerPoint.objects.filter(postransactionno=haudobj.sa_transacno,
                    isvoid=False,type='Reward').order_by('-pk').first()
                    if custpts_ids:
                        custptsdtl_ids = CustomerPointDtl.objects.filter(transacno=custpts_ids.transacno).order_by('pk')
                        ptsdtl = False; pttl_lst =[]
                       
                        if custptsdtl_ids:
                            nopoint = now_point
                            for ptdtl in custptsdtl_ids:

                                ptdtl.isvoid = True
                                ptdtl.void_referenceno = sa_transacno
                                ptdtl.isopen = False
                                ptdtl.save()
                                deduct_pt = nopoint - ptdtl.point
                                nopoint -= ptdtl.point

                                pct = CustomerPointDtl(type="Reward Return",cust_code=ptdtl.cust_code,
                                cust_name=ptdtl.cust_name,parent_code=None,parent_desc=None,
                                parent_display=None,itm_code=ptdtl.itm_code,itm_desc=ptdtl.itm_desc,
                                point=-ptdtl.point,now_point=deduct_pt,remark=None,remark_code=None,
                                remark_desc=None,isvoid=True,void_referenceno=haudobj.sa_transacno,isopen=False,qty=-ptdtl.qty,
                                total_point=-ptdtl.total_point,seq=False,sa_status="VT",bal_acc2=None,point_acc1=None,
                                point_acc2=None,locid=False)
                                pct.save()
                                pttl_lst.append(pct.pk)
                                ptsdtl = True
                            
                            if ptsdtl == True:
                                # print("True")
                                custpts_ids.isvoid = True
                                custpts_ids.void_referenceno = sa_transacno
                                custpts_ids.save()
                                total_invpts = sum([i.point for i in custptsdtl_ids])
                                # cust_point_value =  nopoint + total_invpts
                                # bal_point = cust_point_value
                               
                                rew_refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reward Sales",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                                rew_transacno = str(rew_refcontrol_obj.control_prefix)+str(rew_refcontrol_obj.Site_Codeid.itemsite_code)+str(rew_refcontrol_obj.control_no)
                                rew_refcontrol_obj.control_no = int(rew_refcontrol_obj.control_no) + 1
                                rew_refcontrol_obj.save()

                                CustomerPoint(transacno=rew_transacno,date=haud.sa_date,username=fmspw[0].pw_userlogin,
                                time=haud.sa_time,cust_name=cust_obj.cust_name,cust_code=cust_obj.cust_code,type="Reward Return",
                                refno=haudobj.sa_transacno,ref_source="Sales Return",isvoid=True,sa_status="VT",void_referenceno=haudobj.sa_transacno,
                                total_point=-total_invpts,now_point=nopoint,seq=None,remarks=None,
                                bal_point=nopoint,expired=False,expired_date=None,mac_code=False,logno=False,
                                approval_user=fmspw[0].pw_userlogin,cardno=False,bdate=None,pdate=None,expired_point=0,
                                postransactionno=sa_transacno,postotalamt=haud.sa_depositamt,locid=False,mgm_refno=None,tdate=None).save()
                                for cds in pttl_lst:
                                    cdts = CustomerPointDtl.objects.filter(pk=cds).first()
                                    if cdts:
                                        cdts.transacno = rew_transacno 
                                        cdts.save()
                                
                                cust_obj.cust_point_value = nopoint
                                cust_obj.save()
                                now_point = cust_obj.cust_point_value

                    #custpmer points revert back under Redeem Policy
                    recustpts_ids = CustomerPoint.objects.filter(postransactionno=haudobj.sa_transacno,
                    isvoid=False,type='Redeem').order_by('-pk').first()
                    if recustpts_ids:
                        
                        recustptsdtl_ids = CustomerPointDtl.objects.filter(transacno=recustpts_ids.transacno).order_by('pk')
                        reptsdtl = False; repttl_lst =[]
                       
                        if recustptsdtl_ids:
                            no_point = now_point
                            for rptdtl in recustptsdtl_ids:

                                rptdtl.isvoid = True
                                rptdtl.void_referenceno = sa_transacno
                                rptdtl.isopen = False
                                rptdtl.save()
                                deduct_pt = no_point + rptdtl.point
                                no_point += rptdtl.point

                                rpct = CustomerPointDtl(type="Redeem Return",cust_code=rptdtl.cust_code,
                                cust_name=rptdtl.cust_name,parent_code=None,parent_desc=None,
                                parent_display=None,itm_code=rptdtl.itm_code,itm_desc=rptdtl.itm_desc,
                                point=-rptdtl.point,now_point=deduct_pt,remark=None,remark_code=None,
                                remark_desc=None,isvoid=True,void_referenceno=haudobj.sa_transacno,isopen=False,qty=-rptdtl.qty,
                                total_point=-rptdtl.total_point,seq=False,sa_status="VT",bal_acc2=None,point_acc1=None,
                                point_acc2=None,locid=False)
                                rpct.save()
                                repttl_lst.append(rpct.pk)
                                reptsdtl = True
                            
                            if reptsdtl == True:
                                # print("True")
                                recustpts_ids.isvoid = True
                                recustpts_ids.void_referenceno = sa_transacno
                                recustpts_ids.save()
                                total_redmpts = sum([i.point for i in recustptsdtl_ids])
                                # cust_point_value =  no_point - total_redmpts
                                # bal_point = cust_point_value
                               
                                redem_refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Redeem Sales",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                                redem_transacno = str(redem_refcontrol_obj.control_prefix)+str(redem_refcontrol_obj.Site_Codeid.itemsite_code)+str(redem_refcontrol_obj.control_no)
                                redem_refcontrol_obj.control_no = int(redem_refcontrol_obj.control_no) + 1
                                redem_refcontrol_obj.save()


                                CustomerPoint(transacno=redem_transacno,date=haud.sa_date,username=fmspw[0].pw_userlogin,
                                time=haud.sa_time,cust_name=cust_obj.cust_name,cust_code=cust_obj.cust_code,type="Redeem Return",
                                refno=haudobj.sa_transacno,ref_source="Sales Return",isvoid=True,sa_status="VT",void_referenceno=haudobj.sa_transacno,
                                total_point=-total_redmpts,now_point=no_point,seq=None,remarks=None,
                                bal_point=no_point,expired=False,expired_date=None,mac_code=False,logno=False,
                                approval_user=fmspw[0].pw_userlogin,cardno=False,bdate=None,pdate=None,expired_point=0,
                                postransactionno=sa_transacno,postotalamt=haud.sa_depositamt,locid=False,mgm_refno=None,tdate=None).save()
                                for rcds in repttl_lst:
                                    rcdts = CustomerPointDtl.objects.filter(pk=rcds).first()
                                    if rcdts:
                                        rcdts.transacno = redem_transacno 
                                        rcdts.save()
                                
                                cust_obj.cust_point_value = no_point
                                cust_obj.save()



                    result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False, 'data':{'sa_transacno':finalsatrasc if finalsatrasc else None}}
                    savalue = sa_transacno_update_void(self, site, fmspw[0]) 
                    return Response(data=result, status=status.HTTP_200_OK)
            
                elif haudobj.sa_transacno_type == 'Redeem Service':
                    for ta in taud_ids:
                        taud = PosTaud(sa_transacno=sa_transacno,pay_groupid=ta.pay_groupid,pay_group=ta.pay_group,
                        pay_typeid=ta.pay_typeid,pay_type=ta.pay_type,pay_desc=ta.pay_desc,pay_tendamt=ta.pay_tendamt,
                        pay_tendrate=ta.pay_tendrate,pay_tendcurr=ta.pay_tendcurr,pay_amt=ta.pay_amt,pay_amtrate=ta.pay_amtrate,
                        pay_amtcurr=ta.pay_amtcurr,pay_rem1=ta.pay_rem1,pay_rem2=ta.pay_rem2,pay_rem3=ta.pay_rem3,pay_rem4=ta.pay_rem4,
                        pay_status=ta.pay_status,pay_actamt=ta.pay_actamt,ItemSIte_Codeid=ta.ItemSIte_Codeid,
                        itemsite_code=ta.itemsite_code,paychange=ta.paychange,dt_lineno=ta.dt_lineno,pay_gst_amt_collect=ta.pay_gst_amt_collect,
                        pay_gst=ta.pay_gst,posdaudlineno=ta.posdaudlineno,
                        billed_by=ta.billed_by,subtotal=ta.subtotal,tax=ta.tax,discount_amt=ta.discount_amt,
                        billable_amount=ta.billable_amount,credit_debit=ta.credit_debit,points=ta.points,prepaid=ta.prepaid,
                        pay_premise=ta.pay_premise,is_voucher=ta.is_voucher,)
                    
                        taud.save()
                        taud.sa_date = cart_date 
                        taud.save()
                    
                    for m in multi_ids:
                        multi =  Multistaff(sa_transacno=sa_transacno,item_code=m.item_code,emp_code=m.emp_code,
                        ratio=m.ratio,salesamt=-float("{:.2f}".format(float(m.salesamt))) if m.salesamt else 0,type=m.type,isdelete=m.isdelete,role=m.role,dt_lineno=m.dt_lineno,
                        level_group_code=m.level_group_code) 
                        multi.save()

                    for da in daud_ids:
                        if float(da.dt_discpercent) > 0.0:
                            dt_discpercent = -da.dt_discpercent
                        else:
                            dt_discpercent = da.dt_discpercent    
                        
                        cart_obj = ItemCart.objects.filter(isactive=True,cart_id=cart_id,lineno=da.dt_lineno,
                        sitecode=site.itemsite_code,cart_date=date.today(),cart_status="Inprogress",
                        cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx).first()

                        sales = "";service = ""
                        if cart_obj.sales_staff.all():
                            for i in cart_obj.sales_staff.all():
                                if sales == "":
                                    sales = sales + i.display_name
                                elif not sales == "":
                                    sales = sales +","+ i.display_name
                        if cart_obj.service_staff.all(): 
                            for s in cart_obj.service_staff.all():
                                if service == "":
                                    service = service + s.display_name
                                elif not service == "":
                                    service = service +","+ s.display_name 

                        daud = PosDaud(sa_transacno=sa_transacno,dt_status="VT",dt_itemnoid=da.dt_itemnoid,dt_itemno=da.dt_itemno,
                        dt_itemdesc=da.dt_itemdesc,dt_price=da.dt_price,dt_promoprice="{:.2f}".format(float(da.dt_promoprice)),dt_amt=-float("{:.2f}".format(float(da.dt_amt))) if da.dt_amt else 0,
                        dt_qty=-da.dt_qty,dt_discamt=-da.dt_discamt if float(da.dt_discamt) > 0.0 else da.dt_discamt, 
                        dt_discpercent=-da.dt_discpercent if float(da.dt_discpercent) > 0.0 else da.dt_discpercent,dt_discdesc=da.dt_discdesc,
                        dt_discno=da.dt_discno,dt_remark=da.dt_remark,dt_Staffnoid=da.dt_Staffnoid,dt_staffno=da.dt_staffno,
                        dt_staffname=da.dt_staffname,dt_discuser=da.dt_discuser,dt_combocode=da.dt_combocode,
                        ItemSite_Codeid=da.ItemSite_Codeid,itemsite_code=da.itemsite_code,dt_lineno=da.dt_lineno,
                        dt_uom=da.dt_uom,isfoc=da.isfoc,
                        item_remarks=da.item_remarks,dt_transacamt="{:.2f}".format(float(da.dt_transacamt)),
                        dt_deposit=-float("{:.2f}".format(float(da.dt_deposit))) if da.dt_deposit else 0,
                        holditemqty=da.holditemqty,st_ref_treatmentcode=da.st_ref_treatmentcode,
                        item_status_code=da.item_status_code,first_trmt_done=da.first_trmt_done,
                        first_trmt_done_staff_code=da.first_trmt_done_staff_code,first_trmt_done_staff_name=da.first_trmt_done_staff_name,
                        record_detail_type=da.record_detail_type,trmt_done_staff_code=da.trmt_done_staff_code,trmt_done_staff_name=da.trmt_done_staff_name,
                        trmt_done_id=da.trmt_done_id,trmt_done_type=da.trmt_done_type,topup_service_trmt_code=da.topup_service_trmt_code,
                        topup_product_treat_code=da.topup_product_treat_code,topup_prepaid_trans_code=da.topup_prepaid_trans_code,
                        topup_prepaid_type_code=da.topup_prepaid_type_code,
                        gst_amt_collect=-float("{:.2f}".format(float(da.gst_amt_collect))) if da.gst_amt_collect else 0,
                        topup_prepaid_pos_trans_lineno=da.topup_prepaid_pos_trans_lineno,
                        topup_outstanding=da.topup_outstanding if da and da.topup_outstanding is not None and da.topup_outstanding > 0 else 0 ,
                        itemcart=cart_obj,
                        staffs="/"+" "+ service)
                        daud.save()
                        daud.sa_date = cart_date 
                        daud.save()

                        if int(da.itemcart.itemcodeid.item_div) == 3:
                            if da.itemcart.type == 'Sales':
                                #sacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                                #cust_code=haudobj.sa_custno,site_code=site.itemsite_code)

                                sacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                                cust_code=haudobj.sa_custno,treatment_parentcode=da.itemcart.treatment.treatment_parentcode)
                              
                                if da.itemcart and da.itemcart.itemdesc:
                                    description = da.itemcart.itemdesc+" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)
                                else:
                                    description = da.itemcart.itemcodeid.itemdesc+" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)

                                
                                for i in da.itemcart.multi_treat.all():
                                    # if i.type in ['FFi','FFd']:
                                    #     if i.treatment_limit_times is not None and int(i.treatment_limit_times) == 0:
                                    #         # Treatment.objects.filter(pk=i.pk).update(course=description,status="Cancel",
                                    #         # trmt_room_code=None,treatment_count_done=0)
                                            
                                    #         # i.treatment_code = str(i.treatment_code)+"-"+"VT"
                                    #         # i.times =  str(i.times)+"-"+"VT"
                                    #         # i.treatment_no =  str(i.treatment_no)+"-"+"VT"
                                    #         i.course = description
                                    #         i.status = "Cancel"
                                    #         i.trmt_room_code = None
                                    #         i.treatment_count_done = 0
                                    #         i.save()
                                    #         ex_ids = Treatment.objects.filter(~Q(pk=i.pk),~Q(status='Cancel')).filter(treatment_parentcode=da.itemcart.treatment.treatment_parentcode,times__gt=i.times).order_by('pk')
                                    #         for e in ex_ids:
                                    #             tim = str(int(e.times) -1).zfill(2)
                                    #             tr_no = str(int(e.treatment_no) -1).zfill(2)
                                    #             e.times = tim
                                    #             e.treatment_no = tr_no
                                    #             e.treatment_code = str(da.itemcart.treatment.treatment_parentcode)+"-"+str(tim)
                                    #             e.save() 
                                    #         op_obj =Treatment.objects.filter(treatment_parentcode=i.treatment_parentcode,status='Open').order_by('-pk').first()    
                                    #         if op_obj:
                                    #             op_obj.unit_amount = i.unit_amount
                                    #             op_obj.save()    
                                    #     else:
                                    #         Treatment.objects.filter(pk=i.pk).update(course=description,status="Open",
                                    #         trmt_room_code=None,treatment_count_done=0)

                                    # else:
                                    Treatment.objects.filter(pk=i.pk).update(course=description,status="Open",
                                    trmt_room_code=None,treatment_count_done=0)

                                    TmpItemHelper.objects.filter(treatment__pk=i.pk).delete()

                                    # ihelper_ids = ItemHelper.objects.filter(helper_transacno=haudobj.sa_transacno,
                                    # site_code=site.itemsite_code)
                                    ihelper_ids = ItemHelper.objects.filter(helper_transacno=haudobj.sa_transacno,
                                    item_code=i.treatment_code)
                                    
                                    for hlp in ihelper_ids:
                                        tmphlp = ItemHelper(item_code=hlp.item_code,item_name=hlp.item_name,line_no=hlp.line_no,
                                        sa_transacno=hlp.sa_transacno,amount=-float("{:.2f}".format(float(hlp.amount))) if hlp.amount else 0,helper_name=hlp.helper_name,
                                        helper_code=hlp.helper_code,site_code=hlp.site_code,share_amt=-hlp.share_amt,
                                        helper_transacno=sa_transacno,
                                        wp1=hlp.wp1,wp2=hlp.wp2,wp3=hlp.wp3,times=hlp.times,
                                        treatment_no=hlp.treatment_no)
                                        tmphlp.save()
                                        ItemHelper.objects.filter(id=tmphlp.id).update(sa_date= date.today())
                                       

                                    treat_obj = i
                                    # accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
                                    # treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
                                    # type="Sales").order_by('id').first()

                                    accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
                                    treatment_parentcode=treat_obj.treatment_parentcode,ref_no=treat_obj.treatment_code,
                                    type="Sales").order_by('id').first()


                                    if accids:
                                        usagelevel_ids = Usagelevel.objects.filter(service_code=treat_obj.service_itembarcode,
                                        isactive=True).order_by('-pk')
                                        for i in usagelevel_ids:
                                            # instance = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                                            # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno,line_no=1,
                                            # usage_status="Usage",uom=i.uom,item_code=i.item_code).order_by('line_no').first() 

                                            instance = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                                            sa_transacno=accids.sa_transacno,line_no=1,
                                            usage_status="Usage",uom=i.uom,item_code=i.item_code).order_by('line_no').first() 

                                            # print(instance,"instance")
                                            if instance :
                                                now = datetime.datetime.now()
                                                s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))
                                
                                                instance.isactive = False
                                                instance.usage_update = s1
                                                instance.save()
                                                # useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                                                # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno,uom=i.uom,item_code=i.item_code).order_by('line_no') 

                                                useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                                                sa_transacno=accids.sa_transacno,uom=i.uom,item_code=i.item_code).order_by('line_no') 

                                                rec = useids.last()
                                                lineno = float(rec.line_no) + 1    

                                            
                                                TreatmentUsage(treatment_code=instance.treatment_code,item_code=instance.item_code,
                                                item_desc=instance.item_desc,qty=-instance.qty,uom=instance.uom,site_code=instance.site_code,
                                                usage_status="Void TD",line_no=lineno,void_line_ref=1,usage_update=s1,
                                                sa_transacno=instance.sa_transacno,isactive=False).save()
                                                
                                                #ItemBatch
                                                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                                                item_code=instance.item_code[:-4],uom=instance.uom).order_by('pk').last()
                                                
                                                if batch_ids:
                                                    addamt = batch_ids.qty + instance.qty
                                                    batch_ids.qty = addamt
                                                    batch_ids.updated_at = timezone.now()
                                                    batch_ids.save()

                                                    #Stktrn
                                                
                                                    currenttime = timezone.now()
                                                    currentdate = timezone.now().date()

                                                    post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                                                    
                                                
                                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                                                    itemcode=instance.item_code,store_no=site.itemsite_code,
                                                    tstore_no=None,fstore_no=None,trn_docno=instance.treatment_code,
                                                    trn_type="Void Usage",trn_db_qty=None,trn_cr_qty=None,
                                                    trn_qty=instance.qty,trn_balqty=addamt,trn_balcst=None,
                                                    trn_amt=None,trn_cost=None,trn_ref=None,
                                                    hq_update=0,line_no=instance.line_no,item_uom=instance.uom,
                                                    item_batch=None,mov_type=None,item_batch_cost=None,
                                                    stock_in=None,trans_package_line_no=None,
                                                    trn_post=currentdate,trn_date=currentdate).save()

                                
                                for sa in sacc_ids:
                                    master_ids = Treatment_Master.objects.filter(sa_transacno=sa.ref_transacno,
                                    treatment_code=sa.ref_no,site_code=site.itemsite_code).update(status="Cancel")
                                    appt_ids = Appointment.objects.filter(sa_transacno=sa.ref_transacno,
                                    treatmentcode=sa.ref_no,itemsite_code=site.itemsite_code).update(appt_status="Cancelled")
        
                                    TreatmentAccount.objects.filter(pk=sa.pk).update(sa_status='VOID')
                                    # type__in=('Deposit', 'Top Up')
                                    olacc_ids = TreatmentAccount.objects.filter(ref_transacno=sa.ref_transacno,
                                    treatment_parentcode=sa.treatment_parentcode,cust_code=haudobj.sa_custno).order_by('id').last()

                                    PackageAuditingLog(treatment_parentcode=sa.treatment_parentcode,
                                    user_loginid=fmspw[0],package_type="Void",pa_qty=sa.qty if sa.qty else None).save()    
 
                                    acttr = TreatmentAccount(Cust_Codeid=sa.Cust_Codeid,cust_code=sa.cust_code,
                                    description=description,ref_no=sa.ref_no,type=sa.type,amount="{:.2f}".format(float(abs(sa.amount))),
                                    balance="{:.2f}".format(float(olacc_ids.balance + abs(sa.amount))),user_name=sa.user_name,User_Nameid=sa.User_Nameid,
                                    ref_transacno=sa.ref_transacno,sa_transacno=sa_transacno,qty=sa.qty,
                                    outstanding="{:.2f}".format(float(olacc_ids.outstanding)) if olacc_ids and olacc_ids.outstanding is not None and olacc_ids.outstanding > 0 else 0,deposit=-float("{:.2f}".format(float(sa.deposit))) if sa.deposit else 0,treatment_parentcode=sa.treatment_parentcode,
                                    sa_status="SA",cas_name=fmspw[0].pw_userlogin,sa_staffno=sa.sa_staffno,
                                    sa_staffname=sa.sa_staffname,
                                    dt_lineno=sa.dt_lineno,package_code=sa.package_code,Site_Codeid=sa.Site_Codeid,
                                    site_code=sa.site_code,itemcart=cart_obj)
                                    acttr.save()
                                    acttr.sa_date = cart_date
                                    acttr.save()

                                
                                if da.itemcart.multi_treat.all().exists():        
                                    ct = da.itemcart.multi_treat.all()[0]
                                    searcids = TreatmentPackage.objects.filter(treatment_parentcode=ct.treatment_parentcode).first()
                                    if searcids:
                                        if ct.type in ['FFi','FFd']:
                                            ef_done_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('pk').count()
                                            ef_open_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Open").order_by('pk')
                                            if ct.treatment_limit_times is not None:
                                                if int(ct.treatment_limit_times) == 0:
                                                    if not ef_open_ids:
                                                        # if ct.treatment_limit_times > ef_done_ids or ct.treatment_limit_times == 0:
                                                            efd_treat_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('-pk').first()
                                                            times_ve = str(int(efd_treat_ids.times) + 1).zfill(2)
                                                            treatment_coder = ct.treatment_parentcode+"-"+times_ve
                                                        
                                                            treatids = Treatment(treatment_code=treatment_coder,course=searcids.course,times=times_ve,
                                                            treatment_no=times_ve,price=searcids.totalprice,treatment_date=date.today(),
                                                            cust_name=ct.cust_name,Cust_Codeid=ct.Cust_Codeid,
                                                            cust_code=ct.cust_code,status="Open",unit_amount=0,
                                                            Item_Codeid=searcids.Item_Codeid,item_code=str(searcids.Item_Codeid.item_code)+"0000",treatment_parentcode=ct.treatment_parentcode,
                                                            sa_transacno=ct.sa_transacno,
                                                            sa_status=ct.sa_status,
                                                            remarks=ct.remarks,duration=ct.duration,
                                                            dt_lineno=ct.dt_lineno,expiry=ct.expiry,package_code=ct.package_code,
                                                            Site_Codeid=ct.Site_Codeid,site_code=ct.site_code,type=ct.type,treatment_limit_times=ct.treatment_limit_times,
                                                            service_itembarcode=ct.service_itembarcode,isfoc=ct.isfoc,Trmt_Room_Codeid=ct.Trmt_Room_Codeid,
                                                            trmt_room_code=ct.trmt_room_code,trmt_is_auto_proportion=ct.trmt_is_auto_proportion,
                                                            treatment_account=ct.treatment_account)
                                                            treatids.save()
                                                            treatids.treatment_date = date.today()
                                                            treatids.save()
                                                            if treatids:
                                                                stfdids = Treatmentids.objects.filter(treatment_int=treatids.pk)
                                                                if not stfdids: 
                                                                    t_id =  Treatmentids(treatment_parentcode=ct.treatment_parentcode,
                                                                    treatment_int=treatids.pk).save()
                                                    
                                                            
                                                

                                        stptdone_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('pk').count()
                                        stptcancel_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Cancel").order_by('pk').count()
                                        stptopen_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Open").order_by('pk').count()
                                        
                                        trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                                       
                                        
                                        searcids.open_session = stptopen_ids
                                        searcids.done_session = stptdone_ids
                                        searcids.cancel_session = stptcancel_ids
                                        searcids.balance = "{:.2f}".format(float(trmtAccObj.balance)) 
                                        searcids.outstanding = "{:.2f}".format(float(trmtAccObj.outstanding))
                                        # searcids.treatmentids = treatmids
                                        searcids.save()
                                        treatmids = list(set(Treatment.objects.filter(
                                        treatment_parentcode=ct.treatment_parentcode).filter(~Q(status="Open")).only('pk').order_by('pk').values_list('pk', flat=True).distinct()))

                                        Treatmentids.objects.filter(treatment_parentcode=ct.treatment_parentcode,
                                        treatment_int__in=treatmids).delete() 

                                        p_ids = list(set(Treatmentids.objects.filter(treatment_parentcode=ct.treatment_parentcode).values_list('treatment_int', flat=True).distinct()))
                                        op_ids = list(Treatment.objects.filter(
                                        treatment_parentcode=ct.treatment_parentcode).filter(Q(status="Open"),~Q(pk__in=p_ids)).only('pk').order_by('pk').values_list('pk', flat=True).distinct())
                                        if op_ids:
                                            for j in op_ids:
                                                stf_ids = Treatmentids.objects.filter(treatment_int=j)
                                                if not stf_ids: 
                                                    Treatmentids(treatment_parentcode=ct.treatment_parentcode,
                                                                treatment_int=j).save()
                     
        
                                
                               
                    
                    v_refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference VOID No",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                
                    sa_transacno_ref = str(v_refcontrol_obj.control_prefix)+str(v_refcontrol_obj.Site_Codeid.itemsite_code)+str(v_refcontrol_obj.control_no)
                    v_refcontrol_obj.control_no = int(v_refcontrol_obj.control_no) + 1
                    v_refcontrol_obj.save()

                    h = haudobj 
                    # void_obj[0].reason_desc if void_obj else None
                    PosHaud.objects.filter(pk=h.pk).update(isvoid=True,void_refno=sa_transacno)
                    haud = PosHaud(cas_name=fmspw[0].pw_userlogin,sa_transacno=sa_transacno,sa_status="VT",
                    sa_totamt="{:.2f}".format(float(h.sa_totamt)),sa_totqty=h.sa_totqty,sa_totdisc="{:.2f}".format(float(h.sa_totdisc)) if h.sa_totdisc else 0,
                    sa_totgst="{:.2f}".format(float(h.sa_totgst)) if h.sa_totgst else 0,sa_staffnoid=h.sa_staffnoid,
                    sa_staffno=h.sa_staffno,sa_staffname=h.sa_staffname,sa_custnoid=h.sa_custnoid,sa_custno=h.sa_custno,
                    sa_custname=h.sa_custname,sa_discuser=h.sa_discuser,
                    sa_discamt="{:.2f}".format(float(h.sa_discamt)) if h.sa_discamt else 0,sa_disctotal="{:.2f}".format(float(h.sa_disctotal)) if h.sa_disctotal else 0,
                    ItemSite_Codeid=h.ItemSite_Codeid,itemsite_code=h.itemsite_code,
                    sa_depositamt="{:.2f}".format(float(h.sa_depositamt)) if h.sa_depositamt else 0,isvoid=True,void_refno=h.sa_transacno,
                    payment_remarks=h.payment_remarks,
                    sa_transacamt="{:.2f}".format(float(h.sa_transacamt)) if h.sa_transacamt else 0,
                    holditemqty=h.holditemqty,walkin=h.walkin,sa_round="{:.2f}".format(float(h.sa_round)) if h.sa_round else 0,
                    total_outstanding="{:.2f}".format(float(h.total_outstanding)) if h and h.total_outstanding is not None and h.total_outstanding > 0 else 0,trans_user_login=h.trans_user_login,
                    trans_user_loginid=h.trans_user_loginid,sa_transacno_ref=sa_transacno_ref,
                    sa_transacno_type='Void Transaction',sa_transacno_title="VOID",
                    issuestrans_user_login=fmspw[0].pw_userlogin,trans_remark=void_obj[0].reason_desc if void_obj and void_obj[0].reason_desc else None)
                    haud.save()
                    haud.sa_date = cart_date
                    haud.save()

                    if haud.pk:
                        # control_obj.control_no = int(control_obj.control_no) + 1
                        # control_obj.save()

                        finalsatrasc = haud.sa_transacno

                    cart_ids = ItemCart.objects.filter(isactive=True,cart_id=cart_id,cart_status="Inprogress",
                    sitecode=site.itemsite_code,cart_date=date.today(),cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx)
                    for cart in cart_ids:
                        ItemCart.objects.filter(pk=cart.pk).update(cart_status='Completed',quantity=-cart.quantity)
                    
                    result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False,
                    'data':{'sa_transacno':finalsatrasc if finalsatrasc else None}}
                    savalue = sa_transacno_update_void(self, site, fmspw[0]) 
                    return Response(data=result, status=status.HTTP_200_OK)

        except Exception as e:
           invalid_message = str(e)
           return general_error_response(invalid_message)




class VoidCheck(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = VoidListSerializer

    def list(self, request):
        try:
            if str(self.request.GET.get('cust_id',None)) != "undefined":
                if isinstance(int(self.request.GET.get('cust_id',None)), int):
                    fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
                    site = fmspw.loginsite
                    cust_id = self.request.GET.get('cust_id',None)
                    cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
                    if cust_obj is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer id!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    if str(self.request.GET.get('cust_id',None)) == "undefined":
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select customer!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)         
                    
                    control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not control_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    # poshdr_id = self.request.GET.get('poshdr_id',None)
                
                    # queryset = ItemCart.objects.filter(isactive=True,cart_date=date.today(),customercode=cust_obj.cust_code,
                    # sitecode=site.itemsite_code,cart_status="Inprogress",is_payment=False).exclude(type__in=type_tx)
                    #sa_date__date=date.today()

                    # queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    # isvoid=False,ItemSite_Codeid__pk=site.pk).only('sa_custno','isvoid','cart_id',
                    # 'itemsite_code').exclude(cart_id=None).order_by('pk')

                    queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    isvoid=False).only('sa_custno','isvoid','cart_id',
                    'itemsite_code').exclude(cart_id=None).order_by('pk')
                    
                    # print(queryset,"queryset")
                    oldidcart = list(set([q.cart_id for q in queryset if q.cart_id]))
                    # print(oldidcart,"oldidcart")

                    # old_cart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                    # cart_id__in=oldidcart,sitecode=site.itemsite_code,isactive=True,
                    # cart_status="Inprogress").filter(~Q(cart_date=date.today())).exclude(type__in=type_tx).order_by('pk')
                    
                    old_cart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                    cart_id__in=oldidcart,isactive=True,
                    cart_status="Inprogress").filter(~Q(cart_date=date.today())).exclude(type__in=type_tx).order_by('pk')
                    
                    todidcart = list(set([t.cart_id for t in old_cart_ids if t.cart_id]))
                    # print(todidcart,"todidcart")
                    
                    if queryset:
                        if len(queryset) >= 1:
                            #previous record
                            # query_set = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                            # isvoid=False,ItemSite_Codeid__pk=site.pk,cart_id__in=todidcart).only('sa_custno','isvoid',
                            # 'cart_id','itemsite_code').exclude(cart_id=None).order_by('pk')

                            query_set = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                            isvoid=False,cart_id__in=todidcart).only('sa_custno','isvoid',
                            'cart_id','itemsite_code').exclude(cart_id=None).order_by('pk')
                            
                            # print(query_set,"query_set")
                            
                            for q in query_set:
                                # active / Inactive , not today rec
                                q.cart_id = None
                                q.save()
                                # idscart = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                # cart_id__in=todidcart,sitecode=site.itemsite_code,
                                # cart_status="Inprogress").filter(~Q(cart_date=date.today())).exclude(type__in=type_tx).delete()
                                idscart = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                cart_id__in=todidcart,
                                cart_status="Inprogress").filter(~Q(cart_date=date.today())).exclude(type__in=type_tx).delete()
                               
                                # print(idscart,"idscart")

                            #today record
                            # querysetafter = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                            # isvoid=False,ItemSite_Codeid__pk=site.pk).only('sa_custno','isvoid','cart_id',
                            # 'itemsite_code').exclude(cart_id=None).order_by('pk')

                            querysetafter = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                            isvoid=False).only('sa_custno','isvoid','cart_id',
                            'itemsite_code').exclude(cart_id=None).order_by('pk')


                            idcart = list(set([e.cart_id for e in querysetafter if e.cart_id]))

                            # idscart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                            # cart_id__in=idcart,sitecode=site.itemsite_code,cart_date=date.today(),
                            # isactive=True,cart_status="Inprogress").exclude(type__in=type_tx).order_by('pk')
                            # print(idscart_ids,"idscart_ids")

                            idscart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                            cart_id__in=idcart,cart_date=date.today(),
                            isactive=True,cart_status="Inprogress").exclude(type__in=type_tx).order_by('pk')
                           
                            
                            if len(querysetafter) > 1:
                                if idscart_ids:
                                    lastrec = idscart_ids.last()
                                    # print(lastrec,"lastrec")
                                    # del_query_set = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                                    # isvoid=False,ItemSite_Codeid__pk=site.pk).only('sa_custno','isvoid',
                                    # 'cart_id','itemsite_code').filter(~Q(cart_id=lastrec.cart_id)).exclude(cart_id=None).order_by('pk')
                                    # print(del_query_set,"del_query_set")

                                    del_query_set = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                                    isvoid=False,).only('sa_custno','isvoid',
                                    'cart_id','itemsite_code').filter(~Q(cart_id=lastrec.cart_id)).exclude(cart_id=None).order_by('pk')
                                    

                                    for dq in del_query_set:
                                        dq.cart_id = None
                                        dq.save()
                                        # idscart = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                        # cart_id=dq.cart_id,sitecode=site.itemsite_code,cart_date=date.today(),
                                        # cart_status="Inprogress").filter(~Q(cart_id=lastrec.cart_id)).exclude(type__in=type_tx).delete()
                                        
                                        idscart = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                        cart_id=dq.cart_id,cart_date=date.today(),
                                        cart_status="Inprogress").filter(~Q(cart_id=lastrec.cart_id)).exclude(type__in=type_tx).delete()
                                        
                            
                            #cartre = ItemCart.objects.filter(sitecodeid=site).order_by('cart_id')
                            cartre = ItemCart.objects.filter(sitecodeid=site).order_by('-cart_id')[:2]
                            final = list(set([r.cart_id for r in cartre]))
                            code_site = site.itemsite_code
                            prefix = control_obj.control_prefix
                            silicon = 6
                            system_setup = Systemsetup.objects.filter(title='ICControlnoslice',value_name='ICControlnoslice',isactive=True).first()
                            if system_setup and system_setup.value_data: 
                                silicon = int(system_setup.value_data)
      

                            clst = []
                            if final != []:
                                for f in final:
                                    fhstr = int(f[silicon:])
                                    # newstr = f.replace(prefix,"")
                                    # new_str = newstr.replace(code_site, "")
                                    clst.append(fhstr)
                                    clst.sort(reverse=True)

                                # print(clst,"clst")
                                cart_id = int(clst[0]) + 1
                                # cart_id = int(clst[0][-6:]) + 1
                                
                                control_obj.control_no = str(cart_id)
                                control_obj.save()

                            savalue = sa_transacno_update_void(self, site, fmspw) 

                            last_rec = idscart_ids.last()
                            if last_rec:
                                # ids_cart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                # cart_id=last_rec.cart_id,sitecode=site.itemsite_code,cart_date=date.today(),
                                # isactive=True,cart_status="Inprogress").exclude(type__in=type_tx).order_by('pk')
                                # print(ids_cart_ids,"ids_cart_ids")

                                ids_cart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                cart_id=last_rec.cart_id,cart_date=date.today(),
                                isactive=True,cart_status="Inprogress").exclude(type__in=type_tx).order_by('pk')
                                
                                if ids_cart_ids:
                                    # finalquery = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                                    # isvoid=False,ItemSite_Codeid__pk=site.pk,cart_id=last_rec.cart_id).only('sa_custno','isvoid','cart_id',
                                    # 'itemsite_code').exclude(cart_id=None).order_by('pk')
                                    finalquery = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                                    isvoid=False,cart_id=last_rec.cart_id).only('sa_custno','isvoid','cart_id',
                                    'itemsite_code').exclude(cart_id=None).order_by('pk')
                                    

                                    if finalquery:
                                        serializer = VoidListSerializer(finalquery, many=True)
                                        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
                                    else:
                                        result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                                else:
                                    result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                            else:
                                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                    else:
                        result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                    return Response(data=result, status=status.HTTP_200_OK) 
            else:
                result = {'status': status.HTTP_200_OK,"message":"No Data",'error': False, "data":[]}
                return Response(data=result, status=status.HTTP_200_OK)           
        except Exception as e:
           invalid_message = str(e)
           return general_error_response(invalid_message)

class VoidCancel(generics.CreateAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = VoidCancelSerializer
    
    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            serializer = self.get_serializer(data=request.data)
            # print(serializer,"serializer")
            if serializer.is_valid():
                # print(request.data,"request.data")
                cart_id = request.data['cart_id']
                # print(cart_id,"cart_id")
                if cart_id:
                    # print(cart_id,"cart_id")
                    bro_ids = ItemCart.objects.filter(cart_id=cart_id,sitecode=site.itemsite_code,
                    cart_status="Inprogress",cart_date=date.today())
                    if bro_ids:
                        queryset = PosHaud.objects.filter(cart_id=cart_id,sa_custno=bro_ids[0].customercode,
                        isvoid=False,ItemSite_Codeid__pk=site.pk).only('isvoid','cart_id',
                        'sa_custno','itemsite_code').exclude(cart_id=None).order_by('pk')
                        if queryset:
                            queryset[0].cart_id = None
                            queryset[0].save()
                        #cart_date=date.today()
                        ids_cart = ItemCart.objects.filter(cart_id=cart_id,cust_noid=bro_ids[0].cust_noid,
                        sitecode=site.itemsite_code,cart_status="Inprogress").exclude(type__in=type_tx).delete()
                        result = {'status': status.HTTP_200_OK,"message":"Void Cancelled Successfully",'error': False}
                        return Response(data=result, status=status.HTTP_200_OK) 
                    else:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"ItemCart is not in Inprogress so cant delete!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID !!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 
                                
            else:
                data = serializer.errors
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['cart_id'][0],'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
            
            

class VoidReasonViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = VoidReason.objects.filter(isactive=True).order_by('pk')
    serializer_class = VoidReasonSerializer

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


def getPdfPage(request):

    all_student= Customer.objects.filter()[:50]
    data={'customer':all_student}
    template = get_template("pdf_page.html")
    data_p = template.render(data)
    response = BytesIO()

    pdfPage=pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")),response)
    if not pdfPage.err:
        return HttpResponse(response.getvalue(),content_type="application/pdf")
    else:
        return HttpResponse("Error Generating PDF")

                      
               

class TreatmentAccListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentAccSerializer

    def list(self, request):
        try:
            now = timezone.now()
            print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
        
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).only('pk','cust_isactive').first()
            if not cust_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 

            if not self.request.GET.get('show_type',None):
                result = {'status': status.HTTP_200_OK,"message":"Please give show_type !!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  
                

            if self.request.GET.get('year',None):
                year = self.request.GET.get('year',None)
                if self.request.GET.get('show_type',None) == '1':
                    if year != "All":
                        queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
                        open_session__gt=0, treatment_date__year=year).order_by('-pk')
                    else:
                        queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,open_session__gt=0).order_by('-pk')
                elif self.request.GET.get('show_type',None) == '0':
                    if year != "All":
                        queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,
                        open_session__gte=0, treatment_date__year=year).order_by('-pk')
                    else:
                        queryset = TreatmentPackage.objects.filter(cust_code=cust_obj.cust_code,open_session__gte=0).order_by('-pk')

            else:
                result = {'status': status.HTTP_200_OK,"message":"Please give year!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  

            values = self.request.GET.get('value', None)
            key = self.request.GET.get('key', None)
            if values and key is not None:
                if values == "asc":
                    if key == 'sa_date':
                        queryset = queryset.order_by('treatment_date')
                elif values == "desc":
                    if key == 'sa_date':
                        queryset = queryset.order_by('-treatment_date')   
            
            # print(queryset,"queryset 77")
            if queryset:
                trb_ids = queryset.aggregate(balance=Coalesce(Sum('balance'), 0),outstanding=Coalesce(Sum('outstanding'), 0)) 
                full_tot = queryset.count()
                # print(full_tot,"full_tot")
                limit = self.request.GET.get('limit',None)
                if not limit:
                    limit = full_tot
                
                # print(limit,"limit")
                # try:
                #     limit = int(request.GET.get("limit",12))
                # except:
                #     # limit = 8
                #     limit = full_tot
                     
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(queryset, limit)
                total_page = paginator.num_pages

                try:
                    queryset = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page
                
                serializer = TreatmentPackgeSerializer(queryset, many=True, context={'request': self.request})

                # lst = []; id_lst = []; balance = 0; outstanding = 0
                # for data in queryset:
                #     dic = {}
                #     trobj = TreatmentAccount.objects.filter(treatment_parentcode=data.treatment_parentcode,
                #     sa_transacno=data.sa_transacno,type='Deposit').first()
                #     #open_trmids = Treatment.objects.filter(cust_code=trobj.cust_code,treatment_parentcode=trobj.treatment_parentcode,
                #     #site_code=site.itemsite_code,sa_transacno=trobj.ref_transacno,status='Open').count()
                #     open_trmids = Treatment.objects.filter(cust_code=trobj.cust_code,treatment_parentcode=trobj.treatment_parentcode,
                #     sa_transacno=trobj.ref_transacno,status='Open').count()
                #     # print(open_trmids,"open_trmids")
                    
                #     dic['qty'] = trobj.qty
                #     dic['id'] = trobj.pk
                #     dic['treatment_parentcode'] = trobj.treatment_parentcode
                    
                #     # trmids = Treatment.objects.filter(treatment_account__pk=trobj.pk,site_code=site.itemsite_code).only('treatment_account').first()
                #     #trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode,
                #     #site_code=site.itemsite_code).only('treatment_parentcode').first()
                #     trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode).only('treatment_parentcode').order_by('-pk').first()

                    
                #     dic['balance_qty'] = open_trmids


                #     if data.id not in id_lst:
                #         id_lst.append(data.id)
                    
                #     # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                #     # sa_transacno=trobj.sa_transacno,sa_transacno_type='Receipt',
                #     # itemsite_code=fmspw.loginsite.itemsite_code).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
                #     # sa_transacno_type__in=['Receipt','NON SALES']

                #     #pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                #     #sa_transacno=trobj.sa_transacno,itemsite_code=fmspw.loginsite.itemsite_code
                #     #).only('sa_custno','sa_transacno').order_by('pk').first()
                #     pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                #     sa_transacno=trobj.sa_transacno
                #     ).only('sa_custno','sa_transacno').order_by('pk').first()
                    
                #     if pos_haud:
                #         dic['transaction'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                #         if pos_haud.sa_date:
                #             splt = str(pos_haud.sa_date).split(" ")
                #             dtime = str(pos_haud.sa_time).split(" ")
                #             time = dtime[1].split(":")

                #             time_data = time[0]+":"+time[1]
                    
                #             dic['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")+" "+str(time_data)
                        
                #         dic['description'] = ""
                #         if trmids:
                #             if trmids.course:
                #                 dic['description'] = trmids.course 
                                
                #         sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                #         treatment_parentcode=trobj.treatment_parentcode,
                #         type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').aggregate(Sum('deposit'))
                #         if sumacc_ids:
                #             dic["payment"] = "{:.2f}".format(float(sumacc_ids['deposit__sum']))
                #         else:
                #             dic["payment"] = "0.00"

                #         acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                #         treatment_parentcode=trobj.treatment_parentcode
                #         ).only('ref_transacno','treatment_parentcode','site_code').order_by('-sa_date','-sa_time','-id').first()
                #         if acc_ids.balance:
                #             dic["balance"] = "{:.2f}".format(float(acc_ids.balance))
                #             balance += acc_ids.balance
                #         else:
                #             dic["balance"] = "0.00"

                #         if acc_ids.outstanding:   
                #             dic["outstanding"] = "{:.2f}".format(float(acc_ids.outstanding))
                #             outstanding += acc_ids.outstanding
                #         else:
                #             dic["outstanding"] = "0.00"

                #         lst.append(dic)
                
            
                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
                time = str(datetime.datetime.now().time()).split(":")

                time_data = time[0]+":"+time[1]
                
                title = Title.objects.filter(product_license=site.itemsite_code).first()

                path = None;logo = ""
                if title and title.logo_pic:
                    path = BASE_DIR + title.logo_pic.url
                    # logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url
                    logo = str(SITE_ROOT) + str(title.logo_pic)

                
                
                header_data = {"balance" : "{:.2f}".format(float(trb_ids['balance'])),
                "outstanding" : "{:.2f}".format(float(trb_ids['outstanding'])), 
                # "treatment_count" : len(id_lst),
                "treatment_count" : len(serializer.data),
                'year':self.request.GET.get('year'),'logo':logo,'date':current_date+" "+time_data,
                'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name,'issued': fmspw.pw_userlogin,
                'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else ''}

               
                now1 = timezone.now()
                print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
                totalh = now1.second - now.second
                print(totalh,"total")

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'header_data':header_data, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,
                "total":full_tot,"total_pages":total_page}}, 'dataList': serializer.data}}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                # serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)



    # def list(self, request):
    #     try:
    #         fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
    #         site = fmspw.loginsite
    #         cust_id = self.request.GET.get('cust_id',None)
    #         cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).only('pk','cust_isactive').first()
    #         if not cust_obj:
    #             result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
    #             return Response(data=result, status=status.HTTP_200_OK)  

    #         if self.request.GET.get('year',None):
    #             year = self.request.GET.get('year',None)
    #             if year != "All":
    #                 queryset = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,sa_date__year=year,type='Deposit').exclude(sa_status="VOID").only('site_code','cust_code','sa_date','type').order_by('-sa_date','-pk')
    #             else:
    #                 queryset = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,type='Deposit').exclude(sa_status="VOID").only('site_code','cust_code','type').order_by('-sa_date','-pk')
    #         else:
    #             result = {'status': status.HTTP_200_OK,"message":"Please give year!!",'error': True} 
    #             return Response(data=result, status=status.HTTP_200_OK)  
            
    #         values = self.request.GET.get('value', None)
    #         key = self.request.GET.get('key', None)
    #         if values and key is not None:
    #             if values == "asc":
    #                 if key == 'sa_date':
    #                     queryset = queryset.order_by('sa_date')
    #             elif values == "desc":
    #                 if key == 'sa_date':
    #                     queryset = queryset.order_by('-sa_date')   

    #         if queryset:
    #             serializer = self.get_serializer(queryset, many=True)
    #             lst = []; id_lst = []; balance = 0; outstanding = 0
    #             for data in serializer.data:
    #                 value = False
    #                 trobj = TreatmentAccount.objects.filter(pk=data["id"]).first()
    #                 #open_trmids = Treatment.objects.filter(cust_code=trobj.cust_code,treatment_parentcode=trobj.treatment_parentcode,
    #                 #site_code=site.itemsite_code,sa_transacno=trobj.ref_transacno,status='Open').count()
    #                 open_trmids = Treatment.objects.filter(cust_code=trobj.cust_code,treatment_parentcode=trobj.treatment_parentcode,
    #                 sa_transacno=trobj.ref_transacno,status='Open').count()
    #                 # print(open_trmids,"open_trmids")
    #                 if self.request.GET.get('show_type',None) == '1':
    #                     if open_trmids > 0:
    #                         value = True
    #                 else:
    #                     if self.request.GET.get('show_type',None) == '0':
    #                         if open_trmids >= 0:
    #                             value = True         


    #                 if value == True:
    #                     data['qty'] = trobj.qty
                        
    #                     # trmids = Treatment.objects.filter(treatment_account__pk=trobj.pk,site_code=site.itemsite_code).only('treatment_account').first()
    #                     #trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode,
    #                     #site_code=site.itemsite_code).only('treatment_parentcode').first()
    #                     trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode).only('treatment_parentcode').order_by('-pk').first()

                        
    #                     data['balance_qty'] = open_trmids


    #                     # print(data,"data")
    #                     if data["id"] not in id_lst:
    #                         id_lst.append(data["id"])
                        
    #                     # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
    #                     # sa_transacno=trobj.sa_transacno,sa_transacno_type='Receipt',
    #                     # itemsite_code=fmspw.loginsite.itemsite_code).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
    #                     # sa_transacno_type__in=['Receipt','NON SALES']

    #                     #pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
    #                     #sa_transacno=trobj.sa_transacno,itemsite_code=fmspw.loginsite.itemsite_code
    #                     #).only('sa_custno','sa_transacno').order_by('pk').first()
    #                     pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
    #                     sa_transacno=trobj.sa_transacno
    #                     ).only('sa_custno','sa_transacno').order_by('pk').first()
                        
    #                     if pos_haud:
    #                         data['transaction'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
    #                         if pos_haud.sa_date:
    #                             splt = str(pos_haud.sa_date).split(" ")
    #                             dtime = str(pos_haud.sa_time).split(" ")
    #                             time = dtime[1].split(":")

    #                             time_data = time[0]+":"+time[1]
                        
    #                             data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")+" "+str(time_data)
                            
    #                         data['description'] = ""
    #                         if trmids:
    #                             if trmids.course:
    #                                 data['description'] = trmids.course 
                                    
    #                         sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #                         treatment_parentcode=data["treatment_parentcode"],
    #                         type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').aggregate(Sum('deposit'))
    #                         if sumacc_ids:
    #                             data["payment"] = "{:.2f}".format(float(sumacc_ids['deposit__sum']))
    #                         else:
    #                             data["payment"] = "0.00"

    #                         acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #                         treatment_parentcode=data["treatment_parentcode"]
    #                         ).only('ref_transacno','treatment_parentcode','site_code').order_by('-sa_date','-sa_time','-id').first()
    #                         if acc_ids.balance:
    #                             data["balance"] = "{:.2f}".format(float(acc_ids.balance))
    #                             balance += acc_ids.balance
    #                         else:
    #                             data["balance"] = "0.00"

    #                         if acc_ids.outstanding:   
    #                             data["outstanding"] = "{:.2f}".format(float(acc_ids.outstanding))
    #                             outstanding += acc_ids.outstanding
    #                         else:
    #                             data["outstanding"] = "0.00"

    #                         lst.append(data)
                    

    #             if lst != []:

    #                 current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
    #                 time = str(datetime.datetime.now().time()).split(":")

    #                 time_data = time[0]+":"+time[1]
                    
    #                 title = Title.objects.filter(product_license=site.itemsite_code).first()

    #                 path = None;logo = ""
    #                 if title and title.logo_pic:
    #                     path = BASE_DIR + title.logo_pic.url
    #                     logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url


    #                 header_data = {"balance" : "{:.2f}".format(float(balance)),
    #                 "outstanding" : "{:.2f}".format(float(outstanding)), "treatment_count" : len(id_lst),
    #                 'year':self.request.GET.get('year'),'logo':logo,'date':current_date+" "+time_data,
    #                 'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name,'issued': fmspw.pw_userlogin,
    #                 'name': title.trans_h1 if title and title.trans_h1 else '', 
    #                 'address': title.trans_h2 if title and title.trans_h2 else ''}

    #                 result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
    #                 'header_data':header_data, 'data': lst}

    #                 if self.request.GET.get('pdf'):
                       
    #                     data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
    #                     'address': title.trans_h2 if title and title.trans_h2 else '', 
    #                     'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
    #                     'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
    #                     'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
    #                     'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
    #                     'path':path if path else '','data': lst,'cust_obj':cust_obj,'date':current_date,
    #                     'time':time,'fmspw':fmspw
    #                     }
    #                     data.update(header_data)

    #                     template = get_template('treatacc_front.html')
    #                     display = Display(visible=0, size=(800, 600))
    #                     display.start()
    #                     html = template.render(data)
    #                     options = {
    #                         'margin-top': '.25in',
    #                         'margin-right': '.25in',
    #                         'margin-bottom': '.25in',
    #                         'margin-left': '.25in',
    #                         'encoding': "UTF-8",
    #                         'no-outline': None,
    #                     }

    #                     dst ="treatacc_front.pdf"

    #                     response = BytesIO()

    #                     p=pisa.pisaDocument(BytesIO(html.encode("UTF-8")),response)
    #                     # print(p,"pp")
    #                     # if not pdfPage.err:
    #                     #     return HttpResponse(response.getvalue(),content_type="application/pdf")
    #                     # else:
    #                     #     return HttpResponse("Error Generating PDF")


    #                     # p=pdfkit.from_string(html,False,options=options)
    #                     PREVIEW_PATH = dst
    #                     pdf = FPDF() 

    #                     pdf.add_page() 
                        
    #                     pdf.set_font("Arial", size = 15) 
    #                     file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
    #                     pdf.output(file_path) 

    #                     if p:
    #                         # print("iff")
    #                         file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
    #                         report = os.path.isfile(file_path)
    #                         if report:
    #                             file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
    #                             # print(file_path,"file_path")
    #                             with open(file_path, 'wb') as fh:
    #                                 fh.write(response.getvalue())
    #                                 # fh.write(p)

    #                             # print(fh,"fh")    
    #                             display.stop()

    #                             ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/treatacc_front.pdf"

    #                             result = {'status': status.HTTP_200_OK, "message": "PDF Generated Successfully", 'error': False,
    #                             'data': ip_link}
    #                             return Response(data=result, status=status.HTTP_200_OK)

    #                 return Response(data=result, status=status.HTTP_200_OK)
    #             else:
    #                 result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
    #                 return Response(data=result, status=status.HTTP_200_OK)
    #         else:
    #             result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
    #             return Response(data=result, status=status.HTTP_200_OK)

    #     except Exception as e:
    #        invalid_message = str(e)
    #        return general_error_response(invalid_message)     


    # def list(self, request):
    #     try:
    #         fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
    #         site = fmspw.loginsite
    #         cust_id = self.request.GET.get('cust_id',None)
    #         cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).only('pk','cust_isactive').first()
    #         if not cust_obj:
    #             result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
    #             return Response(data=result, status=status.HTTP_200_OK)  

    #         if self.request.GET.get('year',None):
    #             year = self.request.GET.get('year',None)
    #             if year != "All":
    #                 queryset = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,sa_date__year=year,type='Deposit').exclude(sa_status="VOID").only('site_code','cust_code','sa_date','type').order_by('-sa_date','-pk')
    #             else:
    #                 queryset = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,type='Deposit').exclude(sa_status="VOID").only('site_code','cust_code','type').order_by('-sa_date','-pk')
    #         else:
    #             result = {'status': status.HTTP_200_OK,"message":"Please give year!!",'error': True} 
    #             return Response(data=result, status=status.HTTP_200_OK)  
            
    #         value = self.request.GET.get('value', None)
    #         key = self.request.GET.get('key', None)
    #         if value and key is not None:
    #             if value == "asc":
    #                 if key == 'sa_date':
    #                     queryset = queryset.order_by('sa_date')
    #             elif value == "desc":
    #                 if key == 'sa_date':
    #                     queryset = queryset.order_by('-sa_date') 

    #         limit = int(request.GET.get('limit',10)) if request.GET.get('limit',10) else 10
    #         page= int(request.GET.get('page',1)) if request.GET.get('page',1) else 1
    #         if page <= 0:
    #             raise Exception('Page less than one not allowed!!')     


    #         paginator = Paginator(queryset, limit) # chunks of 1000
    #         total_page = 1;total = len(queryset)
    #         if len(queryset) > int(limit):
    #             total_page = math.ceil(len(queryset)/int(limit))

    #         if queryset:
    #             if int(page) > total_page:
    #                 result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 
    #                 'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,"total_pages":total_page}}, 
    #                 'dataList': []}}
    #                 return Response(result, status=status.HTTP_200_OK) 


    #         # per = paginator.page(page)
    #         # print(per,"PPPPPPPPPPPPPPPPPP")
            
    #         # print(paginator.num_pages,"paginator.num_pages")
    #         # for page_idx in range(1, paginator.num_pages+1):
    #         #     # print(page_idx,"KKKKKKKKKKKKKKKKKKKKK")
    #         #     if page_idx == page:
    #         lst = [] ;id_lst = []; balance = 0; outstanding = 0;
    #         for row in paginator.page(page).object_list:
    #             # print(row,"row")
    #             trobj_ids = TreatmentAccount.objects.filter(pk=row.pk) 
    #             # print(trobj_ids,"trobj_ids")
    #             serializer = self.get_serializer(trobj_ids, many=True)
    #             # print(serializer,"serializer")
                
    #             for data in serializer.data:
    #                 # print(data,"data")
    #                 value = False
    #                 trobj = TreatmentAccount.objects.filter(pk=data["id"]).first()
    #                 #open_trmids = Treatment.objects.filter(cust_code=trobj.cust_code,treatment_parentcode=trobj.treatment_parentcode,
    #                 #site_code=site.itemsite_code,sa_transacno=trobj.ref_transacno,status='Open').count()
    #                 open_trmids = Treatment.objects.filter(cust_code=trobj.cust_code,treatment_parentcode=trobj.treatment_parentcode,
    #                 sa_transacno=trobj.ref_transacno,status='Open').count()
    #                 # print(open_trmids,"open_trmids")
    #                 if self.request.GET.get('show_type',None) == '1':
    #                     if open_trmids > 0:
    #                         value = True
    #                 else:
    #                     if self.request.GET.get('show_type',None) == '0':
    #                         if open_trmids >= 0:
    #                             value = True         


    #                 if value == True:
    #                     data['qty'] = trobj.qty
                        
    #                     # trmids = Treatment.objects.filter(treatment_account__pk=trobj.pk,site_code=site.itemsite_code).only('treatment_account').first()
    #                     #trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode,
    #                     #site_code=site.itemsite_code).only('treatment_parentcode').first()
    #                     trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode).only('treatment_parentcode').order_by('-pk').first()

                        
                            
    #                     data['balance_qty'] = open_trmids


    #                     # print(data,"data")
    #                     if data["id"] not in id_lst:
    #                         id_lst.append(data["id"])
                        
    #                     # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
    #                     # sa_transacno=trobj.sa_transacno,sa_transacno_type='Receipt',
    #                     # itemsite_code=fmspw.loginsite.itemsite_code).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
    #                     # sa_transacno_type__in=['Receipt','NON SALES']

    #                     #pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
    #                     #sa_transacno=trobj.sa_transacno,itemsite_code=fmspw.loginsite.itemsite_code
    #                     #).only('sa_custno','sa_transacno').order_by('pk').first()
    #                     pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
    #                     sa_transacno=trobj.sa_transacno
    #                     ).only('sa_custno','sa_transacno').order_by('pk').first()
                        
    #                     if pos_haud:
    #                         data['transaction'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
    #                         if pos_haud.sa_date:
    #                             splt = str(pos_haud.sa_date).split(" ")
    #                             dtime = str(pos_haud.sa_time).split(" ")
    #                             time = dtime[1].split(":")

    #                             time_data = time[0]+":"+time[1]
                        
    #                             data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")+" "+str(time_data)
                            
    #                         data['description'] = ""
    #                         if trmids:
    #                             if trmids.course:
    #                                 data['description'] = trmids.course 
                                    
                            

    #                         sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #                         treatment_parentcode=data["treatment_parentcode"],
    #                         type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').aggregate(Sum('deposit'))
    #                         if sumacc_ids:
    #                             data["payment"] = "{:.2f}".format(float(sumacc_ids['deposit__sum']))
    #                         else:
    #                             data["payment"] = "0.00"    

    #                         # acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #                         # treatment_parentcode=data["treatment_parentcode"]
    #                         # ).only('ref_transacno','treatment_parentcode','site_code').last()

    #                         acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #                         treatment_parentcode=data["treatment_parentcode"]).order_by('-sa_date','-sa_time','-id').first()
                        
    #                         if acc_ids.balance:
    #                             data["balance"] = "{:.2f}".format(float(acc_ids.balance))
    #                             balance += acc_ids.balance
    #                         else:
    #                             data["balance"] = "0.00"

    #                         if acc_ids.outstanding:   
    #                             data["outstanding"] = "{:.2f}".format(float(acc_ids.outstanding))
    #                             outstanding += acc_ids.outstanding
    #                         else:
    #                             data["outstanding"] = "0.00"

    #                         lst.append(data)
                    

    #             if lst != []:

    #                 current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
    #                 time = str(datetime.datetime.now().time()).split(":")

    #                 time_data = time[0]+":"+time[1]
                    
    #                 title = Title.objects.filter(product_license=site.itemsite_code).first()

    #                 path = None;logo = ""
    #                 if title and title.logo_pic:
    #                     path = BASE_DIR + title.logo_pic.url
    #                     logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url


    #                 header_data = {"balance" : "{:.2f}".format(float(balance)),
    #                 "outstanding" : "{:.2f}".format(float(outstanding)), "treatment_count" : len(id_lst),
    #                 'year':self.request.GET.get('year'),'logo':logo,'date':current_date+" "+time_data,
    #                 'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name,'issued': fmspw.pw_userlogin,
    #                 'name': title.trans_h1 if title and title.trans_h1 else '', 
    #                 'address': title.trans_h2 if title and title.trans_h2 else ''}

    #                 result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
    #                 'header_data':header_data, 
    #                 'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
    #                 "total_pages":total_page}}, 'dataList': lst}}

    #                 if self.request.GET.get('pdf'):
                       
    #                     data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
    #                     'address': title.trans_h2 if title and title.trans_h2 else '', 
    #                     'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
    #                     'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
    #                     'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
    #                     'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
    #                     'path':path if path else '','data': lst,'cust_obj':cust_obj,'date':current_date,
    #                     'time':time,'fmspw':fmspw
    #                     }
    #                     data.update(header_data)

    #                     template = get_template('treatacc_front.html')
    #                     display = Display(visible=0, size=(800, 600))
    #                     display.start()
    #                     html = template.render(data)
    #                     options = {
    #                         'margin-top': '.25in',
    #                         'margin-right': '.25in',
    #                         'margin-bottom': '.25in',
    #                         'margin-left': '.25in',
    #                         'encoding': "UTF-8",
    #                         'no-outline': None,
    #                     }

    #                     dst ="treatacc_front.pdf"

    #                     response = BytesIO()

    #                     p=pisa.pisaDocument(BytesIO(html.encode("UTF-8")),response)
    #                     # print(p,"pp")
    #                     # if not pdfPage.err:
    #                     #     return HttpResponse(response.getvalue(),content_type="application/pdf")
    #                     # else:
    #                     #     return HttpResponse("Error Generating PDF")


    #                     # p=pdfkit.from_string(html,False,options=options)
    #                     PREVIEW_PATH = dst
    #                     pdf = FPDF() 

    #                     pdf.add_page() 
                        
    #                     pdf.set_font("Arial", size = 15) 
    #                     file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
    #                     pdf.output(file_path) 

    #                     if p:
    #                         # print("iff")
    #                         file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
    #                         report = os.path.isfile(file_path)
    #                         if report:
    #                             file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
    #                             # print(file_path,"file_path")
    #                             with open(file_path, 'wb') as fh:
    #                                 fh.write(response.getvalue())
    #                                 # fh.write(p)

    #                             # print(fh,"fh")    
    #                             display.stop()

    #                             ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/treatacc_front.pdf"

    #                             result = {'status': status.HTTP_200_OK, "message": "PDF Generated Successfully", 'error': False,
    #                             'data': ip_link}
    #                             return Response(data=result, status=status.HTTP_200_OK)

    #                 return Response(data=result, status=status.HTTP_200_OK)
    #             else:
    #                 result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
    #                 return Response(data=result, status=status.HTTP_200_OK)
    #         else:
    #             result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
    #             return Response(data=result, status=status.HTTP_200_OK)

    #     except Exception as e:
    #        invalid_message = str(e)
    #        return general_error_response(invalid_message)     


    def get_object(self, pk):
        #try:
            return TreatmentAccount.objects.get(pk=pk)
        #except TreatmentAccount.DoesNotExist:
        #    raise Http404

    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            account = self.get_object(pk)

            cust_obj = Customer.objects.filter(cust_code=account.cust_code,cust_isactive=True).first()
           
            # queryset = TreatmentAccount.objects.filter(ref_transacno=account.sa_transacno,
            # treatment_parentcode=account.treatment_parentcode
            # ).only('ref_transacno','treatment_parentcode','site_code').order_by('-sa_date','-sa_time','-id')
            
            queryset = TreatmentAccount.objects.filter(ref_transacno=account.sa_transacno,
            treatment_parentcode=account.treatment_parentcode
            ).only('ref_transacno','treatment_parentcode','site_code').order_by('sa_date','sa_time','id')

            #pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,
            #sa_transacno=account.sa_transacno,itemsite_code=account.site_code
            #).only('sa_custno','sa_transacno').order_by('pk').first()
            pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,
            sa_transacno=account.sa_transacno
            ).only('sa_custno','sa_transacno').order_by('pk').first()
            sa_transacno_ref = ""    
            if pos_haud:
                sa_transacno_ref = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                
            if queryset:
                last = queryset.last()
                serializer = self.get_serializer(queryset, many=True)
                for v in serializer.data:
                    v.pop('payment')
                    if v['sa_date']:
                        splt = str(v['sa_date']).split('T')
                        v['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

                    trobj = TreatmentAccount.objects.filter(pk=v["id"]).only('pk').first()
                    v['type'] = trobj.type
                    if trobj.amount:
                        v["amount"] = "{:.2f}".format(float(trobj.amount))
                    else:
                        v["amount"] = "0.00"    
                    if v["balance"]:
                        v["balance"] = "{:.2f}".format(float(v['balance']))
                    else:
                        v["balance"] = "0.00"
                    if v["outstanding"]:
                        v["outstanding"] = "{:.2f}".format(float(v['outstanding']))
                    else:
                        v["outstanding"] = "0.00"


                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
                time = str(datetime.datetime.now().time()).split(":")

                time_data = time[0]+":"+time[1]
                
                title = Title.objects.filter(product_license=site.itemsite_code).first()

                logo = ""
                if title and title.logo_pic:
                    # logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url
                    logo = str(SITE_ROOT) + str(title.logo_pic)
                
                expiry_date = ""
                treat_ids = Treatment.objects.filter(treatment_parentcode=account.treatment_parentcode).order_by('pk').first()       
                if treat_ids and treat_ids.expiry:
                    splte = str(treat_ids.expiry).split(' ')
                    expiry_date = datetime.datetime.strptime(str(splte[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                    

                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False,
                'header_data':{'credit_balance':"{:.2f}".format(float(last.balance)) if last.balance else "0.00",
                'outstanding_balance':"{:.2f}".format(float(last.outstanding)) if last.outstanding else "0.00",
                'sa_transacno_ref':sa_transacno_ref,'treatparent_code': last.treatment_parentcode,
                'logo':logo,'date':current_date+" "+time_data,
                'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name if cust_obj and cust_obj.cust_code and cust_obj.cust_name else '',
                'issued': fmspw.pw_userlogin,
                'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else '',
                'expiry_date' : expiry_date}, 
                'data': serializer.data}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
           invalid_message = str(e)
           return general_error_response(invalid_message)      


    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def service_expirydatechange(self, request): 
        try:  
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
                site = fmspw.loginsite
                log_emp = fmspw.Emp_Codeid

                if not request.data['treatment_parentcode']:
                    raise Exception('Please give treatment parentcode!!.') 
                
                if not request.data['expiry_date']:
                    raise Exception('Please give Expiry Date!!.') 

                if str(request.data['expiry_date']) < str(date.today()):
                    raise Exception('Expiry Date should not be past days!!.') 
    
                treat_ids = Treatment.objects.filter(treatment_parentcode=request.data['treatment_parentcode']).order_by('pk')   
                if not treat_ids:
                    raise Exception('Treatment parentcode IDs does not exist!!.')

                if not 'username' in request.data or not 'password' in request.data or not request.data['username'] or not request.data['password']:
                    raise Exception('Please Enter Valid Username and Password!!.') 

                if User.objects.filter(username=request.data['username']):
                    self.user = authenticate(username=request.data['username'], password=request.data['password'])
                    # print(self.user,"self.user")
                    if self.user:
                        
                        fmspw_c = Fmspw.objects.filter(user=self.user.id,pw_isactive=True)
                        if not fmspw_c:
                            raise Exception('User is inactive.') 

                        log_emp = fmspw_c[0].Emp_Codeid
                        if fmspw_c[0] and fmspw_c[0].flgchangeexpirydate == False:
                            raise Exception('Logined User not allowed to update service expiry date !!')
                    
                    else:
                        raise Exception('Password Wrong !') 

                else:
                    raise Exception('Invalid Username.')      

                if treat_ids:
                    for i in treat_ids:
                        i.expiry = request.data['expiry_date']
                        i.save()

                package_ids = TreatmentPackage.objects.filter(treatment_parentcode=request.data['treatment_parentcode']).first()
                if package_ids:
                    package_ids.expiry_date =  request.data['expiry_date']
                    package_ids.save()

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         
          


class CreditNoteListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CreditNoteSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
            site = fmspw[0].loginsite
            
            is_all = self.request.GET.get('is_all', None)
            if is_all:
                #queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code).only('cust_code').order_by('pk')
                queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code).only('cust_code').order_by('-pk','-sa_date')

            else:
                # queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code, status='OPEN',site_code=site.itemsite_code).only('cust_code','status').order_by('pk')
                queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code, status='OPEN').only('cust_code','status').order_by('-pk','-sa_date')

            
            
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = [];tot_balance = 0
                for data in serializer.data:
                    if data['sa_date']:
                        splt = str(data['sa_date']).split('T')
                        data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

                    crdobj = CreditNote.objects.filter(pk=data["id"]).first()
                    # sa_transacno_type='Receipt',
                    
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code, sa_transacno=crdobj.sa_transacno,
                    # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code, sa_transacno=crdobj.sa_transacno,
                    # sa_transacno_type='Receipt',ItemSite_Codeid__pk=site.pk).order_by('pk').first()
                    sa_transacno_type='Receipt').order_by('pk').first()
                                  
                    if pos_haud:
                        data['transaction'] = pos_haud.sa_transacno_ref
                    else:
                        data['transaction'] = "" 
                            
                    if data["amount"]:
                        data["amount"] = "{:.2f}".format(float(data['amount']))
                    else:
                        data["amount"] = "0.00"    
                    if data["balance"]:
                        data["balance"] = "{:.2f}".format(float(data['balance']))
                        tot_balance +=  crdobj.balance
                    else:
                        data["balance"] = "0.00" 
                          
                    lst.append(data)


                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
                time = str(datetime.datetime.now().time()).split(":")

                time_data = time[0]+":"+time[1]
                
                title = Title.objects.filter(product_license=site.itemsite_code).first()

                logo = ""
                if title and title.logo_pic:
                    # logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url
                    logo = str(SITE_ROOT) + str(title.logo_pic)

                header_data = {'logo':logo,'date':current_date+" "+time_data,
                'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name if cust_obj and cust_obj.cust_code and cust_obj.cust_name else '',
                'issued': fmspw[0].pw_userlogin,
                'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else '',
                'tot_balance': "{:.2f}".format(float(tot_balance))}    
            
                result = {'status': status.HTTP_200_OK, "message": "Listed Succesfully", 'error': False,
                'header_data': header_data ,'data': lst}
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def get_object(self, pk):
        try:
            return CreditNote.objects.get(pk=pk)
        except CreditNote.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            creditnote = self.get_object(pk)
            serializer = CreditNoteAdjustSerializer(creditnote,context={'request': self.request})
            adjustamt = 0.00
            val =  serializer.data
            data = {'id': val['id'],'credit_code': val['credit_code'],'balance': val['balance'],
            'new_balance': val['new_balance'],'refund_amt': val['refund_amt'],
            'adjust_amount':"{:.2f}".format(float(adjustamt))}

            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
            'data': data}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
            site = fmspw[0].loginsite
            new_balance = self.request.data.get('new_balance', None)
            refund_amt = self.request.data.get('refund_amt', None) 

            if new_balance is None and refund_amt is None:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Please give New Balance or refund amount!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if new_balance == "" or refund_amt == "":
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Please give Valid New Balance or refund amount!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if float(new_balance) < 0 or float(refund_amt) < 0:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Please give Valid New Balance or refund amount!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            creditnt = self.get_object(pk)
            #front calculation
            #adjust_amount = new_balance - creditnt.balance
            balance = creditnt.balance
        
            serializer = CreditNoteAdjustSerializer(creditnt, data=request.data, partial=True, context={'request': self.request})
            if serializer.is_valid():
                if float(new_balance) == float(refund_amt):
                    if float(new_balance) == balance:
                        result = {'status': status.HTTP_400_BAD_REQUEST, "message": "New Balance and Refund Amt, Existing credit note Balance should not be same!!", 'error': True}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                  
                if float(refund_amt) > float(balance):
                    result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Refund Amt Should not be greater than new balance!!", 'error': True}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                control_obj = ControlNo.objects.filter(control_description__iexact="Refund CN",Site_Codeid__pk=site.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Refund CN Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                refund_code = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)

                adjustamt = float(balance) - float(new_balance)

                if not refund_amt is None and float(refund_amt) > 0.00:
                    amount = refund_amt
                elif not refund_amt is None and float(refund_amt) == 0.00:  
                    amount = 0.00
        
                # print(amount,balance,adjustamt,new_balance,"daa")   
                cn_refund = CnRefund.objects.create(rfn_trans_no=refund_code,cn_no=creditnt.credit_code,
                site_code=site.itemsite_code,amount=amount,staff_code=fmspw[0].emp_code,transac_no=creditnt.sa_transacno,
                rfn_before_amt=balance,rfn_adjust_amt=adjustamt,rfn_new_amt=float(new_balance),
                rfn_date=timezone.now()) 

                if cn_refund.pk:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()

                if not new_balance is None and float(new_balance) > 0.00:
                    serializer.save(balance=new_balance,status="OPEN")
                elif not new_balance is None and float(new_balance) == 0.00:
                    serializer.save(balance=new_balance,status="CLOSE")

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        

class ProductPurchaseListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ProductPurchaseSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if not cust_obj:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)

            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
            site = fmspw.loginsite
            haud_ids = list(set(PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
            isvoid=False).order_by('pk').values_list('sa_transacno',flat=True).distinct()))
           
            query_set = PosDaud.objects.filter(sa_transacno__in=haud_ids,dt_status="SA",
            record_detail_type='PRODUCT').order_by('-pk')
            # print(query_set,"query_set")
           
            if query_set:
                full_tot = query_set.count()
                try:
                    limit = int(request.GET.get("limit",10))
                except:
                    limit = 10
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(query_set, limit)
                total_page = paginator.num_pages

                try:
                    queryset = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page

                serializer = self.get_serializer(queryset, many=True)

                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
                time = str(datetime.datetime.now().time()).split(":")

                time_data = time[0]+":"+time[1]
                
                title = Title.objects.filter(product_license=site.itemsite_code).first()

                logo = ""
                if title and title.logo_pic:
                    # logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url
                    logo = str(SITE_ROOT) + str(title.logo_pic)

                header_data = { 
                'logo':logo,'date':current_date+" "+time_data,
                'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name if cust_obj and cust_obj.cust_code and cust_obj.cust_name else '',
                'issued': fmspw.pw_userlogin,
                'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else ''}
                
                resData = {
                    'header_data':header_data,
                    'dataList': serializer.data,
                    'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
                    }
                }
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  resData}
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
       
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        



class ProductAccListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ProductAccSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)

            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
            site = fmspw.loginsite

            queryset = DepositAccount.objects.filter(cust_code=cust_obj.cust_code,
            type='Deposit').only('site_code','cust_code','type').order_by('-sa_date')
            
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = []; id_lst = []; balance = 0; outstanding = 0; hold_qty = 0
                for data in serializer.data:
                    depobj = DepositAccount.objects.filter(pk=data["id"]).only('pk').first()
                    if data["id"]:
                        id_lst.append(data["id"])
                    
                    # sa_transacno_type='Receipt',ItemSite_Codeid__pk=site.pk,
                    #pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    #sa_transacno=depobj.sa_transacno,itemsite_code=site.itemsite_code,
                    #).only('sa_custno','sa_transacno','itemsite_code').order_by('pk').first()
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    sa_transacno=depobj.sa_transacno,
                    ).only('sa_custno','sa_transacno','itemsite_code').order_by('pk').first()
                    if pos_haud:
                        data['transaction'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                        if pos_haud.sa_date:
                            splt = str(pos_haud.sa_date).split(" ")
                            data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        
                        if not data['package_code']:
                            data['package_code'] = ""

                        acc_ids = DepositAccount.objects.filter(sa_transacno=depobj.sa_transacno,
                        ref_productcode=depobj.ref_productcode
                        ).only('sa_transacno','site_code','ref_productcode').order_by('-sa_date','-sa_time','-id').first()
                        if acc_ids and acc_ids.balance:
                            data["balance"] = "{:.2f}".format(float(acc_ids.balance))
                            if acc_ids and not acc_ids.balance is None and acc_ids.balance > 0:
                                holdids = Holditemdetail.objects.filter(sa_transacno=depobj.sa_transacno,
                                itemno=depobj.item_barcode,sa_custno=depobj.cust_code,status='OPEN').only('sa_transacno','itemno').order_by('pk').last()  
                                if holdids or not acc_ids.outstanding is None and acc_ids.outstanding > 0:  
                                    balance += acc_ids.balance
                        else:
                            data["balance"] = "0.00"    
                        if acc_ids.outstanding:   
                            data["outstanding"] = "{:.2f}".format(float(acc_ids.outstanding))
                            outstanding += acc_ids.outstanding
                        else:
                            data["outstanding"] = "0.00"

                        holdids = Holditemdetail.objects.filter(sa_transacno=depobj.sa_transacno,
                        itemno=depobj.item_barcode,itemsite_code=site.itemsite_code,
                        sa_custno=cust_obj.cust_code).only('sa_transacno','itemno').last()  
                        if holdids:
                            data['item_status'] = holdids.status if holdids.status else ""
                            hold_qty += holdids.holditemqty
                            data["hold_qty"] = holdids.holditemqty  
                            data['hold_id']  =  holdids.pk                
                        else:
                            data['item_status'] = ""
                            data["hold_qty"] = ""
                            data['hold_id']  = ""              
                        
                       
                        lst.append(data)

                if lst != []:
                    current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
                    time = str(datetime.datetime.now().time()).split(":")

                    time_data = time[0]+":"+time[1]
                    
                    title = Title.objects.filter(product_license=site.itemsite_code).first()

                    logo = ""
                    if title and title.logo_pic:
                        # logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url
                        logo = str(SITE_ROOT) + str(title.logo_pic)

                    header_data = {"balance" : "{:.2f}".format(float(balance)), "totalholdqty" : hold_qty,
                    "outstanding" : "{:.2f}".format(float(outstanding)), "totalproduct_count" : len(id_lst),
                    'logo':logo,'date':current_date+" "+time_data,
                    'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name if cust_obj and cust_obj.cust_code and cust_obj.cust_name else '',
                    'issued': fmspw.pw_userlogin,
                    'name': title.trans_h1 if title and title.trans_h1 else '', 
                    'address': title.trans_h2 if title and title.trans_h2 else ''}
                    
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                    'header_data':header_data, 'data': lst}
                    return Response(data=result, status=status.HTTP_200_OK)
                else:
                    result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                    return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         
            
    
    def get_object(self, pk):
        try:
            return DepositAccount.objects.get(pk=pk)
        except DepositAccount.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            account = self.get_object(pk)
            cust_obj = Customer.objects.filter(cust_code=account.cust_code,cust_isactive=True).first()
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            queryset = DepositAccount.objects.filter(sa_transacno=account.sa_transacno,
            ref_productcode=account.ref_productcode).only('sa_transacno',
            'site_code','ref_productcode').order_by('-sa_date','-sa_time','-pk')

            #pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,
            #sa_transacno=account.sa_transacno,itemsite_code=site.itemsite_code,
            #).only('sa_custno','sa_transacno','itemsite_code').order_by('pk').first()
            pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,
            sa_transacno=account.sa_transacno
            ).only('sa_custno','sa_transacno','itemsite_code').order_by('pk').first()
            sa_transacno_ref = ""
            if pos_haud:
                sa_transacno_ref = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                
            if queryset:
                hold_qty = 0
                last = queryset.first()
                #holdids = Holditemdetail.objects.filter(sa_transacno=account.sa_transacno,
                #itemno=account.item_barcode,itemsite_code=site.itemsite_code,
                #sa_custno=account.cust_code).only('sa_transacno','itemno','itemsite_code','sa_custno').first()  
                holdids = Holditemdetail.objects.filter(sa_transacno=account.sa_transacno,
                itemno=account.item_barcode,
                sa_custno=account.cust_code).only('sa_transacno','itemno','itemsite_code','sa_custno').first()  
                if holdids:
                    hold_qty += holdids.holditemqty                    
                    
                serializer = self.get_serializer(queryset, many=True)
                for v in serializer.data:
                    v.pop('package_code');v.pop('item_description')
                    if v['sa_date']:
                        splt = str(v['sa_date']).split('T')
                        v['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

                    depobj = DepositAccount.objects.filter(pk=v["id"]).first()
                    v['description'] = depobj.description # transaction
                    v['type'] = depobj.type #treatment
                    if depobj.amount:
                        v["payment"] = "{:.2f}".format(float(depobj.amount))
                    else:
                        v["payment"] = "0.00"    
                    if v["balance"]:
                        v["balance"] = "{:.2f}".format(float(v['balance']))
                    else:
                        v["balance"] = "0.00"
                    if v["outstanding"]:
                        v["outstanding"] = "{:.2f}".format(float(v['outstanding']))
                    else:
                        v["outstanding"] = "0.00"


                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
                time = str(datetime.datetime.now().time()).split(":")

                time_data = time[0]+":"+time[1]
                
                title = Title.objects.filter(product_license=site.itemsite_code).first()

                logo = ""
                if title and title.logo_pic:
                    # logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url
                    logo = str(SITE_ROOT) + str(title.logo_pic)
    

                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False,
                'header_data':{'credit_balance':"{:.2f}".format(float(last.balance)) if last.balance else "0.00",
                'outstanding_balance':"{:.2f}".format(float(last.outstanding)) if last.outstanding else "0.00",
                "totalholdqty" : hold_qty,'sa_transacno_ref': sa_transacno_ref,
                'logo':logo,'date':current_date+" "+time_data,
                'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name if cust_obj and cust_obj.cust_code and cust_obj.cust_name else '',
                'issued': fmspw.pw_userlogin,
                'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else ''
                }, 
                'data': serializer.data}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


    @action(detail=False, methods=['get'], name='holditemacclist')
    def holditemacclist(self, request):
        try: 
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            deposit_id = self.request.GET.get('deposit_id', None)
            depo_obj = DepositAccount.objects.filter(pk=deposit_id).first()
            if depo_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "DepositAccount ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)

            pos_haud = PosHaud.objects.filter(sa_custno=depo_obj.cust_code,
            sa_transacno=depo_obj.sa_transacno
            ).only('sa_custno','sa_transacno','itemsite_code').order_by('pk').first()

            # hold_checkids = Holditemdetail.objects.filter(sa_transacno=depo_obj.sa_transacno,
            # itemno=depo_obj.item_barcode,
            # sa_custno=depo_obj.cust_code).only('sa_transacno','itemno','sa_custno').order_by('pk').first()

           
            holdids = Holditemdetail.objects.filter(sa_transacno=depo_obj.sa_transacno,
            itemno=depo_obj.item_barcode,
            sa_custno=depo_obj.cust_code).only('sa_transacno','itemno','sa_custno').order_by('pk')
           
            sa_transacno_ref = ""

            # if hold_checkids and hold_checkids.status == 'CLOSE' and len(hold_checkids) == 1:
            #     result = {'status': status.HTTP_200_OK, 'message': "No Content", 'error': False, 'data': []}
            #     return Response(data=result, status=status.HTTP_200_OK)
 

            if pos_haud and holdids:
                sa_transacno_ref = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""

                serializer = HolditemAccListSerializer(holdids, many=True)
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False,
                'data': serializer.data,
                'header_data':{'sa_transacno_ref':sa_transacno_ref,'transaction':depo_obj.sa_transacno,
                'qty_hold':holdids[0].holditemqty,'total_count':holdids.count()}
                }
                return Response(result, status=status.HTTP_200_OK)

            else:
                result = {'status': status.HTTP_200_OK, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
 
        except Exception as e:
           invalid_message = str(e)
           return general_error_response(invalid_message)     


                

class PrepaidAccListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = PrepaidAccSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)

            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
            site = fmspw.loginsite

            is_all = self.request.GET.get('is_all',None)
            if is_all:
                # queryset = PrepaidAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
                # sa_status__in=['DEPOSIT','SA']).only('site_code','cust_code','sa_status').order_by('pk')
                queryset = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,
                sa_status__in=['DEPOSIT']).exclude(sa_status='VT').only('site_code','cust_code','sa_status').order_by('-pk','-sa_date')

            else:
                # queryset = PrepaidAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
                # sa_status__in=['DEPOSIT','SA'],remain__gt=0).only('site_code','cust_code','sa_status').order_by('pk')
                queryset = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,
                status=True,remain__gt=0).exclude(sa_status='VT').only('site_code','cust_code','sa_status').order_by('-pk','-sa_date')


            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = []; id_lst = []; product_type = 0; service_type = 0; all_type = 0
                for data in serializer.data:
                    data.pop('voucher_no'); data.pop('condition_type1')
                    preobj = PrepaidAccount.objects.filter(pk=data["id"]).only('pk').first()
                    if data["id"]:
                        id_lst.append(data["id"])
                    
                    # sa_transacno_type='Receipt',ItemSite_Codeid__pk=site.pk
                    # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    # sa_transacno=preobj.pp_no,itemsite_code=site.itemsite_code,
                    # ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno=preobj.pp_no
                    ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
                    if pos_haud:
                        data['prepaid'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""

                        # last_acc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                        # site_code=preobj.site_code,status=True,line_no=preobj.line_no).only('pp_no','site_code','status','line_no').last()
                        if is_all:
                            last_acc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                            line_no=preobj.line_no).only('pp_no','site_code','status','line_no').order_by('pk').last()
                        else:
                            last_acc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                            status=True,line_no=preobj.line_no).order_by('pk').only('pp_no','site_code','status','line_no').last()
                        l_splt = str(data['last_update']).split("T")
                        data['last_update'] = datetime.datetime.strptime(str(l_splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        
                        # print(last_acc_ids.pk,"last_acc_ids")
                        if last_acc_ids:
                            if last_acc_ids.sa_date:
                                splt = str(last_acc_ids.sa_date).split(" ")
                                data['last_update'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        
                        # oriacc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                        # site_code=preobj.site_code,sa_status='DEPOSIT',line_no=preobj.line_no).only('pp_no','site_code','sa_status','line_no').first()
                        oriacc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                        sa_status='DEPOSIT',line_no=preobj.line_no).only('pp_no','site_code','sa_status','line_no').first()
                        if oriacc_ids:
                            if oriacc_ids.sa_date:
                                #purchase date
                                splt_st = str(oriacc_ids.sa_date).split(" ")
                                data['sa_date'] = datetime.datetime.strptime(str(splt_st[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        if last_acc_ids:
                            if last_acc_ids.pp_type:
                                rangeobj = ItemRange.objects.filter(itm_code=last_acc_ids.pp_type,itm_status=True).first()
                                if rangeobj:
                                    data['type'] = rangeobj.itm_desc
                                else:
                                    data['type'] = " "
            
                            if last_acc_ids.exp_date:
                                splt_ex = str(last_acc_ids.exp_date).split(" ")
                                data['exp_date'] = datetime.datetime.strptime(str(splt_ex[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                            if last_acc_ids.exp_status:
                                if last_acc_ids.exp_status == True:
                                    data['exp_status'] = "Open"
                                elif last_acc_ids.exp_status == False:
                                    data['exp_status'] = "Expired"
                            else:
                                data['exp_status'] = ""        

                            if last_acc_ids.pp_amt:
                                data['pp_amt'] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                            if last_acc_ids.pp_bonus:
                                data['pp_bonus'] = "{:.2f}".format(float(last_acc_ids.pp_bonus))
                            if last_acc_ids.pp_total:
                                data['pp_total'] = "{:.2f}".format(float(last_acc_ids.pp_total))
                            if last_acc_ids.use_amt >= 0:
                                data['use_amt'] = "{:.2f}".format(float(last_acc_ids.use_amt ))
                            if last_acc_ids.remain >= 0:
                            #     print(last_acc_ids.remain,"last_acc_ids.remain")
                                data['remain'] = "{:.2f}".format(float(last_acc_ids.remain))

                            # print(data['remain'],"data['remain']")    
                            
                            data['voucher'] = "P.P"
                            if last_acc_ids.topup_amt >= 0: # Deposit
                                data['topup_amt'] = "{:.2f}".format(float(last_acc_ids.topup_amt ))
                            if last_acc_ids.outstanding >= 0:
                                data['outstanding'] = "{:.2f}".format(float(last_acc_ids.outstanding))

                        open_ids = PrepaidAccountCondition.objects.filter(pp_no=preobj.pp_no,
                        pos_daud_lineno=preobj.line_no).only('pp_no','pos_daud_lineno').first()
                        data["conditiontype1"]=open_ids.conditiontype1               
                        data["product"] = 0.00;data["service"] = 0.00;data["all"] = 0.00
                        if open_ids.conditiontype1 == "Product Only":
                            data["product"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                            product_type += last_acc_ids.remain 
                        elif open_ids.conditiontype1 == "Service Only":
                            data["service"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                            service_type += last_acc_ids.remain
                        elif open_ids.conditiontype1 == "All":
                            data["all"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                            all_type += last_acc_ids.remain
        
                        lst.append(data)

                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
                time = str(datetime.datetime.now().time()).split(":")

                time_data = time[0]+":"+time[1]
                
                title = Title.objects.filter(product_license=site.itemsite_code).first()

                logo = ""
                if title and title.logo_pic:
                    # logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url
                    logo = str(SITE_ROOT) + str(title.logo_pic)
            

                if lst != []:
                    header_data = {"balance_producttype" : "{:.2f}".format(float(product_type)), 
                    "balance_servicetype" : "{:.2f}".format(float(service_type)),
                    "balance_alltype" : "{:.2f}".format(float(all_type)),"totalprepaid_count" : len(id_lst),
                    "logo":logo,'date':current_date+" "+time_data,
                    'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name if cust_obj and cust_obj.cust_code and cust_obj.cust_name else '',
                    'issued': fmspw.pw_userlogin,
                    'name': title.trans_h1 if title and title.trans_h1 else '', 
                    'address': title.trans_h2 if title and title.trans_h2 else ''}
                    
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                    'header_data':header_data, 'data': lst}
                    return Response(data=result, status=status.HTTP_200_OK)
                else:
                    result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                    return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         
            
    def get_object(self, pk):
        try:
            return PrepaidAccount.objects.get(pk=pk)
        except PrepaidAccount.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first() 
            site = fmspw.loginsite
            account = self.get_object(pk)
            cust_obj = Customer.objects.filter(cust_code=account.cust_code,cust_isactive=True).first()
            # queryset = PrepaidAccount.objects.filter(pp_no=account.pp_no,line_no=account.line_no,
            # site_code=account.site_code).only('pp_no','line_no').order_by('pk')
            queryset = PrepaidAccount.objects.filter(pp_no=account.pp_no,line_no=account.line_no
            ).only('pp_no','line_no').order_by('-pk','-sa_date')

            
            
            # last_acc_ids = PrepaidAccount.objects.filter(pp_no=account.pp_no,
            # site_code=account.site_code,status=True,line_no=account.line_no).only('pp_no','site_code','status','line_no').last()
            last_acc_ids = PrepaidAccount.objects.filter(pp_no=account.pp_no,
            line_no=account.line_no).only('pp_no','site_code','status','line_no').order_by('pk').last()
              
                      

            open_ids = PrepaidAccountCondition.objects.filter(pp_no=account.pp_no,
            pos_daud_lineno=account.line_no).only('pp_no','pos_daud_lineno').first()
            product_type = 0.00; service_type = 0.00; all_type = 0.00
            if open_ids.conditiontype1 == "Product Only":
                product_type += last_acc_ids.remain 
            elif open_ids.conditiontype1 == "Service Only":
                service_type += last_acc_ids.remain
            elif open_ids.conditiontype1 == "All":
                all_type += last_acc_ids.remain

            if queryset:
                last = queryset.last()
                serializer = PrepaidacSerializer(queryset, many=True)
                # sa_transacno_type='Receipt',ItemSite_Codeid__pk=site.pk
                # pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,
                # sa_transacno=account.pp_no,itemsite_code=site.itemsite_code,
                # ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
                pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,sa_transacno=account.pp_no,
                ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
           
                for v in serializer.data:
                    if pos_haud:
                        v['prepaid_ref'] = pos_haud.sa_transacno_ref
                    else:
                        v['prepaid_ref'] = "" 

                    
                    ppobj = PrepaidAccount.objects.filter(pk=v["id"]).first()
                    if ppobj.sa_status in ['DEPOSIT','TOPUP']:
                        v['old_transaction'] = "-"
                        v['transaction_ref'] = "-"
                        v['voucher#'] = "-"
                        v['item_no'] = "-"
                        v['item_name'] = "-"
                    elif ppobj.sa_status == 'SA':
                        if ppobj.transac_no:
                            poshaud = PosHaud.objects.filter(sa_custno=account.cust_code,
                            sa_transacno=ppobj.transac_no).only('sa_custno','sa_transacno').order_by('pk').first()
                            if poshaud:
                                v['old_transaction'] = poshaud.sa_transacno
                                v['transaction_ref'] = poshaud.sa_transacno_ref
                            else:
                                v['old_transaction'] = "-"
                                v['transaction_ref'] = "-"

                        v['voucher#'] = "-"
                        v['item_no'] = ppobj.item_no if ppobj.item_no else "-"
                        stockobj = Stock.objects.filter(item_code=ppobj.item_no).only('item_code').first()
                        if stockobj:
                            v['item_name'] = stockobj.item_name if stockobj.item_name else "-"
                        else:
                            v['item_name'] = "-"  
                    else:
                        v['old_transaction'] = "-";v['transaction_ref'] = "-";v['voucher#'] = "-";v['item_no'] = "-"
                        v['item_name'] = "-";

                    v['use_amt'] = "{:.2f}".format(float(v['use_amt'])) if v['use_amt'] else 0.00
                    if ppobj.sa_status == 'DEPOSIT':
                        v['topup_amt'] = "-"
                        v['topup_no'] = "-"
                        v['topup_date'] = "-"
                        v['status'] = "-"
                    elif ppobj.sa_status == 'TOPUP': 
                        v['topup_amt'] = "{:.2f}".format(float(v['topup_amt'])) if v['topup_amt'] else ""
                        v['topup_no'] = ppobj.topup_no
                        if ppobj.topup_date:
                            splt = str(ppobj.topup_date).split(" ")
                            v['topup_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        v['status'] = ppobj.sa_status
                    elif ppobj.sa_status == 'SA':
                        v['topup_amt'] = "-"
                        v['topup_no'] = "-"
                        v['topup_date'] = "-"
                        v['status'] = "-"
                    else:
                        v['topup_amt'] = "-";v['topup_no'] = "-";v['topup_date'] = "-";v['status'] = "-"

                    v['balance'] = "{:.2f}".format(float(ppobj.remain)) if ppobj.remain else 0.00  
                    v['supplementary'] = ""
                    v['remain'] = "{:.2f}".format(float(ppobj.remain))

                    if v['sa_date']:
                        splt_st = str(v['sa_date']).split("T")
                        v['sa_date'] = datetime.datetime.strptime(str(splt_st[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                

                # depoamt_acc_ids = PrepaidAccount.objects.filter(pp_no=account.pp_no,
                # site_code=account.site_code,line_no=account.line_no,sa_status__in=('DEPOSIT', 'TOPUP','SA')).only('pp_no','site_code','line_no','sa_status').aggregate(Sum('topup_amt'))
                depoamt_acc_ids = PrepaidAccount.objects.filter(pp_no=account.pp_no,
                line_no=account.line_no,sa_status__in=('DEPOSIT', 'TOPUP')).only('pp_no','site_code','line_no','sa_status').aggregate(Sum('topup_amt'))
              

                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%d-%m-%Y")
                time = str(datetime.datetime.now().time()).split(":")

                time_data = time[0]+":"+time[1]
                
                title = Title.objects.filter(product_license=site.itemsite_code).first()

                logo = ""
                if title and title.logo_pic:
                    # logo = "http://"+request.META['HTTP_HOST']+title.logo_pic.url
                    logo = str(SITE_ROOT) + str(title.logo_pic)
                    
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False,
                'header_data':{'prepaid_amount':"{:.2f}".format(float(last.pp_amt)) if last.pp_amt else "0.00",
                'used_amount':"{:.2f}".format(float(last.use_amt)) if last.use_amt else "0.00", 
                'bonus':"{:.2f}".format(float(last.pp_bonus)) if last.pp_bonus else "0.00", 
                'balance':"{:.2f}".format(float(last.remain)) if last.remain else "0.00", 
                'outstanding':"{:.2f}".format(float(last.outstanding)) if last.outstanding else "0.00", 
                'deposit_amount': "{:.2f}".format(float(depoamt_acc_ids['topup_amt__sum'])) if depoamt_acc_ids else "0.00",
                "balance_producttype" : "{:.2f}".format(float(product_type)), 
                "balance_servicetype" : "{:.2f}".format(float(service_type)),
                "balance_alltype" : "{:.2f}".format(float(all_type)),"pp_no" : last.pp_no,
                'logo':logo,'date':current_date+" "+time_data,
                'cust_name': cust_obj.cust_code +" "+ cust_obj.cust_name if cust_obj and cust_obj.cust_code and cust_obj.cust_name else '',
                'issued': fmspw.pw_userlogin,
                'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else ''}, 
                
                'data': serializer.data}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         
    
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def changeexpirydate(self, request): 
        try:  
            with transaction.atomic():
                if not request.data['prepaid_id']:
                    raise Exception('Please give prepaid id!!.') 
                
                if not request.data['expiry_date']:
                    raise Exception('Please give Expiry Date!!.') 
                    
                if str(request.data['expiry_date']) < str(date.today()):
                    raise Exception('Expiry Date should not be past days!!.') 

                if request.data['prepaid_id']:
                    pp_obj = PrepaidAccount.objects.filter(pk=request.data['prepaid_id']).first()
                    if not pp_obj:
                        raise Exception('PrepaidAccount ID does not exist!!.') 
                    if pp_obj:
                        pp_obj.exp_date = request.data['expiry_date']
                        pp_obj.save()
                        result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                        'error': False}
                        return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         


    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def terminateprepaid(self, request): 
        try:   
            
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).order_by('-pk').first()
            log_emp =  fmspw.Emp_Codeid ; logflag = False

            if not log_emp:
                raise Exception('Employee does not exist.') 

            if not 'prepaid_id' in request.data or not request.data['prepaid_id'] :
                raise Exception('Please give prepaid ID!!.') 
            
            pp_obj = PrepaidAccount.objects.filter(pk=request.data['prepaid_id']).first()
            if not pp_obj:
                raise Exception('PrepaidAccount ID does not exist!!.') 

            if not 'username' in request.data or not request.data['username'] or not 'password' in request.data or not request.data['password']:
                raise Exception('Please Enter Valid Username and Password!!.') 

            if User.objects.filter(username=request.data['username']):
                self.user = authenticate(username=request.data['username'], password=request.data['password'])
                # print(self.user,"self.user")
                if self.user:
                    
                    fmspw_c = Fmspw.objects.filter(user=self.user.id,pw_isactive=True).order_by('-pk').first()
                    if not fmspw_c:
                        raise Exception('User is inactive.') 

                   
                    log_emp = fmspw_c.Emp_Codeid
                    logflag = True
                else:
                    raise Exception('Password Wrong !') 

            else:
                raise Exception('Invalid Username.') 
           
            if logflag == True:
                last_acc_ids = PrepaidAccount.objects.filter(pp_no=pp_obj.pp_no,
                line_no=pp_obj.line_no).order_by('pk').last()
                if last_acc_ids:
                    if last_acc_ids.status == False:
                        raise Exception('Prepaid Already in terminate status.') 

                    last_acc_ids.status = False
                    last_acc_ids.save()
                    
                    AuditLog(user_loginid=fmspw_c,username=fmspw_c.pw_userlogin,
                    created_at=timezone.now(),pp_no=pp_obj.pp_no,line_no=pp_obj.line_no).save()



                result = {'status': status.HTTP_200_OK,"message":"Created Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Username not Secure,Can't Proceed!!",'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)  



class ComboViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ComboServicesSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        queryset = Combo_Services.objects.filter(Isactive=True,Site_Code__pk=site.pk).order_by('-pk')
        return queryset

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer_class =  ComboServicesSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            # print(result,"result") 
            return Response(result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
     

    def get_object(self, pk):
        try:
            return Combo_Services.objects.get(pk=pk, Isactive=True)
        except Combo_Services.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        combo = self.get_object(pk)
        serializer = ComboServicesSerializer(combo,context={'request': self.request})
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
        return Response(result, status=status.HTTP_200_OK)


class DashboardCustAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def get(self, request):
        try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            today_date = timezone.now().date()
            from_date = self.request.GET.get('from_date',None)
            if not from_date:
                raise Exception("Please Give From Date")

            to_date = self.request.GET.get('to_date',None)
            if not to_date:
                raise Exception("Please Give To Date")

            #newcustomer
            daily_custids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__date=today_date).only('site_code','cust_joindate').order_by('-pk').count()
            monthly_custids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__date__gte=from_date,
            cust_joindate__date__lte=to_date).only('site_code','cust_joindate').order_by('-pk').count()
            total_custids = Customer.objects.filter(site_code=site.itemsite_code).only('site_code').order_by('-pk').count()
            customer = {'daily_custcnt':daily_custids,'monthly_custcnt':monthly_custids,'total_cust':total_custids}
            
            daily_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,isvoid=False).only('itemsite_code','sa_date','isvoid').order_by('-pk')
            daily_satranacno = list(set([i.sa_transacno for i in daily_haudids if i.sa_transacno]))

            month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,isvoid=False).only('itemsite_code','sa_date','isvoid').order_by('-pk')
            month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))

            daily_pack_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
            
            dailyproductqty = 0;dailyserviceqty = 0 ; dailyproductdepoamt = 0.0 ; dailyservicedepoamt = 0.0 
            if daily_pack_ids:
                for pack in daily_pack_ids:
                    pack_code = pack.dt_itemno[:-4]
                    packdtl_ids = PackageDtl.objects.filter(package_code=pack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for st in packdtl_ids:
                        pospack_ids = PosPackagedeposit.objects.filter(sa_transacno=pack.sa_transacno,
                        code=st.code,package_code=st.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        itmstock = Stock.objects.filter(item_code=st.code[:-4]).first()
                        if itmstock and pospack_ids:
                            if int(itmstock.item_div) == 1:
                                posqty = pospack_ids.qty    
                                if pospack_ids.hold_qty and int(pospack_ids.hold_qty)  > 0:
                                    posqty = pospack_ids.qty - int(pospack_ids.hold_qty)

                                dailyproductqty += posqty
                                dailyproductdepoamt += pospack_ids.deposit_amt
                            elif int(itmstock.item_div) == 3:
                                dailyserviceqty += pospack_ids.qty
                                dailyservicedepoamt += pospack_ids.deposit_amt
            

            monthly_pack_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
            monthproductqty = 0;monthserviceqty = 0 ; monthproductdepoamt = 0.0 ; monthservicedepoamt = 0.0 
            if monthly_pack_ids:
                for mpack in monthly_pack_ids:
                    mpack_code = mpack.dt_itemno[:-4]
                    # print(mpack_code,"mpack_code")
                    mpackdtl_ids = PackageDtl.objects.filter(package_code=mpack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for mst in mpackdtl_ids:
                        mpospack_ids = PosPackagedeposit.objects.filter(sa_transacno=mpack.sa_transacno,
                        code=mst.code,package_code=mst.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        mitmstock = Stock.objects.filter(item_code=mst.code[:-4]).first()
                        if mitmstock and mpospack_ids:
                            if int(mitmstock.item_div) == 1:
                                mposqty = mpospack_ids.qty    
                                if mpospack_ids.hold_qty and int(mpospack_ids.hold_qty) > 0:
                                    mposqty = mpospack_ids.qty - int(mpospack_ids.hold_qty)

                                monthproductqty += mposqty
                                monthproductdepoamt += mpospack_ids.deposit_amt
                            elif int(mitmstock.item_div) == 3:
                                monthserviceqty += mpospack_ids.qty
                                monthservicedepoamt += mpospack_ids.deposit_amt
                    

            #Daily Product
            daily_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='PRODUCT').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            daily_productqty = sum([i.dt_qty for i in daily_product_ids])
            daily_productdeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_product_ids])))
            daily_product_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='TP PRODUCT').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            daily_product_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_product_ar_ids])))
            
            #monthly Product
            month_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PRODUCT').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            month_productqty = sum([i.dt_qty for i in month_product_ids])
            month_productdeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in month_product_ids])))
            month_product_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",
            record_detail_type='TP PRODUCT').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            month_product_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in month_product_ar_ids])))

            finaldailyprodepo = float(daily_productdeposit) + dailyproductdepoamt
            finalmonthprodepo = float(month_productdeposit) + monthproductdepoamt

            product_sold = {'dailyproduct_qty':daily_productqty + dailyproductqty,
            'monthlyproduct_qty':month_productqty + monthproductqty,
            'daily_product': "0.00" if finaldailyprodepo == 0 else "{:.2f}".format(finaldailyprodepo),
            'monthly_product': "0.00" if finalmonthprodepo == 0 else "{:.2f}".format(finalmonthprodepo),
            'daily_product_ar': "0.00" if daily_product_ar == 0 else daily_product_ar,
            'monthly_product_ar': "0.00" if month_product_ar == 0 else month_product_ar}

            #Daily Service
            daily_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='SERVICE').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            daily_serviceqty = sum([i.dt_qty for i in daily_service_ids])
            daily_servicedeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_service_ids])))
            daily_service_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='TP SERVICE').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            daily_service_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_service_ar_ids])))

            #monthly Service
            month_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='SERVICE').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            month_serviceqty = sum([i.dt_qty for i in month_service_ids])
            month_servicedeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in month_service_ids])))
            month_service_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",
            record_detail_type='TP SERVICE').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            month_service_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in month_service_ar_ids])))

            finaldailyserdepo = float(daily_servicedeposit) + dailyservicedepoamt
            finalmonthserdepo = float(month_servicedeposit) + monthservicedepoamt

            service_sold = {'dailyservice_qty':daily_serviceqty + dailyserviceqty,
            'monthlyservice_qty':month_serviceqty + monthserviceqty,
            'daily_service': "0.00" if finaldailyserdepo == 0 else "{:.2f}".format(finaldailyserdepo),
            'monthly_service': "0.00" if finalmonthserdepo == 0 else "{:.2f}".format(finalmonthserdepo),
            'daily_service_ar': "0.00" if daily_service_ar == 0 else daily_service_ar,
            'monthly_service_ar': "0.00" if month_service_ar == 0 else month_service_ar}
            
            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'customer': customer,'product_sold':product_sold,'service_sold':service_sold} 
            now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            total = now1.second - now.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


class DashboardVoucherAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def get(self, request):
        # try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            today_date = date.today()
            yesterday = today_date - timedelta(days = 1)

            from_date = self.request.GET.get('from_date',None)
            if not from_date:
                raise Exception("Please Give From Date")

            to_date = self.request.GET.get('to_date',None)
            if not to_date:
                raise Exception("Please Give To Date")

            #newcustomer
           
            daily_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,isvoid=False).order_by('-pk')
            daily_satranacno = list(set([i.sa_transacno for i in daily_haudids if i.sa_transacno]))

            month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,isvoid=False).order_by('-pk')
            month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))

            daily_pack_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
            
            dailyvoucherqty = 0;dailyprepaideqty = 0 ; dailyvoucherdepoamt = 0.0 ; dailyprepaiddepoamt = 0.0 
            if daily_pack_ids:
                for pack in daily_pack_ids:
                    pack_code = pack.dt_itemno[:-4]
                    packdtl_ids = PackageDtl.objects.filter(package_code=pack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for st in packdtl_ids:
                        pospack_ids = PosPackagedeposit.objects.filter(sa_transacno=pack.sa_transacno,
                        code=st.code,package_code=st.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        itmstock = Stock.objects.filter(item_code=st.code[:-4]).first()
                        if itmstock and pospack_ids:
                            if int(itmstock.item_div) == 4:
                                dailyvoucherqty += pospack_ids.qty
                                dailyvoucherdepoamt += pospack_ids.deposit_amt
                            elif int(itmstock.item_div) == 5:
                                dailyprepaideqty += pospack_ids.qty
                                dailyprepaiddepoamt += pospack_ids.deposit_amt
            

            monthly_pack_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
            monthvoucherqty = 0;monthprepaidqty = 0 ; monthvoucherdepoamt = 0.0 ; monthprepaiddepoamt = 0.0 
            if monthly_pack_ids:
                for mpack in monthly_pack_ids:
                    mpack_code = mpack.dt_itemno[:-4]
                    # print(mpack_code,"mpack_code")
                    mpackdtl_ids = PackageDtl.objects.filter(package_code=mpack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for mst in mpackdtl_ids:
                        mpospack_ids = PosPackagedeposit.objects.filter(sa_transacno=mpack.sa_transacno,
                        code=mst.code,package_code=mst.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        mitmstock = Stock.objects.filter(item_code=mst.code[:-4]).first()
                        if mitmstock and mpospack_ids:
                            if int(mitmstock.item_div) == 4:
                                monthvoucherqty +=  mpospack_ids.qty
                                monthvoucherdepoamt += mpospack_ids.deposit_amt
                            elif int(mitmstock.item_div) == 5:
                                monthprepaidqty += mpospack_ids.qty
                                monthprepaiddepoamt += mpospack_ids.deposit_amt
            

            #Daily Voucher
            daily_voucher_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk')
            daily_voucherqty = sum([i.dt_qty for i in daily_voucher_ids])
            daily_voucherdeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_voucher_ids])))

            #monthly Voucher
            month_voucher_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk')
            month_voucherqty = sum([i.dt_qty for i in month_voucher_ids])
            month_voucherdeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in month_voucher_ids])))

            finaldailyvoucherdepo = float(daily_voucherdeposit) + dailyvoucherdepoamt
            finalmonthvoucherdepo = float(month_voucherdeposit) + monthvoucherdepoamt


            voucher_sold = {'dailyvoucher_qty':daily_voucherqty + dailyvoucherqty,
            'monthlyvoucher_qty':month_voucherqty + monthvoucherqty,
            'daily_voucher': "0.00" if finaldailyvoucherdepo == 0 else "{:.2f}".format(finaldailyvoucherdepo),
            'monthly_voucher': "0.00" if finalmonthvoucherdepo == 0 else "{:.2f}".format(finalmonthvoucherdepo)}
            
            #Daily prepaid
            daily_prepaid_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk')
            daily_prepaidqty = sum([i.dt_qty for i in daily_prepaid_ids])
            daily_prepaiddeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_prepaid_ids])))
            daily_prepaid_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='TP PREPAID').order_by('-pk')
            daily_prepaid_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_prepaid_ar_ids])))

            #monthly prepaid
            month_prepaid_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk')
            month_prepaidqty = sum([i.dt_qty for i in month_prepaid_ids])
            month_prepaiddeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in month_prepaid_ids])))
            month_prepaid_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",
            record_detail_type='TP PREPAID').order_by('-pk')
            month_prepaid_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in month_prepaid_ar_ids])))

            finaldailyprepaiddepo = float(daily_prepaiddeposit) + dailyprepaiddepoamt
            finalmonthprepaiddepo = float(month_prepaiddeposit) + monthprepaiddepoamt

            prepaid_sold = {'dailyprepaid_qty':daily_prepaidqty + dailyprepaideqty,
            'monthlyprepaid_qty':month_prepaidqty + monthprepaidqty,
            'daily_prepaid': "0.00" if finaldailyprepaiddepo == 0 else "{:.2f}".format(finaldailyprepaiddepo),
            'monthly_prepaid': "0.00" if finalmonthprepaiddepo == 0 else "{:.2f}".format(finalmonthprepaiddepo),
            'daily_prepaid_ar': "0.00" if daily_prepaid_ar == 0 else daily_prepaid_ar,
            'monthly_prepaid_ar': "0.00" if month_prepaid_ar == 0 else month_prepaid_ar}
            
            #healspa docs
            
            # print(today_date,"today_date")
            # print(site.itemsite_code,"site.itemsite_code")
            

            #new customer txn rate daily
            percent_newcustser_daily = 0; percent_newcustser_monthly = 0
            cust_lst = []

            tot_no_newcustids = Customer.objects.filter(cust_joindate__date=today_date,
            site_code=site.itemsite_code).order_by('-pk').count()
            # print(tot_no_newcustids,"tot_no_newcustids")
            total_cust_ids = list(set(Customer.objects.filter(cust_joindate__date=today_date,
            site_code=site.itemsite_code).order_by('-pk').values_list('pk',flat=True).distinct()))
            # print(total_cust_ids,"total_cust_ids")
            if total_cust_ids:
                for c in total_cust_ids:
                    # print(c,"c")
                    nehaud_ids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_status='SA',
                    sa_date__date=today_date,isvoid=False,sa_transacno_type__in=['Receipt'],
                    sa_custnoid__pk=c).order_by('-pk')
                    # print(nehaud_ids,"nehaud_ids")
                    if nehaud_ids:
                        for j in nehaud_ids:
                            newcustser_cnt = PosDaud.objects.filter(sa_transacno=j.sa_transacno,dt_status="SA",
                            dt_itemnoid__item_div='3',itemsite_code=site.itemsite_code).order_by('-pk')
                            # print(newcustser_cnt,"newcustser_cnt")
                            if newcustser_cnt:
                                if c not in cust_lst:
                                    # print("iff")
                                    cust_lst.append(c)
            
            # print(cust_lst,"cust_lst")
            # print(tot_no_newcustids,"tot_no_newcustids")
            if cust_lst != [] and tot_no_newcustids >=1:
                percent_custns = (len(cust_lst) / tot_no_newcustids) * 100
                # print(percent_custns,"percent_custns")
                if percent_custns <= 100:
                    percent_newcustser_daily =  "{:.2f}".format(float(percent_custns))

            # print(percent_newcustser_daily,"percent_newcustser_daily") 
            # sa_date__date__gte=from_date,sa_date__date__lte=to_date
            #new customer txn rate monthly
            newcust_mlst = []

            tot_nom_newcustids = Customer.objects.filter(cust_joindate__date__gte=from_date,
            cust_joindate__date__lte=to_date,site_code=site.itemsite_code).order_by('-pk').count()
            # print(tot_nom_newcustids,"tot_nom_newcustids")
            totalm_cust_ids = list(set(Customer.objects.filter(cust_joindate__date__gte=from_date,
            cust_joindate__date__lte=to_date,site_code=site.itemsite_code).order_by('-pk').values_list('pk',flat=True).distinct()))
            # print(totalm_cust_ids,"totalm_cust_ids") 
            if totalm_cust_ids:
                for m in totalm_cust_ids:
                    mnehaud_ids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_status='SA',
                    sa_date__date__gte=from_date,sa_date__date__lte=to_date,
                    isvoid=False,sa_transacno_type__in=['Receipt'],
                    sa_custnoid__pk=m).order_by('-pk')
                    # print(mnehaud_ids,"mnehaud_ids")
                    if mnehaud_ids:
                        for k in mnehaud_ids:
                            mnewcustser_cnt = PosDaud.objects.filter(sa_transacno=k.sa_transacno,dt_status="SA",
                            dt_itemnoid__item_div='3',itemsite_code=site.itemsite_code).order_by('-pk')
                            # print(newcustser_cnt,"newcustser_cnt")
                            if mnewcustser_cnt:
                                if m not in newcust_mlst:
                                    # print("iff")
                                    newcust_mlst.append(m)
            
            # print(newcust_mlst,"newcust_mlst")
            if newcust_mlst != [] and tot_nom_newcustids >=1:
                percent_custmon = (len(newcust_mlst) / tot_nom_newcustids) * 100
                if percent_custmon <= 100:
                    percent_newcustser_monthly = "{:.2f}".format(float(percent_custmon))
             

            #old customer tx rate daily
            percent_custser_daily = 0; percent_custser_monthly = 0

            haud_custlst = []
            oldc_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_status='SA',
            sa_date__date=today_date,isvoid=False,sa_transacno_type__in=['Receipt'],
            ).order_by('-pk')
            # print(oldc_haudids,"oldc_haudids")
            if oldc_haudids:
                for o in oldc_haudids:
                    oldc_daudids = PosDaud.objects.filter(sa_transacno=o.sa_transacno,dt_status="SA",
                    dt_itemnoid__item_div='3',itemsite_code=site.itemsite_code).order_by('-pk')
                    # print(oldc_daudids,"oldc_daudids")
                    if oldc_daudids:
                        if o.sa_custnoid.pk not in haud_custlst:
                            haud_custlst.append(o.sa_custnoid.pk)

            if haud_custlst != []:
                cust_aghaudids = Customer.objects.filter(pk__in=haud_custlst,site_code=site.itemsite_code
                ).filter(~Q(cust_joindate__date=today_date)).order_by('-pk')
                # print(cust_aghaudids,"cust_aghaudids")
                if cust_aghaudids:
                    cust_signuphaud = cust_aghaudids.count()
                    # print(cust_signuphaud,"cust against haud")
                    tday_apptids = list(set(Appointment.objects.filter(appt_isactive=True,
                    appt_date=date.today(),itemsite_code=site.itemsite_code
                    ).order_by('-pk').values_list('cust_noid__pk',flat=True).distinct()))
                    # print(tday_apptids,"tday_apptids")
                    if tday_apptids:
                        # print("iff,tday_apptids")
                        cust_ags_apptids = Customer.objects.filter(pk__in=tday_apptids,site_code=site.itemsite_code
                        ).filter(~Q(cust_joindate__date=today_date)).order_by('-pk')
                        # print(cust_ags_apptids,"cust_ags_apptids")
                        if cust_ags_apptids:
                            custsigup_appt = cust_ags_apptids.count()
                            # print(custsigup_appt,"Cust against appt")
                            if cust_signuphaud > custsigup_appt:
                                percent_custser_daily =  100
                            else:    
                                value = (cust_signuphaud / custsigup_appt) * 100
                                percent_custser_daily =  "{:.2f}".format(float(value))
            
            # print(percent_custser_daily,"percent_custser_daily")
            # sa_date__date__gte=from_date,sa_date__date__lte=to_date

            #old customer tx rate monthly
            haud_custlst_m = []
            oldc_haudids_m = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_status='SA',
            sa_date__date__gte=from_date,sa_date__date__lte=to_date,
            isvoid=False,sa_transacno_type__in=['Receipt'],
            ).order_by('-pk')
            # print(oldc_haudids_m,"oldc_haudids_m")
            if oldc_haudids_m:
                for om in oldc_haudids_m:
                    oldc_daudids_m = PosDaud.objects.filter(sa_transacno=om.sa_transacno,dt_status="SA",
                    dt_itemnoid__item_div='3',itemsite_code=site.itemsite_code).order_by('-pk')
                    if oldc_daudids_m:
                        if om.sa_custnoid.pk not in haud_custlst_m:
                            haud_custlst_m.append(om.sa_custnoid.pk)

            if haud_custlst_m != []:
                cust_aghaudids_m = Customer.objects.filter(pk__in=haud_custlst_m,site_code=site.itemsite_code
                ).filter(~Q(cust_joindate__date=today_date)).order_by('-pk')
                # print(cust_aghaudids_m,"cust_aghaudids_m")
                if cust_aghaudids_m:
                    cust_signuphaud_m = cust_aghaudids_m.count()
                    # print(cust_signuphaud_m,"cust against haud Month")
                    tday_apptids_m = list(set(Appointment.objects.filter(appt_isactive=True,
                    appt_date__gte=from_date,appt_date__lte=to_date,itemsite_code=site.itemsite_code
                    ).order_by('-pk').values_list('cust_noid__pk',flat=True).distinct()))
                    # print(tday_apptids_m,"tday_apptids_m")
                    if tday_apptids_m:
                        # print("iff,tday_apptids_m month ")
                        cust_ags_apptids_m = Customer.objects.filter(pk__in=tday_apptids_m,site_code=site.itemsite_code
                        ).filter(~Q(cust_joindate__date=today_date)).order_by('-pk')
                        # print(cust_ags_apptids_m,"cust_ags_apptids_m")
                        if cust_ags_apptids_m:
                            custsigup_appt_m = cust_ags_apptids_m.count()
                            # print(custsigup_appt_m,"Cust against appt Month")
                            if cust_signuphaud_m > custsigup_appt_m:
                                percent_custser_monthly =  100
                            else:    
                                value_m = (cust_signuphaud_m / custsigup_appt_m) * 100
                                percent_custser_monthly =  "{:.2f}".format(float(value_m))
            
            # print(percent_custser_monthly,"percent_custser_monthly")

            percent_wakincusttddaily = 0 ;percent_wakincusttdmonth= 0

            #Customer Unit price daily
            sum_amount_d = 0 
            up_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_status='SA',
            sa_date__date=today_date,isvoid=False).order_by('-pk')
            if up_haudids:
                for up in up_haudids:
                    up_daudids = PosDaud.objects.filter(sa_transacno=up.sa_transacno,dt_status="SA",
                    record_detail_type='TD',itemsite_code=site.itemsite_code).order_by('-pk').aggregate(amount=Coalesce(Sum('dt_amt'), 0))
                    if up_daudids and up_daudids['amount'] > 0.0:
                        sum_amount_d += up_daudids['amount']

            # print(sum_amount_d,"sum_amount_d") 
            todayappt_ids = Appointment.objects.filter(appt_isactive=True,
            appt_date=date.today(),itemsite_code=site.itemsite_code
            ).filter(~Q(appt_status__in=['Cancelled','Block'])).order_by('-pk').count()
            # print(todayappt_ids,"todayappt_ids")
            if todayappt_ids:
                percent_wakincusttddaily =  "{:.2f}".format(float(sum_amount_d / todayappt_ids))
            

            # print(percent_wakincusttddaily,"percent_wakincusttddaily")

            #Customer Unit price Monthly
            sum_amount_m = 0
            mup_haudisds = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_status='SA',
            sa_date__date__gte=from_date,sa_date__date__lte=to_date,
            isvoid=False).order_by('-pk')
            if mup_haudisds:
                for upm in mup_haudisds:
                    upm_daudids = PosDaud.objects.filter(sa_transacno=upm.sa_transacno,dt_status="SA",
                    record_detail_type='TD',itemsite_code=site.itemsite_code).order_by('-pk').aggregate(amount=Coalesce(Sum('dt_amt'), 0))
                    if upm_daudids and upm_daudids['amount'] > 0.0:
                        sum_amount_m += upm_daudids['amount']
            
            # print(sum_amount_m,"sum_amount_m")
            mon_apptids = Appointment.objects.filter(appt_isactive=True,
            appt_date__gte=from_date,appt_date__lte=to_date,itemsite_code=site.itemsite_code
            ).filter(~Q(appt_status__in=['Cancelled','Block'])).order_by('-pk').count()
            # print(mon_apptids,"mon_apptids")
            if mon_apptids:
                percent_wakincusttdmonth = "{:.2f}".format(float(sum_amount_m / mon_apptids))
            
            # print(percent_wakincusttdmonth,"percent_wakincusttdmonth")    



            healspa_data = {'percent_custser_daily':percent_custser_daily,'percent_custser_monthly':percent_custser_monthly,
            'percent_newcustser_daily':percent_newcustser_daily,'percent_newcustser_monthly':percent_newcustser_monthly,
            'percent_wakincusttddaily':percent_wakincusttddaily,'percent_wakincusttdmonth':percent_wakincusttdmonth}


            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'voucher_sold':voucher_sold,'prepaid_sold':prepaid_sold,'healspa_data': healspa_data} 
            now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            total = now1.second - now.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)


class DashboardTDAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def get(self, request):
        try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            today_date = timezone.now().date()

            from_date = self.request.GET.get('from_date',None)
            if not from_date:
                raise Exception("Please Give From Date")

            to_date = self.request.GET.get('to_date',None)
            if not to_date:
                raise Exception("Please Give To Date")

            # daily_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,isvoid=False).order_by('-pk')
            # daily_satranacno = list(set([i.sa_transacno for i in daily_haudids if i.sa_transacno]))

            # month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            # sa_date__date__lte=to_date,isvoid=False).order_by('-pk')
            # month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))
            

            # #Treatment Done
            # daily_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            # sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
            # refer_lst = list(set([i.st_ref_treatmentcode for i in daily_td_ids if i.st_ref_treatmentcode]))
            # # print(refer_lst,"refer_lst")

            # daily_treatids = Treatment.objects.filter(site_code=site.itemsite_code,treatment_code__in=refer_lst,
            # status='Done').order_by('-pk')
            # # print(daily_treatids,"daily_treatids")
            # daily_tdqty = daily_treatids.count()
            # # print(daily_tdqty,"daily_tdqty")
            
            # if daily_treatids:
            #     daily_vals = daily_treatids.aggregate(Sum('unit_amount'))
            #     # print(daily_vals,"daily_vals")
            #     daily_unitamt ="{:.2f}".format(float(daily_vals['unit_amount__sum']))
            # else:
            #     daily_unitamt = "0.00"


            # monthly_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            # sa_date__date__lte=to_date,sa_transacno__in=month_satranacno,dt_status="SA",
            # record_detail_type__in=['SERVICE','TD']).order_by('-pk')
            
            # refer_lstmonth = list(set([i.st_ref_treatmentcode for i in monthly_td_ids if i.st_ref_treatmentcode]))
            # # print(refer_lst,"refer_lst")

            # month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
            # treatment_code__in=refer_lstmonth,status='Done').order_by('-pk')
            
            # monthly_tdqty = month_treatids.count()

            # if month_treatids:
            #     month_vals = month_treatids.aggregate(Sum('unit_amount'))
            #     month_unitamt ="{:.2f}".format(float(month_vals['unit_amount__sum']))
            # else:
            #     month_unitamt = "0.00"

            # treatment_done = {'daily_tdqty':daily_tdqty,'monthly_tdqty':monthly_tdqty,
            # 'daily_tdamt':daily_unitamt,'monthly_tdamt':month_unitamt}
            
            #dailly TD prepaid
            da_pre_amt = 0; da_pre_qty = 0 ;da_taud = [] ; pre_sa_transac = []

            daily_treat_ids =  Treatment.objects.filter(site_code=site.itemsite_code,
            treatment_date__date=today_date,status='Done').order_by('-pk')
            for i in daily_treat_ids:
                taud_ids = PosTaud.objects.filter(pay_group='PREPAID',sa_transacno=i.sa_transacno)
                if taud_ids:
                    for t in taud_ids:
                        if t.pay_rem1:
                            splt = t.pay_rem1.split('-')
                            pp_no = splt[0]
                            line_no = splt[1]
                            pac_ids = PrepaidAccount.objects.filter(pp_no=pp_no,line_no=line_no,
                            ).order_by('-pk').first()
                            if pac_ids:
                                if pac_ids.condition_type1 in ['Service Only','All']:
                                    if t.pay_amt > i.unit_amount:
                                        # if t.pk not in da_taud:
                                        da_pre_amt += i.unit_amount
                                        da_pre_qty += 1
                                        da_taud.append(t.pk)
                                        if i.sa_transacno not in pre_sa_transac:
                                            pre_sa_transac.append(i.sa_transacno)

                                    elif t.pay_amt <= i.unit_amount:
                                        # if t.pk not in da_taud:
                                        da_pre_amt += t.pay_amt
                                        da_pre_qty += 1
                                        da_taud.append(t.pk)
                                        if i.sa_transacno not in pre_sa_transac:
                                            pre_sa_transac.append(i.sa_transacno)

        
            #monthly TD prepaid
            mo_pre_amt = 0; mo_pre_qty = 0 ; mo_taud = [] ;
            month_treat_ids =  Treatment.objects.filter(site_code=site.itemsite_code,
            treatment_date__date__gte=from_date,treatment_date__date__lte=to_date,
            status='Done').order_by('-pk') 
            for j in month_treat_ids:
                motaud_ids = PosTaud.objects.filter(pay_group='PREPAID',sa_transacno=j.sa_transacno)
                if motaud_ids:
                    for ta in motaud_ids:
                        if ta.pay_rem1:
                            splte = ta.pay_rem1.split('-')
                            ppno = splte[0]
                            lineno = splte[1]
                            pacids = PrepaidAccount.objects.filter(pp_no=ppno,line_no=lineno,
                            ).order_by('-pk').first()
                            if pacids:
                                if pacids.condition_type1 in ['Service Only','All']:
                                    if ta.pay_amt > j.unit_amount:
                                        # if ta.pk not in mo_taud:
                                        mo_pre_amt += j.unit_amount
                                        mo_pre_qty += 1
                                        mo_taud.append(ta.pk)
                                        if j.sa_transacno not in pre_sa_transac:
                                            pre_sa_transac.append(j.sa_transacno)

                                    elif ta.pay_amt <= j.unit_amount:
                                        # if ta.pk not in mo_taud:
                                        mo_pre_amt += ta.pay_amt
                                        mo_pre_qty += 1
                                        mo_taud.append(ta.pk)
                                        if j.sa_transacno not in pre_sa_transac:
                                            pre_sa_transac.append(j.sa_transacno)
            

            # print(pre_sa_transac,"pre_sa_transac")
            #Daily single TD
            si_tre_ids = Treatment.objects.filter(site_code=site.itemsite_code,
            treatment_date__date=today_date,status='Done',treatment_no='01').exclude(sa_transacno__in=pre_sa_transac).order_by('-pk')
            daily_tdsiqty = si_tre_ids.count()
            # print(daily_tdsiqty,"daily_tdsiqty")
            
            if si_tre_ids:
                daily_sivals = si_tre_ids.aggregate(Sum('unit_amount'))
                # print(daily_sivals,"daily_sivals")
                daily_siunitamt ="{:.2f}".format(float(daily_sivals['unit_amount__sum']))
            else:
                daily_siunitamt = "0.00"

            #month single TD 

            mo_tre_ids = Treatment.objects.filter(site_code=site.itemsite_code,
            treatment_date__date__gte=from_date,treatment_date__date__lte=to_date,
            status='Done',treatment_no='01').exclude(sa_transacno__in=pre_sa_transac).order_by('-pk')
            monthly_tdsiqty = mo_tre_ids.count()
            # print(monthly_tdsiqty,"monthly_tdsiqty")
            
            if mo_tre_ids:
                month_sivals = mo_tre_ids.aggregate(Sum('unit_amount'))
                # print(daily_sivals,"daily_sivals")
                month_siunitamt ="{:.2f}".format(float(month_sivals['unit_amount__sum']))
            else:
                month_siunitamt = "0.00"  

            #Daily multi TD  
            mu_tre_ids = Treatment.objects.filter(site_code=site.itemsite_code,
            treatment_date__date=today_date,status='Done',treatment_no__gt='01').exclude(sa_transacno__in=pre_sa_transac).order_by('-pk')
            daily_tdmuqty = mu_tre_ids.count()
            # print(month_tdmuqty,"month_tdmuqty")
            
            if mu_tre_ids:
                month_muvals = mu_tre_ids.aggregate(Sum('unit_amount'))
                # print(daily_sivals,"daily_sivals")
                daily_mulunitamt ="{:.2f}".format(float(month_muvals['unit_amount__sum']))
            else:
                daily_mulunitamt = "0.00" 

            #month multi TD 

            momu_tre_ids = Treatment.objects.filter(site_code=site.itemsite_code,
            treatment_date__date__gte=from_date,treatment_date__date__lte=to_date,
            status='Done',treatment_no__gt='01').exclude(sa_transacno__in=pre_sa_transac).order_by('-pk')
            month_tdmuqty = momu_tre_ids.count()
            # print(month_tdmuqty,"month_tdmuqty")
            
            if momu_tre_ids:
                month_muvals = momu_tre_ids.aggregate(Sum('unit_amount'))
                # print(daily_sivals,"daily_sivals")
                month_mulunitamt ="{:.2f}".format(float(month_muvals['unit_amount__sum']))
            else:
                month_mulunitamt = "0.00"   

            treatment_done = {'daily_preqty':da_pre_qty,'daily_preamt': "{:.2f}".format(float(da_pre_amt)), 
            'monthly_preqty':mo_pre_qty,'montly_preamt': "{:.2f}".format(float(mo_pre_amt)),
            'daily_single_td_qty':daily_tdsiqty,'daily_singletdamt':daily_siunitamt,
            'month_single_td_qty':monthly_tdsiqty , 'month_singletdamt': month_siunitamt,
            'daily_multi_td_qty': daily_tdmuqty, 'daily_multi_tdamt': daily_mulunitamt,
            'month_multi_td_qty' : month_tdmuqty, 'month_multi_tdamt' : month_mulunitamt}      
                                        


            #Total Collection
            gt1_ids = Paytable.objects.filter(gt_group='GT1',pay_isactive=True).order_by('-pk') 
            gt1_lst = list(set([i.pay_code for i in gt1_ids if i.pay_code]))
            # print(gt1_lst,"gt1_lst")

            gt2_ids = Paytable.objects.filter(gt_group='GT2',pay_isactive=True).order_by('-pk') 
            gt2_lst = list(set([i.pay_code for i in gt2_ids if i.pay_code]))
            # print(gt2_lst,"gt2_lst")

            daily_taud_salesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            pay_type__in=gt1_lst).order_by('-pk')
            # print(daily_taud_salesids,"daily_taud_salesids")
            if daily_taud_salesids:
                daily_taud_salesvals = daily_taud_salesids.aggregate(Sum('pay_actamt'))
                # print(daily_taud_salesvals,"daily_taud_salesvals")
                daily_sales ="{:.2f}".format(float(daily_taud_salesvals['pay_actamt__sum'])) 
            else:
                daily_sales = "0.00"

            month_taud_salesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,pay_type__in=gt1_lst).order_by('-pk')
            # print(month_taud_salesids,"month_taud_salesids")
            if month_taud_salesids:
                month_taud_salesvals = month_taud_salesids.aggregate(Sum('pay_actamt'))
                # print(month_taud_salesvals,"month_taud_salesvals")
                monthly_sales ="{:.2f}".format(float(month_taud_salesvals['pay_actamt__sum'])) 
            else:
                monthly_sales = "0.00"   

            daily_taud_nsalesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            pay_type__in=gt2_lst).order_by('-pk')
            # print(daily_taud_nsalesids,"daily_taud_nsalesids")
            if daily_taud_nsalesids:
                daily_taud_nsalesvals = daily_taud_nsalesids.aggregate(Sum('pay_actamt'))
                # print(daily_taud_nsalesvals,"daily_taud_nsalesvals")
                daily_nonsales ="{:.2f}".format(float(daily_taud_nsalesvals['pay_actamt__sum']))  
            else:
                daily_nonsales = "0.00"

            month_taud_nsalesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=from_date,
            sa_date__date__lte=to_date,pay_type__in=gt2_lst).order_by('-pk')
            # print(month_taud_nsalesids,"month_taud_nsalesids")
            if month_taud_nsalesids:
                month_taud_nsalesvals = month_taud_nsalesids.aggregate(Sum('pay_actamt'))
                # print(month_taud_nsalesvals,"month_taud_nsalesvals")
                monthly_nonsales ="{:.2f}".format(float(month_taud_nsalesvals['pay_actamt__sum'])) 
            else:
                monthly_nonsales = "0.00"


            total_daily = float(daily_sales) + float(daily_nonsales)
            total_monthly = float(monthly_sales) + float(monthly_nonsales)
            total_collection = {'daily_sales':daily_sales,'monthly_sales':monthly_sales,
            'daily_nonsales':daily_nonsales,'monthly_nonsales':monthly_nonsales,
            'total_daily': "{:.2f}".format(float(total_daily)) ,
            'total_monthly':"{:.2f}".format(float(total_monthly))}

            #appointment
            daily_appt_ids = Appointment.objects.filter(appt_date=today_date,
            itemsite_code=site.itemsite_code).count()
            monthly_appt_ids = Appointment.objects.filter(appt_date__gte=from_date,appt_date__lte=to_date,
            itemsite_code=site.itemsite_code).count()
            daily_reqthe_ids = Appointment.objects.filter(appt_date=today_date,
            itemsite_code=site.itemsite_code,requesttherapist=True).count()
            monthly_reqthe_ids = Appointment.objects.filter(appt_date__gte=from_date,appt_date__lte=to_date,
            itemsite_code=site.itemsite_code,requesttherapist=True).count()
            daily_source_ids = Appointment.objects.filter(appt_date=today_date,
            itemsite_code=site.itemsite_code).exclude(Q(source_code__isnull=True) | Q(source_code__exact='')).count()
            monthly_source_ids = Appointment.objects.filter(appt_date__gte=from_date,appt_date__lte=to_date,
            itemsite_code=site.itemsite_code).exclude(Q(source_code__isnull=True) | Q(source_code__exact='')).count()

            
            appointment = {'daily_appt_cnt': daily_appt_ids, 'monthly_appt_cnt':monthly_appt_ids,
            'daily_reqthe_cnt':daily_reqthe_ids, 'monthly_reqthe_cnt': monthly_reqthe_ids,
            'daily_source_cnt':daily_source_ids,'month_source_cnt':monthly_source_ids}


            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'treatment_done':treatment_done,'total_collection':total_collection,'appointment':appointment} 
            now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            total = now1.second - now.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


#Month Top 10 / Top 20 
class DashboardTopProductAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def get(self, request):
        try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
            
            if not self.request.GET.get('select',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Top Value",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not self.request.GET.get('order_by',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Order by",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
     
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            today_date = timezone.now().date()

            month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,isvoid=False).only('itemsite_code','sa_date','isvoid').order_by('-pk')
            month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))


            monthly_pack_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
            
            retail_lst = [];service_lst = [];voucher_lst=[];prepaid_lst=[]
            if monthly_pack_ids:
                for mpack in monthly_pack_ids:
                    mpack_code = mpack.dt_itemno[:-4]
                    # print(mpack_code,"mpack_code")
                    mpackdtl_ids = PackageDtl.objects.filter(package_code=mpack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for mst in mpackdtl_ids:
                        mpospack_ids = PosPackagedeposit.objects.filter(sa_transacno=mpack.sa_transacno,
                        code=mst.code,package_code=mst.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        mitmstock = Stock.objects.filter(item_code=mst.code[:-4]).first()
                        if mitmstock and mpospack_ids:
                            if int(mitmstock.item_div) == 1:
                                if not any(d['item_code'] == mst.code for d in retail_lst):
                                    retail_lst.append({'item_code': mst.code,'item_name': mst.description, 'total_qty': mst.qty, 'total_trasc':  float("{:.2f}".format(mst.price * mst.qty))})
                                else:
                                    for r in retail_lst:
                                        if mst.code in r.values():
                                            r['total_qty'] += mst.qty
                                            r['total_trasc'] += float("{:.2f}".format(mst.price * mst.qty))

                            elif int(mitmstock.item_div) == 3:
                                if not any(d['item_code'] == mst.code for d in service_lst):
                                    service_lst.append({'item_code': mst.code,'item_name': mst.description, 'total_qty': mst.qty, 'total_trasc':  float("{:.2f}".format(mst.price * mst.qty))})
                                else:
                                    for s in service_lst:
                                        if mst.code in s.values():
                                            s['total_qty'] += mst.qty
                                            s['total_trasc'] += float("{:.2f}".format(mst.price * mst.qty))

                            elif int(mitmstock.item_div) == 4:
                                if not any(d['item_code'] == mst.code for d in voucher_lst):
                                    voucher_lst.append({'item_code': mst.code,'item_name': mst.description, 'total_qty': mst.qty, 'total_trasc':  float("{:.2f}".format(mst.price * mst.qty))})
                                else:
                                    for v in voucher_lst:
                                        if mst.code in v.values():
                                            v['total_qty'] += mst.qty
                                            v['total_trasc'] += float("{:.2f}".format(mst.price * mst.qty))

                            elif int(mitmstock.item_div) == 5:
                                if not any(d['item_code'] == mst.code for d in prepaid_lst):
                                    prepaid_lst.append({'item_code': mst.code,'item_name': mst.description, 'total_qty': mst.qty, 'total_trasc':  float("{:.2f}".format(mst.price * mst.qty))})
                                else:
                                    for p in prepaid_lst:
                                        if mst.code in p.values():
                                            p['total_qty'] += mst.qty
                                            p['total_trasc'] += float("{:.2f}".format(mst.price * mst.qty))
            
            # print(retail_lst,"retail_lst")
            month_product_ids = list(PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
            ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc'))
            # print(month_product_ids,"month_product_ids")

            fretail_lst = []
            for frp in retail_lst:
                if not any(d['item_code'] == frp['item_code'] for d in fretail_lst):
                    fretail_lst.append({'item_code': frp['item_code'],'item': frp['item_name'], 'qty': frp['total_qty'], 'amount':  frp['total_trasc']})
                else:
                    for fr in fretail_lst:
                        if frp['item_code'] in fr.values():
                            fr['qty'] += frp['total_qty']
                            fr['amount'] += frp['total_trasc']

            for rp in month_product_ids:
                if not any(d['item_code'] == rp['dt_itemno'] for d in fretail_lst):
                    fretail_lst.append({'item_code': rp['dt_itemno'],'item': rp['dt_itemnoid__item_name'], 'qty': rp['total_qty'], 'amount':  rp['total_trasc']})
                else:
                    for fre in fretail_lst:
                        if rp['dt_itemno'] in fre.values():
                            fre['qty'] += rp['total_qty']
                            fre['amount'] += float("{:.2f}".format(rp['total_trasc']))

            # print(fretail_lst,"fretail_lst")

            month_service_ids = list(PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
            ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc'))
            # print(month_service_ids,"month_service_ids")

            fservice_lst = []
            for se in service_lst:
                if not any(d['item_code'] == se['item_code'] for d in fservice_lst):
                    fservice_lst.append({'item_code': se['item_code'],'item': se['item_name'], 'qty': se['total_qty'], 'amount':  se['total_trasc']})
                else:
                    for sr in fservice_lst:
                        if se['item_code'] in sr.values():
                            sr['qty'] += se['total_qty']
                            sr['amount'] += se['total_trasc']

            for ser in month_service_ids:
                if not any(d['item_code'] == ser['dt_itemno'] for d in fservice_lst):
                    fservice_lst.append({'item_code': ser['dt_itemno'],'item': ser['dt_itemnoid__item_name'], 'qty': ser['total_qty'], 'amount':  ser['total_trasc']})
                else:
                    for si in fservice_lst:
                        if ser['dt_itemno'] in si.values():
                            si['qty'] += ser['total_qty']
                            si['amount'] += float("{:.2f}".format(ser['total_trasc']))

            # print(fservice_lst,"fservice_lst")

            month_voucher_ids = list(PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
            ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc'))
            # print(month_voucher_ids,"month_voucher_ids")

            fvoucher_lst = []
            for vo in voucher_lst:
                if not any(d['item_code'] == vo['item_code'] for d in fvoucher_lst):
                    fvoucher_lst.append({'item_code': vo['item_code'],'item': vo['item_name'], 'qty': vo['total_qty'], 'amount':  vo['total_trasc']})
                else:
                    for voc in fvoucher_lst:
                        if vo['item_code'] in voc.values():
                            voc['qty'] += vo['total_qty']
                            voc['amount'] += vo['total_trasc']

            for vc in month_voucher_ids:
                if not any(d['item_code'] == vc['dt_itemno'] for d in fvoucher_lst):
                    fvoucher_lst.append({'item_code': vc['dt_itemno'],'item': vc['dt_itemnoid__item_name'], 'qty': vc['total_qty'], 'amount':  vc['total_trasc']})
                else:
                    for vr in fvoucher_lst:
                        if vc['dt_itemno'] in vr.values():
                            vr['qty'] += vc['total_qty']
                            vr['amount'] += float("{:.2f}".format(vc['total_trasc']))

            # print(fvoucher_lst,"fservice_lst")

            month_prepaid_ids = list(PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
            ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc'))
            # print(month_prepaid_ids,"month_prepaid_ids")

            fprepaid_lst = []
            for pre in prepaid_lst:
                if not any(d['item_code'] == pre['item_code'] for d in fprepaid_lst):
                    fprepaid_lst.append({'item_code': pre['item_code'],'item': pre['item_name'], 'qty': pre['total_qty'], 'amount':  pre['total_trasc']})
                else:
                    for fpre in fprepaid_lst:
                        if pre['item_code'] in fpre.values():
                            fpre['qty'] += pre['total_qty']
                            fpre['amount'] += pre['total_trasc']

            for pe in month_prepaid_ids:
                if not any(d['item_code'] == pe['dt_itemno'] for d in fprepaid_lst):
                    fprepaid_lst.append({'item_code': pe['dt_itemno'],'item': pe['dt_itemnoid__item_name'], 'qty': pe['total_qty'], 'amount':  pe['total_trasc']})
                else:
                    for fprp in fprepaid_lst:
                        if pe['dt_itemno'] in fprp.values():
                            fprp['qty'] += pe['total_qty']
                            fprp['amount'] += float("{:.2f}".format(pe['total_trasc']))

            # print(fprepaid_lst,"fservice_lst")

            monthly_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
            record_detail_type__in=['SERVICE','TD']).order_by('-pk')
            # print(monthly_td_ids,"monthly_td_ids")
            refer_lstmonth = list(set([i.st_ref_treatmentcode for i in monthly_td_ids if i.st_ref_treatmentcode]))
            # print(refer_lstmonth,"refer_lstmonth")

            month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
            treatment_code__in=refer_lstmonth,status='Done').order_by('-pk').values('item_code',
            ).order_by('item_code').annotate(total_qty=Count('item_code'),total_unitamt=Sum('unit_amount')).order_by('-total_qty')
            # print(month_treatids,"month_treatids") 

            td_val_lst = list(month_treatids) 
            for td in td_val_lst:
                item_code = td['item_code'][:-4]
                stock_obj = Stock.objects.filter(item_code=item_code).order_by('-pk').first()
                td['item_name'] = stock_obj.item_name


            if int(self.request.GET.get('select',None)) == 10:
                if str(self.request.GET.get('order_by',None)) == "price": 
                    product_val = sorted(fretail_lst[:10], key=lambda d:d['amount'], reverse=True)
                    service_val = sorted(fservice_lst[:10], key=lambda d:d['amount'], reverse=True)
                    voucher_val = sorted(fvoucher_lst[:10], key=lambda d:d['amount'], reverse=True)
                    prepaid_val = sorted(fprepaid_lst[:10], key=lambda d:d['amount'], reverse=True)
                    

                elif str(self.request.GET.get('order_by',None)) == "qty": 
                    product_val = sorted(fretail_lst[:10], key=lambda d:d['qty'], reverse=True)
                    service_val = sorted(fservice_lst[:10], key=lambda d:d['qty'], reverse=True)
                    voucher_val = sorted(fvoucher_lst[:10], key=lambda d:d['qty'], reverse=True)
                    prepaid_val = sorted(fprepaid_lst[:10], key=lambda d:d['qty'], reverse=True)

                top10_td_lst = td_val_lst[:10]
                td_val = [{'item': i['item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_unitamt']))} for i in top10_td_lst]
      

            elif int(self.request.GET.get('select',None)) == 20:
                if str(self.request.GET.get('order_by',None)) == "price": 
                    product_val = sorted(fretail_lst[:20], key=lambda d:d['amount'], reverse=True)
                    service_val = sorted(fservice_lst[:20], key=lambda d:d['amount'], reverse=True)
                    voucher_val = sorted(fvoucher_lst[:20], key=lambda d:d['amount'], reverse=True)
                    prepaid_val = sorted(fprepaid_lst[:20], key=lambda d:d['amount'], reverse=True)

                elif str(self.request.GET.get('order_by',None)) == "qty": 
                    product_val = sorted(fretail_lst[:20], key=lambda d:d['qty'], reverse=True)
                    service_val = sorted(fservice_lst[:20], key=lambda d:d['qty'], reverse=True)
                    voucher_val = sorted(fvoucher_lst[:20], key=lambda d:d['qty'], reverse=True)
                    prepaid_val = sorted(fprepaid_lst[:20], key=lambda d:d['qty'], reverse=True)

                top20_td_lst = td_val_lst[:20]
                td_val = [{'item': i['item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_unitamt']))} for i in top20_td_lst]
          
           
            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'top_product':product_val,'top_service':service_val,'top_prepaid':prepaid_val,
            'top_voucher':voucher_val,'top_td':td_val}

           
            now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            total = now1.second - now.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

# class DashboardTopProductAPIView(APIView):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]
#     serializer_class = []

#     def get(self, request):
#         try:
#             now = timezone.now()
#             # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
            
#             if not self.request.GET.get('select',None):
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Top Value",'error': True}
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

#             if not self.request.GET.get('order_by',None):
#                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Order by",'error': True}
#                 return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
     
#             fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
#             site = fmspw.loginsite
#             today_date = timezone.now().date()

#             month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#             sa_date__year=today_date.year,isvoid=False).only('itemsite_code','sa_date','isvoid').order_by('-pk')
#             month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))
            

#             if str(self.request.GET.get('order_by',None)) == "price": 
#                 month_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
#                 ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc')
#                 # print(month_product_ids,"month_product_ids")

#                 month_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
#                 ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc')
#                 # print(month_service_ids,"month_service_ids")

#                 month_prepaid_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
#                 ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc')
#                 # print(month_prepaid_ids,"month_prepaid_ids")

#                 month_voucher_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
#                 ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc')
#                 # print(month_voucher_ids,"month_voucher_ids")

#                 monthly_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
#                 record_detail_type__in=['SERVICE','TD']).order_by('-pk')
#                 # print(monthly_td_ids,"monthly_td_ids")
#                 refer_lstmonth = list(set([i.st_ref_treatmentcode for i in monthly_td_ids if i.st_ref_treatmentcode]))
#                 # print(refer_lstmonth,"refer_lstmonth")

#                 month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
#                 treatment_code__in=refer_lstmonth,status='Done').order_by('-pk').values('item_code',
#                 ).order_by('item_code').annotate(total_qty=Count('item_code'),total_unitamt=Sum('unit_amount')).order_by('-total_unitamt')
#                 # print(month_treatids,"month_treatids") 
#                 td_val_lst = list(month_treatids) 
#                 for td in td_val_lst:
#                     item_code = td['item_code'][:-4]
#                     stock_obj = Stock.objects.filter(item_isactive=True,item_code=item_code).order_by('-pk').first()
#                     td['item_name'] = stock_obj.item_name
#                 # print(td_val_lst,"td_val_lst") 
  
#             elif str(self.request.GET.get('order_by',None)) == "qty": 
#                 month_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
#                 ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_qty')
#                 # print(month_product_ids,"month_product_ids")

#                 month_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
#                 ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_qty')
#                 # print(month_service_ids,"month_service_ids")


#                 month_prepaid_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
#                 ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_qty')
#                 # print(month_prepaid_ids,"month_prepaid_ids")

#                 month_voucher_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
#                 ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_qty')
#                 # print(month_voucher_ids,"month_voucher_ids")

#                 monthly_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
#                 sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
#                 record_detail_type__in=['SERVICE','TD']).order_by('-pk')
#                 # print(monthly_td_ids,"monthly_td_ids")
#                 refer_lstmonth = list(set([i.st_ref_treatmentcode for i in monthly_td_ids if i.st_ref_treatmentcode]))
#                 # print(refer_lstmonth,"refer_lstmonth")

#                 month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
#                 treatment_code__in=refer_lstmonth,status='Done').order_by('-pk').values('item_code',
#                 ).order_by('item_code').annotate(total_qty=Count('item_code'),total_unitamt=Sum('unit_amount')).order_by('-total_qty')
#                 # print(month_treatids,"month_treatids") 

#                 td_val_lst = list(month_treatids) 
#                 for td in td_val_lst:
#                     item_code = td['item_code'][:-4]
#                     stock_obj = Stock.objects.filter(item_isactive=True,item_code=item_code).order_by('-pk').first()
#                     td['item_name'] = stock_obj.item_name

#                 # print(td_val_lst,"td_val_lst") 
    
                
#             if int(self.request.GET.get('select',None)) == 10:
              
#                 top10_pro_lst = month_product_ids[:10]
#                 product_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top10_pro_lst])
                
#                 top10_ser_lst = month_service_ids[:10]
#                 service_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top10_ser_lst])
                
#                 top10_pre_lst = month_prepaid_ids[:10]
#                 prepaid_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top10_pre_lst])

#                 top10_vou_lst = month_voucher_ids[:10]
#                 voucher_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top10_vou_lst])
                
#                 top10_td_lst = td_val_lst[:10]
#                 td_val = list([{'item': i['item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_unitamt']))} for i in top10_td_lst])
  
            
#             elif int(self.request.GET.get('select',None)) == 20: 
                
#                 top20_pro_lst = month_product_ids[:20]
#                 product_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top20_pro_lst])
                
#                 top20_ser_lst = month_service_ids[:20]
#                 service_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top20_ser_lst])
                
#                 top20_pre_lst = month_prepaid_ids[:20]
#                 prepaid_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top20_pre_lst])
                
#                 top20_vou_lst = month_voucher_ids[:20]
#                 voucher_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top20_vou_lst])
                
#                 top20_td_lst = td_val_lst[:20]
#                 td_val = list([{'item': i['item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_unitamt']))} for i in top20_td_lst])
  
           
        
#             result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
#             'top_product':product_val,'top_service':service_val,'top_prepaid':prepaid_val,
#             'top_voucher':voucher_val,'top_td':td_val} 
#             now1 = timezone.now()
#             # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
#             total = now1.second - now.second
#             # print(total,"total")
                   
#             return Response(result,status=status.HTTP_200_OK)
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)


class DashboardChartAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def get(self, request):
        try:
            tnow = timezone.now()
            # print(str(tnow.hour) + '  ' +  str(tnow.minute) + '  ' +  str(tnow.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            today_date = timezone.now().date()
            if not self.request.GET.get('select',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Quarterly / Yearly",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            select = self.request.GET.get('select',None)  
            now = datetime.datetime(today_date.year,1,1)
            # print(now,"now")
            if select == "Yearly":
                categories = [(now + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(12)] 
                # print(categories,"categories") 
                xstep = 1

                #new Customer
                male_lst = []; female_lst = [] 
                for i in range(1, 13):
                    # print(i,"iii")
                    monthly_mcustids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=i,
                    cust_joindate__year=today_date.year,Cust_sexesid__pk=1).order_by('-pk').count()
                    # print(monthly_mcustids,"monthly_mcustids")
                    male_lst.append(monthly_mcustids)

                    monthly_fcustids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=i,
                    cust_joindate__year=today_date.year,Cust_sexesid__pk=2).order_by('-pk').count()
                    female_lst.append(monthly_fcustids)
                
                total_custids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month__gte=1,
                cust_joindate__month__lte=12,cust_joindate__year=today_date.year).order_by('-pk').count()

                newcust_data = {
                'title': { 'text': "New Customer" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': [
                            {
                                'name': "New Customer (Male)",
                                'data': male_lst,
                                'color': "#ffa31a"
                            },
                            {
                                'name': "New Customer (Female)",
                                'data': female_lst,
                                'color': "#a1cae2"
                            }
                        ],
                'outlinetext' : "Total Number of Customer",
                'outlinevalue': total_custids               
                }  


                #Product Sold Qty

                yearly_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,isvoid=False).order_by('-pk')
                # print(yearly_haudids,len(yearly_haudids),"yearly_haudids")
                yearly_satranacno = list(set([i.sa_transacno for i in yearly_haudids if i.sa_transacno]))
                # print(yearly_satranacno,len(yearly_satranacno),"yearly_satranacno")
            

                yearly_prodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk')
                # print(yearly_prodaud_ids,len(yearly_prodaud_ids),"yearly_prodaud_ids")
                pro_lst = []

                for y in yearly_prodaud_ids:
                    # print(y,y.pk,"YY")
                    brand_code = y.dt_itemnoid.item_brand
                    # print(brand_code,"brand_code")
                    brand_ids = ItemBrand.objects.filter(itm_code=brand_code,retail_product_brand=True,itm_status=True).first()
                    # print(brand_ids,"brand_ids")
                    if brand_ids:
                        # print("first iff")
                        # print(pro_lst,"pro_lst")
                        # print(any(d['code'] == brand_code for d in pro_lst),"any")
                        # print(not any(d['code'] == brand_code for d in pro_lst),"NOOT")
                        if not any(d['code'] == brand_code for d in pro_lst):
                            # print("iff")
                            r = lambda: random.randint(0,255)
                            color = '#%02X%02X%02X' % (r(),r(),r())
                            # print(color,"kkk")
                            pro_vals = {'code':brand_code,'name':brand_ids.itm_desc,'color':color}
                            # print(vals,"vals")
                            pro_lst.append(pro_vals)


                yearly_packprodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
                for yp in yearly_packprodaud_ids:
                    mpack_code = yp.dt_itemno[:-4]
                    # print(mpack_code,"mpack_code")
                    mpackdtl_ids = PackageDtl.objects.filter(package_code=mpack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for mst in mpackdtl_ids:
                        pospack_ids = PosPackagedeposit.objects.filter(sa_transacno=yp.sa_transacno,
                        code=mst.code,package_code=mst.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        itmstock = Stock.objects.filter(item_code=mst.code[:-4]).first()
                        if itmstock and pospack_ids:
                            if int(itmstock.item_div) == 1:
                                brandids = ItemBrand.objects.filter(itm_code=itmstock.item_brand,retail_product_brand=True,itm_status=True).first()
                                if brandids:
                                    brandcode = itmstock.item_brand
                                    if not any(d['code'] == brandcode for d in pro_lst):
                                        r = lambda: random.randint(0,255)
                                        color = '#%02X%02X%02X' % (r(),r(),r())
                                        pro_lst.append({'code':brandcode,'name':brandids.itm_desc,'color':color})
                               
                       
                # print(pro_lst,"pro_lst")  
                tot_proqty = 0          
                for b in pro_lst:
                    datalst = []
                    for i in range(1, 13):
                        month_bhaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,isvoid=False).order_by('-pk')
                        month_bsatranacno = list(set([i.sa_transacno for i in month_bhaudids if i.sa_transacno]))
                        
                        eachmonth_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,sa_transacno__in=month_bsatranacno,dt_status="SA",record_detail_type='PRODUCT',
                        dt_itemnoid__item_brand=b['code']).order_by('-pk')
                        # print(eachmonth_product_ids,"eachmonth_product_ids")
                        eachmonth_productqty = sum([i.dt_qty for i in eachmonth_product_ids])
                        # print(eachmonth_productqty,"eachmonth_productqty")
                        
                        eachmonth_packprodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,sa_transacno__in=month_bsatranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
                        for ep in eachmonth_packprodaud_ids:
                            epack_code = ep.dt_itemno[:-4]
                            epackdtl_ids = PackageDtl.objects.filter(package_code=epack_code,site_code=site.itemsite_code,
                            isactive=True).order_by('pk')
                            for est in epackdtl_ids:
                                pospackids = PosPackagedeposit.objects.filter(sa_transacno=ep.sa_transacno,
                                code=est.code,package_code=est.package_code,site_code=site.itemsite_code).order_by('pk').first()
                                itm_stock = Stock.objects.filter(item_code=est.code[:-4]).first()
                                if itm_stock and pospackids:
                                    if int(itm_stock.item_div) == 1 and itm_stock.item_brand == b['code']:
                                        pos_qty = pospackids.qty    
                                        if pospackids.hold_qty and int(pospackids.hold_qty)  > 0:
                                            pos_qty = pospackids.qty - int(pospackids.hold_qty)

                                        eachmonth_productqty += pos_qty   

                                       
                        tot_proqty += eachmonth_productqty
                        datalst.append(eachmonth_productqty)
                    b['data'] = datalst

                # print(pro_lst,"pro_lst After") 

                produtsold_data = {
                'title': { 'text': "Product Sold QTY" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': pro_lst ,
                'outlinetext' : "Total Product Sold QTY",
                'outlinevalue' : tot_proqty,       
                }  
                
                #Service Sales Amount
                
                yearly_servicedaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk')
                # print(yearly_servicedaud_ids,len(yearly_servicedaud_ids),"yearly_servicedaud_ids")
                service_lst = []

                for s in yearly_servicedaud_ids:
                    # print(s,s.pk,"SSS")
                    if s.dt_itemnoid:
                        dept_code = s.dt_itemnoid.item_dept
                        # print(dept_code,"dept_code")
                        dept_ids = ItemDept.objects.filter(itm_code=dept_code,is_service=True, itm_status=True).first()
                        # print(dept_ids,"dept_ids")
                        if dept_ids:
                            # print("first iff")
                            # print(service_lst,"service_lst")
                            # print(any(d['code'] == dept_code for d in service_lst),"any")
                            # print(not any(d['code'] == dept_code for d in service_lst),"NOOT")
                            if not any(d['code'] == dept_code for d in service_lst):
                                # print("iff")
                                r = lambda: random.randint(0,255)
                                color = '#%02X%02X%02X' % (r(),r(),r())
                                # print(color,"kkk")
                                service_vals = {'code':dept_code,'name':dept_ids.itm_desc,'color':color}
                                # print(vals,"vals")
                                service_lst.append(service_vals)


                for yr in yearly_packprodaud_ids:
                    mspack_code = yr.dt_itemno[:-4]
                    mspackdtl_ids = PackageDtl.objects.filter(package_code=mspack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for mser in mspackdtl_ids:
                        serpospack_ids = PosPackagedeposit.objects.filter(sa_transacno=yr.sa_transacno,
                        code=mser.code,package_code=mser.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        serstock = Stock.objects.filter(item_code=mser.code[:-4]).first()
                        if serstock and serpospack_ids:
                            if int(serstock.item_div) == 3:
                                deptids = ItemDept.objects.filter(itm_code=serstock.item_dept,is_service=True, itm_status=True).first()
                                if deptids:
                                    deptcode = serstock.item_dept
                                    if not any(d['code'] == deptcode for d in service_lst):
                                        r = lambda: random.randint(0,255)
                                        color = '#%02X%02X%02X' % (r(),r(),r())
                                        service_lst.append({'code':deptcode,'name':deptids.itm_desc,'color':color})
                               
                       
                # print(service_lst,"service_lst")  
                tot_serviceamt = 0.0          
                for e in service_lst:
                    sdatalst = []
                    for i in range(1, 13):
                        month_shaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,isvoid=False).order_by('-pk')
                        month_ssatranacno = list(set([i.sa_transacno for i in month_shaudids if i.sa_transacno]))
                        
                        eachmonth_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,sa_transacno__in=month_ssatranacno,dt_status="SA",record_detail_type='SERVICE',
                        dt_itemnoid__item_dept=e['code']).order_by('-pk')
                        # print(eachmonth_service_ids,"eachmonth_service_ids")
                        eachmonth_serviceqty = sum([i.dt_transacamt for i in eachmonth_service_ids])
                        # print(eachmonth_serviceqty,"eachmonth_serviceqty")

                        eachmonth_packser_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,sa_transacno__in=month_ssatranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
                        for es in eachmonth_packser_ids:
                            espack_code = es.dt_itemno[:-4]
                            espackdtl_ids = PackageDtl.objects.filter(package_code=espack_code,site_code=site.itemsite_code,
                            isactive=True).order_by('pk')
                            for eserv in espackdtl_ids:
                                pos_ser_packids = PosPackagedeposit.objects.filter(sa_transacno=es.sa_transacno,
                                code=eserv.code,package_code=eserv.package_code,site_code=site.itemsite_code).order_by('pk').first()
                                itm_stockser = Stock.objects.filter(item_code=eserv.code[:-4]).first()
                                if itm_stockser and pos_ser_packids:
                                    if int(itm_stockser.item_div) == 3 and itm_stockser.item_dept == e['code']:
                                        eachmonth_serviceqty += pos_ser_packids.qty   

                        tot_serviceamt += eachmonth_serviceqty
                        sdatalst.append(int(eachmonth_serviceqty))
                    e['data'] = sdatalst

                # print(service_lst,"service_lst After")     

                servicesales_data = {
                'title': { 'text': "Service Sales Amount" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': service_lst,
                'outlinetext' : "Total Service Sales Amount",
                'outlinevalue' : "{:.2f}".format(float(tot_serviceamt))         
                }  

                #Treatment Done Count

                yearly_tddaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
                # print(yearly_tddaud_ids,len(yearly_tddaud_ids),"yearly_tddaud_ids")
                td_lst = []

                for t in yearly_tddaud_ids:
                    # print(t,t.pk,"TTTT")
                    if t.dt_itemnoid:
                        tdept_code = t.dt_itemnoid.item_dept
                        # print(tdept_code,"tdept_code")
                        tdept_ids = ItemDept.objects.filter(itm_code=tdept_code,is_service=True, itm_status=True).first()
                        # print(tdept_ids,"tdept_ids")
                        if tdept_ids:
                            if t.st_ref_treatmentcode:
                                treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                                treatment_code=t.st_ref_treatmentcode,status='Done').order_by('-pk').first()
                                if treatids:
                                    # print("first iff")
                                    # print(td_lst,"td_lst")
                                    # print(any(d['code'] == tdept_code for d in td_lst),"any")
                                    # print(not any(d['code'] == tdept_code for d in td_lst),"NOOT")
                                    if not any(d['code'] == tdept_code for d in td_lst):
                                        # print("iff")
                                        r = lambda: random.randint(0,255)
                                        color = '#%02X%02X%02X' % (r(),r(),r())
                                        # print(color,"kkk")
                                        td_vals = {'code':tdept_code,'name':tdept_ids.itm_desc,'color':color}
                                        # print(vals,"vals")
                                        td_lst.append(td_vals)

                # print(td_lst,"td_lst")  
                tot_tdcount = 0          
                for l in td_lst:
                    tddatalst = []
                    for i in range(1, 13):
                        month_tdhaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,isvoid=False).order_by('-pk')
                        month_tdsatranacno = list(set([i.sa_transacno for i in month_tdhaudids if i.sa_transacno]))
                        
                        eachmonth_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,sa_transacno__in=month_tdsatranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD'],
                        dt_itemnoid__item_dept=l['code']).order_by('-pk')
                        # print(eachmonth_td_ids,"eachmonth_td_ids")
                        refer_lstmonth = list(set([i.st_ref_treatmentcode for i in eachmonth_td_ids if i.st_ref_treatmentcode]))
                        # print(refer_lst,"refer_lst")

                        month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                        treatment_code__in=refer_lstmonth,status='Done',Item_Codeid__item_dept=l['code']).order_by('-pk')
                        
                        monthly_tdqty = month_treatids.count()
                        tot_tdcount += monthly_tdqty
                        tddatalst.append(monthly_tdqty)
                    l['data'] = tddatalst

                # print(td_lst,"td_lst After")  

                treatmentdone_data = {
                'title': { 'text': "Treatment Done Count" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': td_lst ,
                'outlinetext' : "Total Number of Treatment Done Count",
                'outlinevalue' : tot_tdcount        
                }  


                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'data': [newcust_data,produtsold_data,servicesales_data,treatmentdone_data]}                    
            
            elif select == "Quarterly": 
                current_month = today_date.month
                # print(current_month,"current_month")
                # current_month = 4

                if current_month == 1:
                    range_lst = [12,1,2,3]
                    new_rangelst = [1,2,3]
                    now1 = datetime.datetime(today_date.year-1,12,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in new_rangelst] 
                    # print(categories ,"categories bbb")
                    dec_val = "Dec"+"-"+str(today_date.year-1)
                    categories.insert(0,dec_val)
                    # print(categories,"categories aa")
                elif current_month in [2,3]: 
                    range_lst = [1,2,3,4]
                    now1 = datetime.datetime(today_date.year-1,12,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 
                    # print(categories,"categories")
                elif current_month == 4: 
                    range_lst = [3,4,5,6]
                    now1 = datetime.datetime(today_date.year,3,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(4)] 
                    # print(categories,"categories") 
                elif current_month == 5:
                    range_lst = [4,5,6,7]
                    now1 = datetime.datetime(today_date.year,4,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(4)] 
                elif current_month == 6:
                    range_lst = [5,6,7,8]
                    now1 = datetime.datetime(today_date.year,5,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(4)] 
                elif current_month == 7:
                    range_lst = [6,7,8,9]
                    now1 = datetime.datetime(today_date.year,6,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(4)] 
                elif current_month == 8:
                    range_lst = [7,8,9,10]
                    now1 = datetime.datetime(today_date.year,7,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(4)] 
                elif current_month == 9:
                    range_lst = [8,9,10,11]
                    now1 = datetime.datetime(today_date.year,8,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(4)] 
                elif current_month in [10, 11, 12]:
                    range_lst = [9,10,11,12]
                    now1 = datetime.datetime(today_date.year,9,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(4)] 


                xstep = 1 
                #new Customer
                male_lst = []; female_lst = [] 
                for i in range_lst:
                    # print(i,"iii")
                    if current_month == 1:
                        year = today_date.year
                        if i == 12:
                            year = today_date.year - 1
                    else:
                        year = today_date.year        

                    monthly_mcustids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=i,
                    cust_joindate__year=year,Cust_sexesid__pk=1).order_by('-pk').count()
                    # print(monthly_mcustids,"monthly_mcustids")
                    male_lst.append(monthly_mcustids)

                    monthly_fcustids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=i,
                    cust_joindate__year=year,Cust_sexesid__pk=2).order_by('-pk').count()
                    female_lst.append(monthly_fcustids)
                
                total_custids = sum(male_lst) + sum(female_lst)

                newcust_data = {
                'title': { 'text': "New Customer" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': [
                            {
                                'name': "New Customer (Male)",
                                'data': male_lst,
                                'color': "#ffa31a"
                            },
                            {
                                'name': "New Customer (Female)",
                                'data': female_lst,
                                'color': "#a1cae2"
                            }
                        ],
                'outlinetext' : "Total Number of Customer",
                'outlinevalue' : total_custids               
                }  

                
                year_lst = [today_date.year]  

                #Product Sold Qty
                if current_month == 1:
                    start_date = datetime.datetime(today_date.year-1,12,1).date()
                    end_date = datetime.datetime(today_date.year,3,31).date()

                

                    yearly_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,isvoid=False).order_by('-pk')
                    yearly_satranacno = list(set([i.sa_transacno for i in yearly_haudids if i.sa_transacno]))

                    yearly_prodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk')
                    
                    yearly_packprodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
                    
                else:
                    yearly_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,isvoid=False).order_by('-pk')
                    # print(yearly_haudids,len(yearly_haudids),"yearly_haudids")
                    yearly_satranacno = list(set([i.sa_transacno for i in yearly_haudids if i.sa_transacno]))
                    # print(yearly_satranacno,len(yearly_satranacno),"yearly_satranacno")

                    yearly_prodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk')
                    # print(yearly_prodaud_ids,len(yearly_prodaud_ids),"yearly_prodaud_ids")

                    yearly_packprodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
                    

                    
                pro_lst = []

                for y in yearly_prodaud_ids:
                    # print(y,y.pk,"YY")
                    if y.dt_itemnoid:
                        brand_code = y.dt_itemnoid.item_brand
                        # print(brand_code,"brand_code")
                        brand_ids = ItemBrand.objects.filter(itm_code=brand_code,retail_product_brand=True,itm_status=True).first()
                        # print(brand_ids,"brand_ids")
                        if brand_ids:
                            # print("first iff")
                            # print(pro_lst,"pro_lst")
                            # print(any(d['code'] == brand_code for d in pro_lst),"any")
                            # print(not any(d['code'] == brand_code for d in pro_lst),"NOOT")
                            if not any(d['code'] == brand_code for d in pro_lst):
                                # print("iff")
                                r = lambda: random.randint(0,255)
                                color = '#%02X%02X%02X' % (r(),r(),r())
                                # print(color,"kkk")
                                pro_vals = {'code':brand_code,'name':brand_ids.itm_desc,'color':color}
                                # print(vals,"vals")
                                pro_lst.append(pro_vals)


                for yp in yearly_packprodaud_ids:
                    mpack_code = yp.dt_itemno[:-4]
                    # print(mpack_code,"mpack_code")
                    mpackdtl_ids = PackageDtl.objects.filter(package_code=mpack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for mst in mpackdtl_ids:
                        pospack_ids = PosPackagedeposit.objects.filter(sa_transacno=yp.sa_transacno,
                        code=mst.code,package_code=mst.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        itmstock = Stock.objects.filter(item_code=mst.code[:-4]).first()
                        if itmstock and pospack_ids:
                            if int(itmstock.item_div) == 1:
                                brandids = ItemBrand.objects.filter(itm_code=itmstock.item_brand,retail_product_brand=True,itm_status=True).first()
                                if brandids:
                                    brandcode = itmstock.item_brand
                                    if not any(d['code'] == brandcode for d in pro_lst):
                                        r = lambda: random.randint(0,255)
                                        color = '#%02X%02X%02X' % (r(),r(),r())
                                        pro_lst.append({'code':brandcode,'name':brandids.itm_desc,'color':color})
                             

                # print(pro_lst,"pro_lst")  
                tot_proqty = 0          
                for b in pro_lst:
                    datalst = []
                    for i in range_lst:
                        if current_month == 1:
                            year = today_date.year
                            if i == 12:
                                year = today_date.year - 1
                        else:
                            year = today_date.year  

                        month_bhaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,isvoid=False).order_by('-pk')
                        month_bsatranacno = list(set([i.sa_transacno for i in month_bhaudids if i.sa_transacno]))
                        
                        eachmonth_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,sa_transacno__in=month_bsatranacno,dt_status="SA",record_detail_type='PRODUCT',
                        dt_itemnoid__item_brand=b['code']).order_by('-pk')
                        # print(eachmonth_product_ids,"eachmonth_product_ids")
                        eachmonth_productqty = sum([i.dt_qty for i in eachmonth_product_ids])
                        # print(eachmonth_productqty,"eachmonth_productqty")

                        eachmonth_packprodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,sa_transacno__in=month_bsatranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
                        for ep in eachmonth_packprodaud_ids:
                            epack_code = ep.dt_itemno[:-4]
                            epackdtl_ids = PackageDtl.objects.filter(package_code=epack_code,site_code=site.itemsite_code,
                            isactive=True).order_by('pk')
                            for est in epackdtl_ids:
                                pospackids = PosPackagedeposit.objects.filter(sa_transacno=ep.sa_transacno,
                                code=est.code,package_code=est.package_code,site_code=site.itemsite_code).order_by('pk').first()
                                itm_stock = Stock.objects.filter(item_code=est.code[:-4]).first()
                                if itm_stock and pospackids:
                                    if int(itm_stock.item_div) == 1 and itm_stock.item_brand == b['code']:
                                        pos_qty = pospackids.qty    
                                        if pospackids.hold_qty and int(pospackids.hold_qty)  > 0:
                                            pos_qty = pospackids.qty - int(pospackids.hold_qty)

                                        eachmonth_productqty += pos_qty   

                        
                        tot_proqty += eachmonth_productqty
                        datalst.append(eachmonth_productqty)

                    b['data'] = datalst

                # print(pro_lst,"pro_lst After") 

                produtsold_data = {
                'title': { 'text': "Product Sold QTY" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': pro_lst,
                'outlinetext' : "Total Product Sold QTY",
                'outlinevalue' : tot_proqty       
                }  

                #Service Sales Amount

                if current_month == 1:
                   
                    yearly_servicedaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk')
                    # print(yearly_servicedaud_ids,len(yearly_servicedaud_ids),"yearly_servicedaud_ids")
                
                else:
                    yearly_servicedaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk')
                    # print(yearly_servicedaud_ids,len(yearly_servicedaud_ids),"yearly_servicedaud_ids")

                service_lst = []

                for s in yearly_servicedaud_ids:
                    # print(s,s.pk,"SSS")
                    if s.dt_itemnoid:
                        dept_code = s.dt_itemnoid.item_dept
                        # print(dept_code,"dept_code")
                        dept_ids = ItemDept.objects.filter(itm_code=dept_code,is_service=True, itm_status=True).first()
                        # print(dept_ids,"dept_ids")
                        if dept_ids:
                            # print("first iff")
                            # print(service_lst,"service_lst")
                            # print(any(d['code'] == dept_code for d in service_lst),"any")
                            # print(not any(d['code'] == dept_code for d in service_lst),"NOOT")
                            if not any(d['code'] == dept_code for d in service_lst):
                                # print("iff")
                                r = lambda: random.randint(0,255)
                                color = '#%02X%02X%02X' % (r(),r(),r())
                                # print(color,"kkk")
                                service_vals = {'code':dept_code,'name':dept_ids.itm_desc,'color':color}
                                # print(vals,"vals")
                                service_lst.append(service_vals)
                

                for yr in yearly_packprodaud_ids:
                    mspack_code = yr.dt_itemno[:-4]
                    mspackdtl_ids = PackageDtl.objects.filter(package_code=mspack_code,site_code=site.itemsite_code,
                    isactive=True).order_by('pk')
                    for mser in mspackdtl_ids:
                        serpospack_ids = PosPackagedeposit.objects.filter(sa_transacno=yr.sa_transacno,
                        code=mser.code,package_code=mser.package_code,site_code=site.itemsite_code).order_by('pk').first()
                        serstock = Stock.objects.filter(item_code=mser.code[:-4]).first()
                        if serstock and serpospack_ids:
                            if int(serstock.item_div) == 3:
                                deptids = ItemDept.objects.filter(itm_code=serstock.item_dept,is_service=True, itm_status=True).first()
                                if deptids:
                                    deptcode = serstock.item_dept
                                    if not any(d['code'] == deptcode for d in service_lst):
                                        r = lambda: random.randint(0,255)
                                        color = '#%02X%02X%02X' % (r(),r(),r())
                                        service_lst.append({'code':deptcode,'name':deptids.itm_desc,'color':color})
                            
                # print(service_lst,"service_lst")  
                tot_serviceamt = 0.0          
                for e in service_lst:
                    sdatalst = []
                    for i in range_lst:
                        if current_month == 1:
                            year = today_date.year
                            if i == 12:
                                year = today_date.year - 1
                        else:
                            year = today_date.year  

                        month_shaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,isvoid=False).order_by('-pk')
                        month_ssatranacno = list(set([i.sa_transacno for i in month_shaudids if i.sa_transacno]))
                        
                        eachmonth_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,sa_transacno__in=month_ssatranacno,dt_status="SA",record_detail_type='SERVICE',
                        dt_itemnoid__item_dept=e['code']).order_by('-pk')
                        # print(eachmonth_service_ids,"eachmonth_service_ids")
                        eachmonth_serviceqty = sum([i.dt_transacamt for i in eachmonth_service_ids])
                        # print(eachmonth_serviceqty,"eachmonth_serviceqty")

                        eachmonth_packser_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,sa_transacno__in=month_ssatranacno,dt_status="SA",record_detail_type='PACKAGE',isfoc=False).order_by('-pk')
                        for es in eachmonth_packser_ids:
                            espack_code = es.dt_itemno[:-4]
                            espackdtl_ids = PackageDtl.objects.filter(package_code=espack_code,site_code=site.itemsite_code,
                            isactive=True).order_by('pk')
                            for eserv in espackdtl_ids:
                                pos_ser_packids = PosPackagedeposit.objects.filter(sa_transacno=es.sa_transacno,
                                code=eserv.code,package_code=eserv.package_code,site_code=site.itemsite_code).order_by('pk').first()
                                itm_stockser = Stock.objects.filter(item_code=eserv.code[:-4]).first()
                                if itm_stockser and pos_ser_packids:
                                    if int(itm_stockser.item_div) == 3 and itm_stockser.item_dept == e['code']:
                                        eachmonth_serviceqty += pos_ser_packids.qty   

                        tot_serviceamt += eachmonth_serviceqty
                        sdatalst.append(int(eachmonth_serviceqty))
                    e['data'] = sdatalst

                # print(service_lst,"service_lst After")     

                servicesales_data = {
                'title': { 'text': "Service Sales Amount" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': service_lst,
                'outlinetext' : "Total Service Sales Amount",
                'outlinevalue' : "{:.2f}".format(float(tot_serviceamt))        
                }  

                #Treatment Done Count

                if current_month == 1:
                    yearly_tddaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
                    # print(yearly_tddaud_ids,len(yearly_tddaud_ids),"yearly_tddaud_ids")
                else:
                    yearly_tddaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
                    # print(yearly_tddaud_ids,len(yearly_tddaud_ids),"yearly_tddaud_ids")

                td_lst = []

                for t in yearly_tddaud_ids:
                    # print(t,t.pk,"TTTT")
                    if t.dt_itemnoid:
                        tdept_code = t.dt_itemnoid.item_dept
                        # print(tdept_code,"tdept_code")
                        tdept_ids = ItemDept.objects.filter(itm_code=tdept_code,is_service=True, itm_status=True).first()
                        # print(tdept_ids,"tdept_ids")
                        if tdept_ids:
                            if t.st_ref_treatmentcode:
                                treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                                treatment_code=t.st_ref_treatmentcode,status='Done').order_by('-pk').first()
                                if treatids:
                                    # print("first iff")
                                    # print(td_lst,"td_lst")
                                    # print(any(d['code'] == tdept_code for d in td_lst),"any")
                                    # print(not any(d['code'] == tdept_code for d in td_lst),"NOOT")
                                    if not any(d['code'] == tdept_code for d in td_lst):
                                        # print("iff")
                                        r = lambda: random.randint(0,255)
                                        color = '#%02X%02X%02X' % (r(),r(),r())
                                        # print(color,"kkk")
                                        td_vals = {'code':tdept_code,'name':tdept_ids.itm_desc,'color':color}
                                        # print(vals,"vals")
                                        td_lst.append(td_vals)

                # print(td_lst,"td_lst")  
                tot_tdcount = 0          
                for l in td_lst:
                    tddatalst = []
                    for i in range_lst:
                        if current_month == 1:
                            year = today_date.year
                            if i == 12:
                                year = today_date.year - 1
                        else:
                            year = today_date.year 

                        month_tdhaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,isvoid=False).order_by('-pk')
                        month_tdsatranacno = list(set([i.sa_transacno for i in month_tdhaudids if i.sa_transacno]))
                        
                        eachmonth_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,sa_transacno__in=month_tdsatranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD'],
                        dt_itemnoid__item_dept=l['code']).order_by('-pk')
                        # print(eachmonth_td_ids,"eachmonth_td_ids")
                        refer_lstmonth = list(set([i.st_ref_treatmentcode for i in eachmonth_td_ids if i.st_ref_treatmentcode]))
                        # print(refer_lst,"refer_lst")

                        month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                        treatment_code__in=refer_lstmonth,status='Done',Item_Codeid__item_dept=l['code']).order_by('-pk')
                        
                        monthly_tdqty = month_treatids.count()
                        tot_tdcount += monthly_tdqty
                        tddatalst.append(monthly_tdqty)
                    l['data'] = tddatalst

                # print(td_lst,"td_lst After")  

                treatmentdone_data = {
                'title': { 'text': "Treatment Done Count" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': td_lst,
                'outlinetext' : "Total Number of Treatment Done Count",
                'outlinevalue' : tot_tdcount        
                }  


                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'data': [newcust_data,produtsold_data,servicesales_data,treatmentdone_data]}                    


            tnow1 = timezone.now()
            # print(str(tnow1.hour) + '  ' +  str(tnow1.minute) + '  ' +  str(tnow1.second),"End hour, minute, second\n")
            total = tnow1.second - tnow.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          


     
class BillingViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = BillingSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        year = timezone.now().year
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)
        transac_no = self.request.GET.get('transac_no',None)
        cust_code = self.request.GET.get('cust_code',None)
        cust_name = self.request.GET.get('cust_name',None)
        queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('-pk')

        if not from_date and not to_date and not transac_no and not cust_code and not cust_name:
            queryset = queryset
        else:
            if from_date and to_date: 
                queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).order_by('-pk')
            if transac_no:
                queryset = queryset.filter(sa_transacno_ref__icontains=transac_no).order_by('-pk')
            if cust_code:
                queryset = queryset.filter(sa_custno__icontains=cust_code).order_by('-pk')
            if cust_name:
                queryset = queryset.filter(sa_custname__icontains=cust_name).order_by('-pk')
        return queryset
    
    def list(self, request):
        try:
            year = timezone.now().year
            queryset = self.filter_queryset(self.get_queryset()).order_by('-pk')
            # queryset = PosHaud.objects.filter(sa_date__year=year).order_by('-pk')
            serializer_class =  BillingSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


class CreditNotePayAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CreditNotePaySerializer

    def get(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code, status='OPEN',site_code=site.itemsite_code).only('cust_code','status').order_by('pk')

            if queryset:
                serializer = CreditNotePaySerializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK, "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message": "No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


class PrepaidPayViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = PrepaidPaySerializer
    queryset = PrepaidAccount.objects.filter().order_by('-id')

    def get_queryset(self,request):
        global type_ex
        type_ex.append('Sales')
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
        # print(fmspw,"fmspw")
        site = fmspw.loginsite
        cart_date = timezone.now().date()
        cust_obj = Customer.objects.filter(pk=self.request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
        cart_id = self.request.GET.get('cart_id',None)

        cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
        cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site.itemsite_code).exclude(type__in=type_ex).order_by('lineno')
        # print(cartc_ids,"cartc_ids")
        if cartc_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        cartids = ItemCart.objects.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
        cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code,
        itemcodeid__item_div__in=[1,3]).exclude(type__in=type_ex).order_by('lineno')
        if not cartids:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Given Cart ID does not exist!!", 'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        return cartids

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            cart_id = self.request.GET.get('cart_id',None)
            if not cart_id:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart_id is not given",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            cartids = self.filter_queryset(self.get_queryset(request))

            cartquery = []
            if cartids:    
                cartquery = CartPrepaidSerializer(cartids, many=True)     
            
            queryset = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,status=True).only('site_code','cust_code','status').order_by('pk')
            if queryset:
                serializer = PrepaidPaySerializer(queryset, many=True)
                data = {'pp_data':serializer.data,'cart_data': cartquery.data if cartquery else []}
                result = {'status': status.HTTP_200_OK, "message": "Listed Succesfully", 'error': False, 'data': data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message": "No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
    
    def get_object(self, pk):
        try:
            return PrepaidAccount.objects.get(pk=pk)
        except PrepaidAccount.DoesNotExist:
            raise Http404

    def partial_update(self, request, pk=None):
        try:
            global type_ex
            type_ex.append('Sales')
            pp = self.get_object(pk)  
            serializer = PrepaidPaySerializer(pp, data=request.data, partial=True)
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            cart_date = timezone.now().date()
            cust_obj = Customer.objects.filter(cust_code=pp.cust_code,cust_isactive=True).only('cust_code','cust_isactive').first()
            cart_id = self.request.GET.get('cart_id',None)
            if not cart_id:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart_id is not given",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
            cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site.itemsite_code).exclude(type__in=type_ex).order_by('lineno')
            if cartc_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            cartids = ItemCart.objects.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
            cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code,
            itemcodeid__item_div__in=[1,3]).exclude(type__in=type_ex).order_by('lineno')
            if not cartids:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Given Cart ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                
                div = list(set([c.itemcodeid.item_div for c in cartids if c.itemcodeid.item_div]))
                open_ids = PrepaidAccountCondition.objects.filter(pp_no=pp.pp_no,
                pos_daud_lineno=pp.line_no).only('pp_no','pos_daud_lineno').first()
                if open_ids:
                    if open_ids.conditiontype1 == "Product Only":
                        if '1' not in div:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Condition found for Retail Product in order list",'error': True}
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    elif open_ids.conditiontype1 == "Service Only":
                        if '3' not in div:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Condition found for Service in order list",'error': True}
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    elif open_ids.conditiontype1 == "All":
                        if '1' not in div and '3' not in div:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Condition found for Service/Retail Product in order list",'error': True}
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                            
                result = {'status': status.HTTP_200_OK,"message":"Checked Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        
                


# class DeleteAPIView(generics.CreateAPIView):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]

#     def post(self, request):
#         cart_ids = ItemCart.objects.filter(customercode='HQ100022',price=0)
#         treat_ids = Treatment.objects.filter(cust_code='HQ100022',unit_amount=0)
#         return Response(data="deleted sucessfully", status=status.HTTP_200_OK)         
    

# class ControlAPIView(generics.CreateAPIView):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]

#     def post(self, request):
#         site_ids = ItemSitelist.objects.filter().exclude(itemsite_code='HQ')
#         control_ids = ControlNo.objects.filter(site_code='HQ')
#         for s in site_ids:
#             for c in control_ids:
#                 ControlNo(control_no=c.control_no,control_prefix=c.control_prefix,
#                 control_description=c.control_description,controldate=c.controldate,
#                 Site_Codeid=s,site_code=s.itemsite_code,mac_code=c.mac_code).save()

#         return Response(data="Created Sucessfully", status=status.HTTP_200_OK)         

# @register.filter
# def get_item(dictionary, key):
#     return dictionary.get(key)           

class HolditemdetailViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Holditemdetail.objects.filter().order_by('-id')
    serializer_class = HolditemdetailSerializer

    
    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)

            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
            site = fmspw.loginsite
            queryset = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=cust_obj.cust_code,
            status='OPEN').order_by('-pk')
            satrasc_ids = list(set([e.sa_transacno for e in queryset if e.sa_transacno]))
            # print(satrasc_ids,"satrasc_ids")


            lst = [] ; final = []
            if satrasc_ids:
                for q in satrasc_ids:
                    # print(q,"sa_transacno")
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    sa_transacno=q,sa_transacno_type__in=['Receipt','Non Sales'],
                    ItemSite_Codeid__pk=site.pk).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
                    # print(pos_haud,"pos_haud")

                    if pos_haud:
                        line_ids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=cust_obj.cust_code,
                        status='OPEN',sa_transacno=q).order_by('-pk')

                        lineno_ids = list(set([e.hi_lineno for e in line_ids if e.hi_lineno]))
                        # print(lineno_ids,"lineno_ids")
 
                        if lineno_ids:
                            for l in lineno_ids:
                                # print(l,"line noo")
                                queryids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=cust_obj.cust_code,
                                status='OPEN',sa_transacno=q,hi_lineno=l
                                ).only('itemsite_code','sa_custno','status','sa_transacno','itemno','hi_lineno').order_by('pk').last()
                                # print(queryids,"queryids")
                                if queryids:
                                    depoids = DepositAccount.objects.filter(cust_code=cust_obj.cust_code,
                                    sa_status="SA",sa_transacno=q,item_barcode=queryids.itemno,dt_lineno=l).only('site_code','cust_code','sa_status').order_by('pk').last()
                                    # print(depoids,"depoids")
                                    # if depoids:
                                    laqueryids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=cust_obj.cust_code,
                                    status='OPEN',sa_transacno=q,hi_lineno=l,itemno=queryids.itemno
                                    ).only('itemsite_code','sa_custno','status','sa_transacno','itemno','hi_lineno').order_by('pk').last()
                                    # print(laqueryids,"laqueryids")
                                    if laqueryids:
                                        if laqueryids.pk not in lst:
                                            lst.append(laqueryids.pk)
                                            if laqueryids.sa_date:
                                                # print(laqueryids.sa_date,"data['sa_date']")
                                                splt = str(laqueryids.sa_date).split(" ")
                                                sa_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d/%m/%Y")

                                                check = "" 
                                                # if depoids.outstanding == 0:
                                                if not depoids or (depoids and depoids.outstanding == 0):    
                                                    check = "fullpay"
                                                elif depoids and depoids.outstanding > 0:
                                                    check = "partialpay" 


                                                valuedata = 'TRUE'

                                                sys_ids = Systemsetup.objects.filter(title='Stock Available',value_name='Stock Available').first() 
                                                if sys_ids:
                                                    valuedata = sys_ids.value_data
                                                    
                                                batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(laqueryids.itemno[:-4]),
                                                uom=laqueryids.hi_uom).order_by('pk').last() 

                                                onhand = True

                                                if valuedata == 'TRUE' and batchids:
                                                    if int(laqueryids.holditemqty) > int(batchids.qty):
                                                        onhand = False
                                                        # raise Exception('Inventory ohand qty Stock is not available') 
                                        

                                                
                                                val ={'id':laqueryids.pk,'sa_date':sa_date,'sa_transacno_ref':pos_haud.sa_transacno_ref,
                                                'hi_itemdesc':laqueryids.hi_itemdesc,'itemno':laqueryids.itemno,
                                                'holditemqty':laqueryids.holditemqty,'qty_issued':"",'staff_issued':"",'check':check,
                                                'onhand':onhand}
                                                final.append(val)

              
            # print(lst,"lst")
            if final != []:
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': final}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)  


    def get_object(self, pk):
        try:
            return Holditemdetail.objects.get(pk=pk)
        except Holditemdetail.DoesNotExist:
            raise Http404       

    def retrieve(self, request, pk=None):
        try:
            holditem = self.get_object(pk)
            serializer = HolditemSerializer(holditem)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def validate_issueqty(self, request): 
        try:
            hold_obj = Holditemdetail.objects.filter(hi_no=request.data['id']).first()
            if not hold_obj:
                raise Exception('Holditemdetail id Does not exist')

            if not request.data['issued_qty']:
                raise Exception('Please enter valid issued qty')


            depo_obj = DepositAccount.objects.filter(cust_code=hold_obj.sa_custno,type='Deposit', 
            sa_transacno=hold_obj.sa_transacno,item_barcode=hold_obj.itemno,
            dt_lineno=hold_obj.hi_lineno).order_by('pk').first() 
            
            if depo_obj:
                # print(depo_obj,depo_obj.pk,"depo_obj")
                if hold_obj.hi_amt == 0:
                    result = {'status': status.HTTP_200_OK , "message": "Validated Succesfully", 
                    'error': False}
                    return Response(result, status=status.HTTP_200_OK)

                sys_ids = Systemsetup.objects.filter(title='Holditembalancecheckforissue',
                value_name='Holditembalancecheckforissue').first() 
                if not sys_ids:
                    raise Exception('Systemsetup for Holditembalancecheckforissue not there')

                if sys_ids and sys_ids.value_data == 'True':
                    dacc_ids = DepositAccount.objects.filter(ref_transacno=depo_obj.sa_transacno,
                    ref_productcode=depo_obj.treat_code).order_by('id').order_by('sa_date','sa_time','id').last()
                    if dacc_ids and dacc_ids.balance:
                        issue_amt =  hold_obj.hi_price * int(request.data['issued_qty']) 
                        if dacc_ids.balance < issue_amt:
                            msg = "{0} issue qty cant be issue! Balance is low".format(str(request.data['issued_qty']))
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)
                        elif dacc_ids.balance >= issue_amt:
                            result = {'status': status.HTTP_200_OK,"message":"Issue Qty Validated Sucessfully",
                            'error': False}
                            return Response(result, status=status.HTTP_200_OK)  
                    elif dacc_ids and (dacc_ids.balance == 0 or dacc_ids.balance == None):
                        msg = "{0} issue qty cant be issue! Balance is Zero".format(str(request.data['issued_qty']))
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)
                elif sys_ids and sys_ids.value_data == 'False':
                    result = {'status': status.HTTP_200_OK , "message": "Validated Succesfully", 
                    'error': False}
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    raise Exception('Systemsetup for Holditembalancecheckforissue value data not correct')

            else:
                # raise Exception('DepositAccount is not there')
                result = {'status': status.HTTP_200_OK , "message": "Validated Succesfully", 
                'error': False}
                return Response(result, status=status.HTTP_200_OK)

                   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
        

    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def issued(self, request):  
        try:
            with transaction.atomic():
                if request.data:
                    fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                    site = fmspw[0].loginsite 
                    con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                    if not con_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    
                    for idx, reqt in enumerate(request.data, start=1): 
                        hold_obj = Holditemdetail.objects.filter(hi_no=reqt['id']).first()
                        if not hold_obj:
                            raise Exception('Holditemdetail id Does not exist')

                        stockobj = Stock.objects.filter(item_code=hold_obj.itemno[:-4]).first()
                        if not stockobj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock ID does not exist!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


                        # cust_obj = Customer.objects.filter(cust_code=hold_obj.sa_custno,cust_isactive=True,site_code=site.itemsite_code).first()
                        cust_obj = Customer.objects.filter(cust_code=hold_obj.sa_custno,cust_isactive=True).first()
                        if not cust_obj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                        if not reqt['issued_qty']:
                            msg = "{0} This Product issued qty should not empty".format(str(hold_obj.hi_itemdesc))
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)

                        if not reqt['emp_id']:
                            msg = "{0} This Product staff issued should not empty".format(str(hold_obj.hi_itemdesc))
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        if int(reqt['issued_qty']) <= 0:
                            msg = "{0} This Product issued qty should not be less than 0".format(str(hold_obj.hi_itemdesc))
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

        
                        if int(reqt['issued_qty']) > int(hold_obj.holditemqty) :
                            msg = "{0} This Product should not greater than Qty Hold".format(str(hold_obj.hi_itemdesc))
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)

                        empobj = Employee.objects.filter(pk=int(reqt['emp_id']),emp_isactive=True).first()
                        if not empobj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                    valuedata = 'TRUE'

                    sys_ids = Systemsetup.objects.filter(title='Stock Available',value_name='Stock Available').first() 
                    if sys_ids:
                        valuedata = sys_ids.value_data

                    
                    # print(request.data,"request.data")
                    lst = []
                    for idx, req in enumerate(request.data, start=1): 
                        # print(req,"req")

                        serializer = HolditemupdateSerializer(data=req)
                        if serializer.is_valid():
                            holdobj = Holditemdetail.objects.filter(hi_no=req['id']).first()
                            new_balance = int(holdobj.holditemqty) - int(req['issued_qty'])
                           

                            stock_obj = Stock.objects.filter(item_code=hold_obj.itemno[:-4]).first()
                            
                            batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(holdobj.itemno[:-4]),
                            uom=holdobj.hi_uom).order_by('pk').last() 

                            obatchids = ItemBatch.objects.none()

                            uom_ids = ItemUomprice.objects.filter(item_code=holdobj.itemno[:-4],item_uom2=holdobj.hi_uom
                            ,uom_unit__gt=0,isactive=True).first()
                            if uom_ids:
                                obatchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(holdobj.itemno[:-4]),
                                uom=uom_ids.item_uom).order_by('pk').last() 
                
                            
                            qtytodeduct = int(req['issued_qty'])

                            if qtytodeduct > 0:
                                stockreduce = False
                                if valuedata == 'TRUE':
                                    if (batchids and int(batchids.qty) >= int(qtytodeduct)) or (int(obatchids.qty) > int(qtytodeduct)):
                                        stockreduce = True
                                else:
                                    stockreduce = True     

                                if stockreduce == True:
                                    currenttime = timezone.now()
                                    currentdate = timezone.now().date()
                                
                                    if batchids and int(batchids.qty) >= int(qtytodeduct):
                                        deduct = batchids.qty - qtytodeduct
                                        batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                                    
                                        #Stktrn
                                       
                                        post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                        stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=holdobj.itemno,
                                        item_uom=holdobj.hi_uom).order_by('pk').last() 

                                        stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=holdobj.itemno,
                                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=holdobj.sa_transacno,trn_date=currentdate,
                                        trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                        trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                        trn_amt="{:.2f}".format(float(holdobj.hi_deposit)),trn_post=currentdate,
                                        trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                        hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                        line_no=holdobj.hi_lineno,item_uom=holdobj.hi_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                        stock_in=None,trans_package_line_no=None)
                                        stktrn_id.save()

                                    else:
                                        flag = False

                                        adcontrolobj = ControlNo.objects.filter(control_description__iexact="ADJS",
                                        site_code=fmspw[0].loginsite.itemsite_code).first()

                                        adjno = False
                                        if adcontrolobj:
                                            adjno = "W"+str(adcontrolobj.control_prefix)+str(adcontrolobj.site_code)+str(adcontrolobj.control_no)

                                        
                                        if batchids and obatchids and int(obatchids.qty) >= int(qtytodeduct):

                                            post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                            stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(holdobj.itemno[:-4])+"0000",
                                            item_uom=uom_ids.item_uom).order_by('pk').last() 


                                            stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=holdobj.itemno,
                                            store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno if adjno else holdobj.sa_transacno,trn_date=currentdate,
                                            trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=-1,trn_balqty=obatchids.qty-1,
                                            trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                            trn_amt=None,trn_post=currentdate,
                                            trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                            hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                            line_no=holdobj.hi_lineno,item_uom=uom_ids.item_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                            stock_in=None,trans_package_line_no=None)
                                            stktrn_id.save()
                                            

                                            stktrnids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=holdobj.itemno,
                                            item_uom=holdobj.hi_uom).order_by('pk').last() 


                                            stktrnid = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=holdobj.itemno,
                                            store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno,trn_date=currentdate,
                                            trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=uom_ids.uom_unit,trn_balqty=uom_ids.uom_unit,
                                            trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                            trn_amt=None,trn_post=currentdate,
                                            trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                            hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                            line_no=holdobj.hi_lineno,item_uom=holdobj.hi_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                            stock_in=None,trans_package_line_no=None)
                                            stktrnid.save()
                                        

                                            fbatch_qty = (batchids.qty + uom_ids.uom_unit) - qtytodeduct

                                            vstk = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=holdobj.itemno,
                                            store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=holdobj.sa_transacno,trn_date=currentdate,
                                            trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=fbatch_qty,
                                            trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                            trn_amt=None,trn_post=currentdate,
                                            trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                            hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                            line_no=holdobj.hi_lineno,item_uom=holdobj.hi_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                            stock_in=None,trans_package_line_no=None)
                                            vstk.save()
                                        


                                            ItemBatch.objects.filter(pk=batchids.pk).update(qty=fbatch_qty,updated_at=timezone.now())

                                            ItemBatch.objects.filter(pk=obatchids.pk).update(qty=obatchids.qty-1,updated_at=timezone.now())
                                            
                                            adcontrolobj.control_no = int(adcontrolobj.control_no) + 1
                                            adcontrolobj.save()

                                            flag = True

                                        if flag == False:
                                            if batchids:
                                                deduct = batchids.qty - qtytodeduct
                                                batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                                            else:
                                                batch_id = ItemBatch(item_code=holdobj.itemno[:-4],site_code=site.itemsite_code,
                                                batch_no="",uom=holdobj.hi_uom,qty=-qtytodeduct,exp_date=None,batch_cost=None).save()
                                                deduct = -qtytodeduct

                                            #Stktrn
                                            currenttime = timezone.now()
                                            currentdate = timezone.now().date()
                                    
                                            post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                            stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=holdobj.itemno,
                                            item_uom=holdobj.hi_uom).order_by('pk').last() 

                                            stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=holdobj.itemno,
                                            store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=holdobj.sa_transacno,trn_date=currentdate,
                                            trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                            trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                            trn_amt=None,trn_post=currentdate,
                                            trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                            hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                            line_no=holdobj.hi_lineno,item_uom=holdobj.hi_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                            stock_in=None,trans_package_line_no=None)
                                            stktrn_id.save()
                                        

                            
                            depo_obj = DepositAccount.objects.filter(cust_code=hold_obj.sa_custno,type='Deposit', 
                            sa_transacno=hold_obj.sa_transacno,item_barcode=hold_obj.itemno,
                            dt_lineno=hold_obj.hi_lineno).order_by('pk').first() 
                            if depo_obj:
                                dacc_ids = DepositAccount.objects.filter(ref_transacno=depo_obj.sa_transacno,
                                ref_productcode=depo_obj.treat_code).order_by('id').order_by('sa_date','sa_time','id').last()
                                if dacc_ids and dacc_ids.balance:
                                    issue_amt =  hold_obj.hi_price * int(req['issued_qty']) 
                                    depo_balance = dacc_ids.balance - issue_amt 
                                    dacc_ids.balance = "{:.2f}".format(depo_balance)
                                    dacc_ids.save()
                                    
                                
                            emp_obj = Employee.objects.filter(pk=int(req['emp_id']),emp_isactive=True).first()
                        
                            remainqty = int(holdobj.holditemqty) - int(req['issued_qty']) 
                            # print(remainqty,"remainqty")

                            laqueryids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=holdobj.sa_custno,
                            status='OPEN',sa_transacno=holdobj.sa_transacno,hi_lineno=holdobj.hi_lineno,itemno=holdobj.itemno
                            ).only('itemsite_code','sa_custno','status','sa_transacno','itemno','hi_lineno').order_by('pk')
                            # print(laqueryids,"laqueryids")
                            length = len(laqueryids) + 1

                        
                            product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                            

                            hold = Holditemdetail(itemsite_code=site.itemsite_code,sa_transacno=holdobj.sa_transacno,
                            transacamt=holdobj.transacamt,itemno=holdobj.itemno,
                            hi_staffno=emp_obj.emp_code,
                            hi_itemdesc=holdobj.hi_itemdesc,hi_price=holdobj.hi_price,hi_amt=holdobj.hi_amt,hi_qty=holdobj.holditemqty,
                            hi_staffname=emp_obj.display_name,
                            hi_lineno=holdobj.hi_lineno,hi_uom=holdobj.hi_uom,hold_item=True,hi_deposit=holdobj.hi_deposit,
                            holditemqty=remainqty,sa_custno=holdobj.sa_custno,
                            sa_custname=holdobj.sa_custname,history_line=length,hold_type=holdobj.hold_type,
                            product_issues_no=product_issues_no,sa_date=timezone.now().date()) 

                            if remainqty == 0:
                                oldqueryids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=holdobj.sa_custno,
                                status='OPEN',sa_transacno=holdobj.sa_transacno,hi_lineno=holdobj.hi_lineno,itemno=holdobj.itemno
                                ).only('itemsite_code','sa_custno','status','sa_transacno','itemno','hi_lineno').order_by('pk').update(status="CLOSE")
                                # print(oldqueryids,"oldqueryids")
                                
                                hold.status = "CLOSE"

                                hold.save()
                                con_obj.control_no = int(con_obj.control_no) + 1
                                con_obj.save()
                            elif remainqty > 0: 

                                hold.status = "OPEN"
                                hold.save()
                                con_obj.control_no = int(con_obj.control_no) + 1
                                con_obj.save()
                            

                            val = {'sa_transacno':holdobj.sa_transacno,'hi_itemdesc':holdobj.hi_itemdesc,
                            'balance':holdobj.holditemqty,'issued_qty':int(req['issued_qty']),
                            'new_balance':new_balance,'id': holdobj.pk,'product_issues_no':holdobj.product_issues_no,
                            'created_hold': hold.pk,'new_staff': emp_obj.display_name}
                            lst.append(val)
                        else:
                            raise Exception(serializer.errors)
                            # result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
                            # return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                    
                    if lst != []:
                        # print(lst[0])
                        value = lst[0]['created_hold']
                        # print(lst,"lst")
                        # print(lst[0]['new_staff'])
                        title = Title.objects.filter(product_license=site.itemsite_code).first()
                        # holdids = Holditemdetail.objects.filter(pk__in=lst)
                        hold_ids = Holditemdetail.objects.filter(pk=value).order_by('-pk').first()

                        path = None
                        if title and title.logo_pic:
                            path = BASE_DIR + title.logo_pic.url

                        split = str(hold_ids.sa_date).split(" ")
                        date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime("%d/%m/%Y")
                        esplit = str(hold_ids.sa_time).split(" ")
                        Time = str(esplit[1]).split(":")

                        time = Time[0]+":"+Time[1]

               
                        data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
                        'address': title.trans_h2 if title and title.trans_h2 else '', 
                        'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
                        'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
                        'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
                        'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
                        'hold_ids': hold_ids, 'date':date,'time':time,
                        'hold': lst,'cust':cust_obj,'staff':lst[0]['new_staff'],'fmspw':fmspw,
                        'path':path if path else '','title':title if title else None,
                        }

                        template = get_template('hold_item.html')
                        display = Display(visible=0, size=(800, 600))
                        display.start()
                        html = template.render(data)
                        options = {
                            'margin-top': '.25in',
                            'margin-right': '.25in',
                            'margin-bottom': '.25in',
                            'margin-left': '.25in',
                            'encoding': "UTF-8",
                            'no-outline': None,
                            
                        }

                        dst ="holditem_" + str(str(hold_ids.sa_transacno)) + ".pdf"

    
                        p=pdfkit.from_string(html,False,options=options)
                        PREVIEW_PATH = dst
                        pdf = FPDF() 

                        pdf.add_page() 
                        
                        pdf.set_font("Arial", size = 15) 
                        file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                        pdf.output(file_path) 

                        if p:
                            file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                            report = os.path.isfile(file_path)
                            if report:
                                file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                                with open(file_path, 'wb') as fh:
                                    fh.write(p)
                                display.stop()

                                # ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/holditem_"+str(hold_ids.sa_transacno)+".pdf"
                                ip_link = str(SITE_ROOT)+"pdf/holditem_"+str(hold_ids.sa_transacno)+".pdf"


                                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                                'error': False,'data': ip_link}
                                return Response(result, status=status.HTTP_200_OK)         
                else:
                    raise Exception('Request body data does not exist') 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)  
          
                

class TreatmentHistoryAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Treatment.objects.filter().order_by('id')
    serializer_class = TreatmentHistorySerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            # check = False
            system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()

            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Treatment Usage',
            value_name='Other Outlet Customer Treatment Usage',isactive=True).first()

            # if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
            #     if cust_obj.site_code != site.itemsite_code or cust_obj.site_code == site.itemsite_code:
            #         check = True
            # else:
            #     if cust_obj.site_code == site.itemsite_code:
            #         check = True    
            
            # queryset = Treatment.objects.none()

            # if check == True:
            #queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code).filter(~Q(status="Open")).order_by('-pk')
            queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code).filter(~Q(status__in=["Open","Cancel"])).order_by('-pk')
            # print(queryset,"queryset") 
            if request.GET.get('year',None):
                year = request.GET.get('year',None)
                if year != "All":
                    #queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code,
                    #treatment_date__year=year).filter(~Q(status="Open")).order_by('-pk') 
                    queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code,
                    treatment_date__year=year).filter(~Q(status__in=["Open","Cancel"])).order_by('-pk') 

            # serializer_class = TreatmentHistorySerializer
            final = []
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                # total = len(queryset)
                # state = status.HTTP_200_OK
                # message = "Listed Succesfully"
                # error = False
                # data = None
                # result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action='list')

                # v = result.get('data')
                # d = v.get('dataList')
                d = serializer.data
                for dat in d:
                    i = dict(dat)
                    # print(i,"ii")
                    trmt_obj = Treatment.objects.filter(pk=i['id']).first()
                    splt = str(trmt_obj.treatment_date).split(' ')
                    

                    helper_ids = ItemHelper.objects.filter(item_code=trmt_obj.treatment_code,sa_transacno=trmt_obj.sa_transacno,
                    ).order_by('-pk','-sa_date').first()
                    if helper_ids:
    
                      
                        pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                        sa_transacno=helper_ids.helper_transacno).first()

                        pos_daud = PosDaud.objects.filter(sa_transacno=helper_ids.helper_transacno,
                        dt_lineno=helper_ids.line_no).first()


                    
                        if pos_haud and pos_daud: 
                            splt_sa = str(pos_haud.sa_date).split(' ')
                            dtime = str(pos_daud.sa_time).split(" ")
                            time = dtime[1].split(":")

                            time_data = time[0]+":"+time[1]

                            i['purchase_date'] = datetime.datetime.strptime(str(splt_sa[0]), "%Y-%m-%d").strftime("%d/%m/%Y")
                            i['trasac_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d/%m/%Y")+" "+str(time_data)
                            # pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                            i['transac'] = pos_haud.sa_transacno if pos_haud.sa_transacno else ""
                            i['link_code'] = ""
                            i['record_status'] = i['record_status'] if i['record_status'] else ""
                            i['remarks'] = i['remarks'] if i['remarks'] else ""
                            i['cust_remark'] = cust_obj.cust_remark if cust_obj.cust_remark else ""
                            i['is_allow']  = False
                            if trmt_obj:
                                if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                                    if trmt_obj.site_code != site.itemsite_code or trmt_obj.site_code == site.itemsite_code:
                                        i['is_allow'] = True
                                else:
                                    if trmt_obj.site_code == site.itemsite_code:
                                        i['is_allow'] = True

                            final.append(i)

              
            if final != []:
                limit = request.GET.get('limit',12)
                page= request.GET.get('page',1)
                paginator = Paginator(final, limit)
                total = len(final)

                total_page = 1

                if len(final) > int(limit):
                    total_page = math.ceil(len(final)/int(limit))

                if int(page) > total_page:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Content",'error': False, 
                    'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                    "total_pages":total_page}}, 
                    'dataList': []}}


                try:
                    queryset_data = paginator.page(page)
                except PageNotAnInteger:
                    queryset_data = paginator.page(1)
                    page= 1 
                except EmptyPage:
                    queryset_data = paginator.page(paginator.num_pages)    

                data_final = queryset_data.object_list

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                "total_pages":total_page}}, 'dataList': data_final},
                'cust_name': cust_obj.cust_name if cust_obj.cust_name else "",
                'cust_refer' : cust_obj.cust_refer if cust_obj.cust_refer else ""}
            
                return Response(result, status=status.HTTP_200_OK) 
            else:
                result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 'data': []}
                result['cust'] = {'cust_name': cust_obj.cust_name if cust_obj.cust_name else "",
                'cust_refer' : cust_obj.cust_refer if cust_obj.cust_refer else ""}
                return Response(result, status=status.HTTP_200_OK)    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        


class StockUsageViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Treatment.objects.filter().order_by('-id')
    serializer_class = StockUsageSerializer

    def get_object(self, pk):
        try:
            return Treatment.objects.get(pk=pk)
        except Treatment.DoesNotExist:
            raise Exception('Record does not exist') 

    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            treat = self.get_object(pk)
            # treat_obj = Treatment.objects.filter(pk=treat.pk,site_code=site.itemsite_code).first()
            treat_obj = Treatment.objects.filter(pk=treat.pk).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            cust_obj = Customer.objects.filter(cust_code=treat_obj.cust_code,
            cust_isactive=True).order_by('-pk').first()  

            if not cust_obj:
                result = {'status': status.HTTP_200_OK,"message":"Customer Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            serializer = StockUsageSerializer(treat)
            newdict = {"remarks": treat.remarks if treat.remarks else ""}
            newdict.update(serializer.data)

            # accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            # treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
            # type="Sales").order_by('id').first()
            
            # accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            # treatment_parentcode=treat_obj.treatment_parentcode,ref_no=treat_obj.treatment_code,
            # type="Sales").order_by('id').first()

            accids = ItemHelper.objects.filter(item_code=treat_obj.treatment_code,
            times=treat_obj.times).order_by('id').first()

            if not accids:
                result = {'status': status.HTTP_200_OK,"message":"Treatment Account is not there!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            # usageids = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
            # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno,isactive=True).order_by('pk')

            usageids = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
            sa_transacno=accids.helper_transacno,isactive=True).order_by('pk')


            uselst = [{'id': u.pk,'no':i,'item_code': u.item_code[:-4],'item_desc': u.item_desc, 'qty': int(u.qty), 'uom': u.uom, 'optional': "", 'auto_table': False} for i,u in enumerate(usageids,start=1)]
            
            for u in uselst:
                u['link_code'] = ""
                code = u['item_code']+"0000"
                linkobj = ItemLink.objects.filter(item_code=code,link_type='L',itm_isactive=True).order_by('pk')
                if linkobj:
                    u['link_code'] = linkobj[0].link_code
                
            usagelevel_ids = Usagelevel.objects.filter(service_code=treat_obj.service_itembarcode,
            isactive=True).order_by('-pk') 

            if usagelevel_ids:
                if uselst != []:
                    newdict['usage'] = uselst
                else:
                    itemlst = [{'no':i,'item_code': u.item_code[:-4],'item_desc': u.item_desc, 'qty': int(u.qty), 'uom': u.uom, 'optional': u.optional, 'auto_table': True} for i,u in enumerate(usagelevel_ids,start=1)]
                    for i in itemlst:
                        stockobj = Stock.objects.filter(item_code=i['item_code']).first()
                        i['stock_id'] = stockobj.pk if stockobj else 0
                        i['link_code'] = ""
                        code = i['item_code']+"0000"
                        link_obj = ItemLink.objects.filter(item_code=code,link_type='L',itm_isactive=True).order_by('pk')
                        if link_obj:
                            i['link_code'] = link_obj[0].link_code
                        
                    newdict['usage'] = itemlst

                newdict['auto'] = "True"    
            else:
                newdict['usage'] = uselst
                newdict['auto'] = "False"    

            # helper_ids = ItemHelper.objects.filter(item_code=treat_obj.treatment_code,
            # sa_transacno=treat_obj.sa_transacno,site_code=site.itemsite_code).order_by('-pk')
            helper_ids = ItemHelper.objects.filter(item_code=treat_obj.treatment_code,
            sa_transacno=treat_obj.sa_transacno).order_by('-pk')
            

            staffs = [{'no':idx, 'staff_code': h.helper_code, 'helper_name': h.helper_name} for idx, h in enumerate(helper_ids, start=1)]
            
            newdict['staffs'] = staffs
            newdict['cust'] =  {'cust_name': cust_obj.cust_name if cust_obj.cust_name else "",
            'cust_refer' : cust_obj.cust_refer if cust_obj.cust_refer else ""}

            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
            'data':  newdict,'duration':treat_obj.duration if treat_obj.duration else None}
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 

    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite

            # treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
            treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None)).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            
            # accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            # treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
            # type="Sales").order_by('id').first()

            # accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            # treatment_parentcode=treat_obj.treatment_parentcode,ref_no=treat_obj.treatment_code,
            # type="Sales").order_by('id').first()

            accids = ItemHelper.objects.filter(item_code=treat_obj.treatment_code,times=treat_obj.times).order_by('id').first()


            if not accids:
                result = {'status': status.HTTP_200_OK,"message":"Treatment Account is not there!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            now = datetime.datetime.now()
            s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))

            for idx, req in enumerate(request.data, start=1):
                # print(req,"req 4444")
                serializer = TreatmentUsageSerializer(data=req)
                if serializer.is_valid():
                    stock_obj = Stock.objects.filter(pk=req['stock_id']).first()
                   
                    # useids = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                    # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno).order_by('line_no') 

                    useids = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                    sa_transacno=accids.helper_transacno).order_by('line_no') 


                    if not useids:
                        lineno = 1
                    else:
                        rec = useids.last()
                        lineno = float(rec.line_no) + 1  

                    use = serializer.save(treatment_code=treat_obj.treatment_code,
                    item_code=req['item_code']+"0000",item_desc=stock_obj.item_desc,
                    site_code=site.itemsite_code,usage_status="Usage",line_no=lineno,
                    usage_update=s1,
                    sa_transacno=accids.helper_transacno if accids and accids.helper_transacno else "")
                    
                    # Inventory Control
                   
                    if req['qty'] > 0:
                        batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=req['item_code'],
                        uom=req['uom']).order_by('pk').last() 
                        #ItemBatch
                        if batchids:
                            deduct = batchids.qty - int(req['qty'])
                            batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                        else:
                            batch_id = ItemBatch(item_code=req['item_code'],site_code=site.itemsite_code,
                            batch_no="",uom=req['uom'],qty=-req['qty'],exp_date=None,batch_cost=stock_obj.lstpo_ucst).save()
                            deduct = -req['qty']

                        #Stktrn
                        currenttime = timezone.now()
                        currentdate = timezone.now().date()
                   
                        post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                        stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(req['item_code'])+"0000",
                        item_uom=req['uom']).order_by('pk').last() 

                        stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(req['item_code'])+"0000",
                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=treat_obj.treatment_code,trn_date=currentdate,
                        trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-req['qty'],trn_balqty=deduct,
                        trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                        trn_amt=None,trn_post=currentdate,
                        trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                        hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                        line_no=lineno,item_uom=req['uom'],item_batch=None,mov_type=None,item_batch_cost=None,
                        stock_in=None,trans_package_line_no=None).save()

                else:
                    data = serializer.errors
                    # print(data,"data")
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            if request.GET.get('treat_remarks',None):
                treat_obj.remarks = request.GET.get('treat_remarks',None)
                treat_obj.save()

            result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",'error': False}
            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 
    
    def get_object_usage(self, pk):
        try:
            return TreatmentUsage.objects.get(pk=pk)
        except TreatmentUsage.DoesNotExist:
            raise Exception('Record does not exist') 

    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            # treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
            treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None)).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            
            # accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            # treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
            # type="Sales").order_by('id').first()

            # accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            # treatment_parentcode=treat_obj.treatment_parentcode,ref_no=treat_obj.treatment_code,
            # type="Sales").order_by('id').first()

            accids = ItemHelper.objects.filter(item_code=treat_obj.treatment_code,times=treat_obj.times).order_by('id').first()
            
            if not accids:
                result = {'status': status.HTTP_200_OK,"message":"Treatment Account is not there!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            instance = self.get_object_usage(pk)
            # print(instance,"instance")
            if instance:
                now = datetime.datetime.now()
                s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))
  
                instance.isactive = False
                instance.usage_update = s1
                instance.save()
                # useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                # site_code=site.itemsite_code,sa_transacno=accids.sa_transacno).order_by('line_no') 
                useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                sa_transacno=accids.helper_transacno).order_by('line_no') 


                rec = useids.last()
                lineno = float(rec.line_no) + 1    

            
                TreatmentUsage(treatment_code=instance.treatment_code,item_code=instance.item_code,
                item_desc=instance.item_desc,qty=-instance.qty,uom=instance.uom,site_code=instance.site_code,
                usage_status="Void Usage",line_no=lineno,void_line_ref=1,usage_update=s1,
                sa_transacno=instance.sa_transacno,isactive=False).save()
                
                #ItemBatch
                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                item_code=instance.item_code[:-4],uom=instance.uom).order_by('pk').last()
                
                if batch_ids:
                    addamt = batch_ids.qty + instance.qty
                    batch_ids.qty = addamt
                    batch_ids.updated_at = timezone.now()
                    batch_ids.save()

                    #Stktrn
                
                    currenttime = timezone.now()
                    currentdate = timezone.now().date()

                    post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                    
                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                    itemcode=instance.item_code,store_no=site.itemsite_code,
                    tstore_no=None,fstore_no=None,trn_docno=instance.treatment_code,
                    trn_type="Void Usage",trn_db_qty=None,trn_cr_qty=None,
                    trn_qty=instance.qty,trn_balqty=addamt,trn_balcst=None,
                    trn_amt=None,trn_cost=None,trn_ref=None,
                    hq_update=0,line_no=instance.line_no,item_uom=instance.uom,
                    item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None,trn_post=currentdate,
                    trn_date=currentdate).save()
                
                
                result = {'status': status.HTTP_200_OK,"message":"Deleted Succesfully",'error': False}
                return Response(result,status=status.HTTP_200_OK)     
            else:
                result = {'status': status.HTTP_200_OK,"message":"No Content",'error': True}
                return Response(result,status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        

            

class StockUsageProductAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockUsageProductSerializer

    def list(self, request):
        try:
            queryset = Stock.objects.filter(item_isactive=True, item_div="2").order_by('pk')
            if request.GET.get('is_retail',None) and int(request.GET.get('is_retail',None)) == 1:
                queryset = Stock.objects.filter(item_isactive=True, item_div="1").order_by('pk')
            elif request.GET.get('is_retail',None) and int(request.GET.get('is_retail',None)) == 2:
                queryset = Stock.objects.filter(item_isactive=True).filter(Q(item_div="1") | Q(item_div="2")).order_by('pk')
        
            if request.GET.get('search',None):
                if not request.GET.get('search',None) is None:
                    queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)
                    ) | Q(item_desc__icontains=request.GET.get('search',None)) | Q(item_code__icontains=request.GET.get('search',None)))

            serializer_class =  StockUsageProductSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action='list')
            v = result.get('data')
            d = v.get("dataList")
            lst = []
            for dat in d:
                q = dict(dat)
               
                q['link_code'] = ""
                code = q['item_code']+"0000"
                linkobj = ItemLink.objects.filter(item_code=code,link_type='L',itm_isactive=True).order_by('pk')
                if linkobj:
                   q['link_code'] = linkobj[0].link_code

                uomlst = []
                stock = Stock.objects.filter(item_isactive=True, pk=q['id']).first()
                itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code).order_by('id')
                
                for i in itemuomprice:
                    itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=i.item_uom).order_by('id').first()
                    itemuom_id = None; itemuom_desc = None
                    if itemuom:
                        itemuom_id = int(itemuom.id)
                        itemuom_desc = itemuom.uom_desc
                        uom = {
                                "itemuomprice_id": int(i.id),
                                "item_uom": i.item_uom,
                                "uom_desc": i.uom_desc,
                                "item_price": "{:.2f}".format(float(i.item_price)),
                                "itemuom_id": itemuom_id, 
                                "itemuom_desc" : itemuom_desc}
                        uomlst.append(uom)

                val = {'uomprice': uomlst}  
                q.update(val) 
                if uomlst != []:
                    lst.append(q)
                v['dataList'] = lst    
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         

class StockUsageMemoViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = UsageMemo.objects.filter().order_by('-id')
    serializer_class = StockUsageMemoSerializer

    def list(self, request):
        try:
            serializer_class = StockUsageMemoSerializer
            if not request.GET.get('date'):
                result = {'status': status.HTTP_200_OK,"message":"Please give Date!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            queryset = UsageMemo.objects.filter(date_out__date=request.GET.get('date'),qty__gt=0).order_by('-pk')
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            
            v = result.get('data')
            d = v.get("dataList")
            for dat in d:
                # print(dat['date_out'],"dat['date_out']")
                splt_sa = str(dat['date_out']).split('T')
                dat["date_out"] = datetime.datetime.strptime(str(splt_sa[0]), "%Y-%m-%d").strftime("%d/%m/%Y")
                
            return Response(result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)            
    

    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            control_obj = ControlNo.objects.filter(control_description__iexact="STOCK USAGE MEMO",site_code=site.itemsite_code).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"STOCK USAGE MEMO Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            memo_no = str(control_obj.site_code)+str(control_obj.control_no)
            if not request.data['stock_id']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Stock Id!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            if not request.data['emp_id']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Emp Id!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
    

            stock_obj = Stock.objects.filter(pk=request.data['stock_id']).first()
            if not stock_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock id Does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            emp_obj = Employee.objects.filter(pk=request.data['emp_id'],emp_isactive=True).first()
            if not emp_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee id Does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            time = datetime.datetime.now().time()
            date = datetime.datetime.strptime(str(request.data['date']), "%Y-%m-%d")
            datetime_new = datetime.datetime.combine(date, time)
    
            serializer = StockUsageMemoSerializer(data=request.data)
            if serializer.is_valid():

                k = serializer.save(date_out=datetime_new,memo_no=memo_no,item_code=stock_obj.item_code+"0000",item_name=stock_obj.item_name,
                staff_code=emp_obj.emp_code,staff_name=emp_obj.display_name,staff_barcode=emp_obj.emp_code,
                date_return=None,time_return=None,created_by=fmspw.pw_userlogin,status="OUT",site_code=site.itemsite_code)
                
                if k.pk:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()

                if request.data['qty'] > 0:
                    qtytodeduct = int(request.data['qty'])
                    valuedata = 'TRUE'

                    sys_ids = Systemsetup.objects.filter(title='Stock Available',value_name='Stock Available').first() 
                    if sys_ids:
                        valuedata = sys_ids.value_data

                    batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=stock_obj.item_code,
                    uom=request.data['uom']).order_by('pk').last() 

                    obatchids = ItemBatch.objects.none()

                    uom_ids = ItemUomprice.objects.filter(item_code=stock_obj.item_code,item_uom2=request.data['uom']
                    ,uom_unit__gt=0,isactive=True).first()
                    if uom_ids:
                        obatchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(stock_obj.item_code),
                        uom=uom_ids.item_uom).order_by('pk').last() 
                        # print(uom_ids.item_uom,"uom_ids.item_uom")


                    stockreduce = False
                    if valuedata == 'TRUE':
                        if (batchids and int(batchids.qty) >= int(qtytodeduct)) or (obatchids and int(obatchids.qty) >= int(qtytodeduct)):
                            stockreduce = True
                    else:
                        stockreduce = True     

                    if stockreduce == True: 
                        currenttime = timezone.now()
                        currentdate = timezone.now().date()
                        
                        if batchids and int(batchids.qty) >= int(qtytodeduct):   
                            #ItemBatch
                            if batchids:
                                deduct = batchids.qty - int(request.data['qty'])
                                batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                            else:
                                batch_id = ItemBatch(item_code=stock_obj.item_code,site_code=site.itemsite_code,
                                batch_no=None,uom=request.data['uom'],qty=-request.data['qty'],exp_date=None,batch_cost=stock_obj.lstpo_ucst).save()
                                deduct = -request.data['qty']


                            #Stktrn
                           
                            post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                            stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(stock_obj.item_code)+"0000",
                            item_uom=request.data['uom']).order_by('pk').last() 

                            itemuom_ids = ItemUomprice.objects.filter(item_code=stock_obj.item_code,item_uom=request.data['uom'],isactive=True).order_by('pk').first()

                            stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(stock_obj.item_code)+"0000",
                            store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=memo_no,
                            trn_type="SUM",trn_db_qty=None,trn_cr_qty=None,trn_qty=-request.data['qty'],trn_balqty=deduct,
                            trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                            trn_amt=itemuom_ids.item_price if itemuom_ids and itemuom_ids.item_price else None,
                            trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                            hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                            line_no=1,item_uom=request.data['uom'],item_batch=None,mov_type=None,item_batch_cost=None,
                            stock_in=None,trans_package_line_no=None,trn_post=currentdate,
                            trn_date=currentdate).save()

                        else:
                            flag = False

                            adcontrolobj = ControlNo.objects.filter(control_description__iexact="ADJS",
                            site_code=fmspw.loginsite.itemsite_code).first()

                            adjno = False
                            if adcontrolobj:
                                adjno = "W"+str(adcontrolobj.control_prefix)+str(adcontrolobj.site_code)+str(adcontrolobj.control_no)



                            if batchids and obatchids and int(obatchids.qty) >= int(qtytodeduct):

                                post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(stock_obj.item_code)+"0000",
                                item_uom=uom_ids.item_uom).order_by('pk').last() 


                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(stock_obj.item_code)+"0000",
                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno if adjno else memo_no,trn_date=currentdate,
                                trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=-1,trn_balqty=obatchids.qty-1,
                                trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                trn_amt=None,trn_post=currentdate,
                                trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                line_no=1,item_uom=uom_ids.item_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None)
                                stktrn_id.save()
                                
                                stktrnids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(stock_obj.item_code)+"0000",
                                item_uom=request.data['uom']).order_by('pk').last() 


                                stktrnid = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(stock_obj.item_code)+"0000",
                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno,trn_date=currentdate,
                                trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=uom_ids.uom_unit,trn_balqty=uom_ids.uom_unit,
                                trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                trn_amt=None,trn_post=currentdate,
                                trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                line_no=1,item_uom=request.data['uom'],item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None)
                                stktrnid.save()
                            

                                fbatch_qty = (batchids.qty + uom_ids.uom_unit) - request.data['qty']

                                vstk = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(stock_obj.item_code)+"0000",
                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=memo_no,trn_date=currentdate,
                                trn_type="SUM",trn_db_qty=None,trn_cr_qty=None,trn_qty=-request.data['qty'],trn_balqty=fbatch_qty,
                                trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                trn_amt=None,trn_post=currentdate,
                                trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                line_no=1,item_uom=request.data['uom'],item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None)
                                vstk.save()
                            

                                ItemBatch.objects.filter(pk=batchids.pk).update(qty=fbatch_qty,updated_at=timezone.now())

                                ItemBatch.objects.filter(pk=obatchids.pk).update(qty=obatchids.qty-1,updated_at=timezone.now())
                                
                                adcontrolobj.control_no = int(adcontrolobj.control_no) + 1
                                adcontrolobj.save()

                                flag = True

                            if flag == False:
                                if batchids:
                                    deduct = batchids.qty - request.data['qty']
                                    batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                                else:
                                    batch_id = ItemBatch(item_code=stock_obj.item_code,site_code=site.itemsite_code,
                                    batch_no="",uom=i.uom,qty=-request.data['qty'],exp_date=None,batch_cost=None).save()
                                    deduct = -request.data['qty']

                                #Stktrn
                                currenttime = timezone.now()
                                currentdate = timezone.now().date()
                        
                                post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(request.data['qty'])+"0000",
                                item_uom=request.data['uom']).order_by('pk').last() 

                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(stock_obj.item_code)+"0000",
                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=memo_no,trn_date=currentdate,
                                trn_type="SUM",trn_db_qty=None,trn_cr_qty=None,trn_qty=-request.data['qty'],trn_balqty=deduct,
                                trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                trn_amt=None,trn_post=currentdate,
                                trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                line_no=1,item_uom=request.data['uom'],item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None)
                                stktrn_id.save()
                            
            

                result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_201_CREATED)
            
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
            'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
    
    def get_object(self, pk):
        try:
            return UsageMemo.objects.get(pk=pk)
        except UsageMemo.DoesNotExist:
            raise Exception('Record does not exist') 

    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            if int(request.data['quantity']) <= 0:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please enter valid quantity",
                'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            instance = self.get_object(pk)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                quantity = instance.qty - request.data['quantity']
                serializer.save(qty=quantity,updated_at=timezone.now())
                
                
                #ItemBatch
                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                item_code=instance.item_code[:-4],uom=instance.uom).order_by('pk').last()
                
                if batch_ids:
                    addamt = batch_ids.qty + request.data['quantity']
                    batch_ids.qty = addamt
                    batch_ids.updated_at = timezone.now()
                    batch_ids.save()

                    #Stktrn
                
                    currenttime = timezone.now()
                    currentdate = timezone.now().date()

                    post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                    itemuom_ids = ItemUomprice.objects.filter(item_code=instance.item_code[:-4],item_uom=instance.uom,isactive=True).order_by('pk').first()

                    
                
                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                    itemcode=instance.item_code,store_no=site.itemsite_code,
                    tstore_no=None,fstore_no=None,trn_docno=instance.memo_no,
                    trn_type="SUA",trn_db_qty=None,trn_cr_qty=None,
                    trn_qty=request.data['quantity'],trn_balqty=addamt,trn_balcst=0,
                    trn_amt=itemuom_ids.item_price if itemuom_ids and itemuom_ids.item_price else None,
                    trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                    hq_update=0,line_no=1,item_uom=instance.uom,
                    item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None,trn_post=currentdate,
                    trn_date=currentdate).save()
            

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_200_OK) 

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        

class TreatmentFaceViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Treatmentface.objects.filter().order_by('-id')
    serializer_class = TreatmentfaceSerializer

    def get_object(self, pk):
        try:
            return Treatmentface.objects.get(pk=pk)
        except Treatmentface.DoesNotExist:
            raise Exception('Record does not exist') 

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            # treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
            treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None)).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            # treatface = Treatmentface.objects.filter(treatment_code=treat_obj.treatment_code,
            # site_code=site.itemsite_code).order_by('pk').first()

            treatface = Treatmentface.objects.filter(treatment_code=treat_obj.treatment_code,
            ).order_by('pk').first()
           
           
            if treatface:
                serializer = TreatmentfaceSerializer(treatface)
                newdict = dict()
                newdict.update(serializer.data)
                newdict.update({'room_id':treat_obj.Trmt_Room_Codeid.pk if treat_obj.Trmt_Room_Codeid else "",
                'room_name': treat_obj.Trmt_Room_Codeid.displayname if treat_obj.Trmt_Room_Codeid else "",
                'remarks': treat_obj.remarks})
                 
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
                'data':  newdict}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
                'data':  []}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            if request.GET.get('treat_id',None):
                # treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
                treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None)).first()
                if not treat_obj:
                    result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            
            # treatface_ids = Treatmentface.objects.filter(treatment_code=treat_obj.treatment_code,
            # site_code=site.itemsite_code).order_by('pk')
            treatface_ids = Treatmentface.objects.filter(treatment_code=treat_obj.treatment_code,
            ).order_by('pk')
            if treatface_ids:
                result = {'status': status.HTTP_200_OK,"message":"Already Record is there for Treatment Face!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            
           
            serializer = TreatmentfaceSerializer(data=request.data)
            if serializer.is_valid():
                treat_obj.remarks = request.data['treat_remarks']
                if 'room_id' in request.data and request.data['room_id']:
                    # room_obj = Room.objects.filter(pk=request.data['room_id'],site_code=site.itemsite_code).first()
                    room_obj = Room.objects.filter(pk=request.data['room_id']).first()
                    treat_obj.Trmt_Room_Codeid = room_obj if room_obj else None
                    treat_obj.trmt_room_code = room_obj.room_code
                    treat_obj.save()
                
                serializer.save(site_code=site.itemsite_code)

                result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_201_CREATED)
            
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
            'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
            

    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            instance = self.get_object(pk)
            # treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
            treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None)).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid(): 
                treat_obj.remarks = request.data['treat_remarks']
                if request.data['room_id']:
                    # room_obj = Room.objects.filter(pk=request.data['room_id'],site_code=site.itemsite_code).first()
                    room_obj = Room.objects.filter(pk=request.data['room_id']).first()
                    treat_obj.Trmt_Room_Codeid = room_obj if room_obj else None
                    treat_obj.trmt_room_code = room_obj.room_code
                    treat_obj.save()
                
                serializer.save(updated_at=timezone.now())

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_200_OK)
            
            
            data = serializer.errors
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
             
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   


class TransactionInvoicesViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            q = self.request.GET.get('search',None)
            custid = self.request.GET.get('custid',None)
            data = []
            if q:
                queryset = PosHaud.objects.filter(isvoid=False,
                ItemSite_Codeid__pk=site.pk,
                sa_transacno_ref__icontains=q).order_by('pk')
                # print(queryset,"queryset")
                serializer = TransactionInvoiceSerializer(queryset, many=True)
                # print(serializer.data,"serializer")

                manual_query = ManualInvoiceModel.objects.filter(active='active',
                manualinv_number__icontains=q).order_by('pk')
                # print(manual_query,"manual_query")
                serializerdata = TransactionManualInvoiceSerializer(manual_query, many=True)
                # print(serializerdata.data,"serializerdata")

                data = serializer.data + serializerdata.data

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",
                'error': False, 'data' :data}
                return Response(result, status=status.HTTP_200_OK)
            else:
                if custid:
                    cust_obj = Customer.objects.filter(pk=custid,
                    cust_isactive=True).first()
                    if not cust_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
                    queryset = PosHaud.objects.filter(isvoid=False,
                    ItemSite_Codeid__pk=site.pk,sa_custnoid=cust_obj,
                    ).order_by('pk')
                    # print(queryset,"queryset")
                    serializer = TransactionInvoiceSerializer(queryset, many=True)
                    # print(serializer.data,"serializer")

                    manual_query = ManualInvoiceModel.objects.filter(active='active',
                    cust_id=cust_obj).order_by('pk')
                    # print(manual_query,"manual_query")
                    serializerdata = TransactionManualInvoiceSerializer(manual_query, many=True)
                    # print(serializerdata.data,"serializerdata")

                    data = serializer.data + serializerdata.data

                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",
                    'error': False, 'data' :data}
                    return Response(result, status=status.HTTP_200_OK)

            
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",
            'error': False, 'data' :data}
            return Response(result, status=status.HTTP_200_OK)


        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   

            
class TransactionHistoryViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = BillingSerializer

    def get_queryset(self):
        # now2 = timezone.now()
        # print(str(now2.hour) + '  ' +  str(now2.minute) + '  ' +  str(now2.second),"1 End hour, minute, second\n")
         
        
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        year = timezone.now().year
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)
        transac_no = self.request.GET.get('transac_no',None)
        cust_code = self.request.GET.get('cust_code',None)
        cust_name = self.request.GET.get('cust_name',None)
        invoice_type = self.request.GET.get('invoice_type',None)
        cust_id = self.request.GET.get('cust_id',None)
        sales_staffs = self.request.GET.get('sales_staffs',None)
        
        system_setup = Systemsetup.objects.filter(title='allinvoiceviewsetting',
        value_name='allinvoiceviewsetting',isactive=True).first()

        cus_system_setup = Systemsetup.objects.filter(title='Customer Profile - Invoice History',
        value_name='allinvoiceviewsetting',isactive=True).first()
        queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('-pk')
        if not cust_id:
            if system_setup and system_setup.value_data == 'True':
                queryset = PosHaud.objects.filter().order_by('-pk')
        else:
            if cust_id:
                queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk,
                    sa_custnoid__pk=cust_id).order_by('-pk')
                if cus_system_setup and cus_system_setup.value_data == 'True':
                    queryset = PosHaud.objects.filter(sa_custnoid__pk=cust_id).order_by('-pk')




        if not from_date and not to_date and not transac_no and not cust_code and not cust_name:
            queryset = queryset
        else:
            if from_date and to_date:
                if invoice_type == "All": 
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).order_by('-pk')
                elif invoice_type == "Sales": 
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date,
                    sa_transacno_type="Receipt").order_by('-pk')
                elif invoice_type == "Void": 
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date,
                    sa_transacno_type="Void Transaction").order_by('-pk')
                elif invoice_type == "TD": 
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date,
                    sa_transacno_type="Redeem Service").order_by('-pk')
                elif invoice_type == "NonSales":
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date,
                    sa_transacno_type="Non Sales").order_by('-pk') 
                else:
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).order_by('-pk')


         
            if transac_no:
                if cust_id:
                    #queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk,sa_date__date__gte=from_date,
                    #sa_date__date__lte=to_date,sa_transacno_ref__icontains=transac_no,sa_custnoid__pk=cust_id).order_by('-pk')
                    queryset = PosHaud.objects.filter(sa_date__date__gte=from_date,
                    sa_date__date__lte=to_date,sa_transacno_ref__icontains=transac_no,sa_custnoid__pk=cust_id).order_by('-pk')
                else:
                    #queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk,sa_date__date__gte=from_date,
                    #sa_date__date__lte=to_date,sa_transacno_ref__icontains=transac_no).order_by('-pk')
                    queryset = PosHaud.objects.filter(sa_date__date__gte=from_date,
                    sa_date__date__lte=to_date,sa_transacno_ref__icontains=transac_no).order_by('-pk')

            if cust_code:
                queryset = queryset.filter(sa_custno__icontains=cust_code).order_by('-pk')
            if cust_name:
                queryset = queryset.filter(Q(sa_custname__icontains=cust_name) | Q(sa_custno__icontains=cust_name) | Q(sa_custnoid__cust_refer__icontains=cust_name)).order_by('-pk')
            
            fquery = list(queryset.filter().order_by('-pk').values_list('sa_transacno', flat=True).distinct())
            # print(queryset,"queryset11")
            #sales staffs
           
            sales_multi = False ; help_ids = False

            salsystem_setup = Systemsetup.objects.filter(title='TransactionHistoryFilterSalesStaff',
            value_name='TransactionHistoryFilterSalesStaff',isactive=True).first()
            
            if salsystem_setup and salsystem_setup.value_data == 'True':
                # print(sales_staffs,"sales_staffs")
                if sales_staffs:
                    salesstaff = str(sales_staffs).split(',')
                    # print(salesstaff,"salesstaff")
                    if sales_staffs[0] == '0':
                        # print("iff")
                        return queryset
                    else:   

                        squeryset = PosHaud.objects.none()
                        wqueryset = PosHaud.objects.none()

                        # print("else") 
                        emp_ids = Employee.objects.filter(emp_isactive=True,pk__in=salesstaff,show_in_sales=True).order_by('-pk').values_list('emp_code', flat=True).distinct()
                        # print(emp_ids,"emp_ids")
                        if emp_ids:
                            sales_multi = Multistaff.objects.filter(emp_code__in=list(emp_ids),sa_transacno__in=fquery).order_by('-pk').values_list('sa_transacno', flat=True).distinct() 
                            # print(sales_multi,"sales_multi")
                            if sales_multi:
                                squeryset = PosHaud.objects.filter(sa_transacno__in=list(sales_multi)).order_by('-pk').values_list('pk', flat=True).distinct()
                                # print(queryset,"queryset77")
                            
            
                        #Workstaffs 
                        if fmspw[0].Emp_Codeid and fmspw[0].Emp_Codeid.emp_isactive == True and fmspw[0].Emp_Codeid.show_in_trmt == True:
                            # print("gg")
                            help_ids = ItemHelper.objects.filter(site_code=site.itemsite_code,
                            helper_code=fmspw[0].Emp_Codeid.emp_code,sa_transacno__in=fquery).order_by('-pk').values_list('helper_transacno', flat=True).distinct() 
                            # print(help_ids,"help_ids")
                            if help_ids:
                                wqueryset = PosHaud.objects.filter(sa_transacno__in=list(help_ids)).order_by('-pk').values_list('pk', flat=True).distinct()
                                # print(wqueryset,"wqueryset")

                        if squeryset and wqueryset:
                            # print("iff 11")
                            combined_list = list(chain(squeryset,wqueryset))
                            queryset = PosHaud.objects.filter(pk__in=combined_list).order_by('-pk')
                            # print(queryset,"combined_list 8888")
                        elif squeryset:
                            # print("iff 22")
                            combined_list = squeryset
                            queryset = PosHaud.objects.filter(pk__in=combined_list).order_by('-pk')
                        elif wqueryset:
                            # print("iff 33")
                            combined_list = wqueryset
                            queryset = PosHaud.objects.filter(pk__in=combined_list).order_by('-pk') 
                        elif not squeryset and not wqueryset:
                            queryset = PosHaud.objects.none()


            # #not work,sales,role
            # if fmspw[0].Emp_Codeid and fmspw[0].Emp_Codeid.emp_isactive == True:
            #     if not fmspw[0].Emp_Codeid.show_in_trmt == True and not fmspw[0].Emp_Codeid.show_in_sales == True:
            #         if fmspw[0].LEVEL_ItmIDid and fmspw[0].LEVEL_ItmIDid.role_code != 1 and not sales_staffs:
            #             queryset = PosHaud.objects.none()

        # now1 = timezone.now()
        # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"1 End hour, minute, second\n")
        # totalh = now1.second - now2.second
        # print(totalh,"total 1")
        return queryset
    
    def list(self, request):
        try:
            # now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            # now2 = timezone.now()
            # print(str(now2.hour) + '  ' +  str(now2.minute) + '  ' +  str(now2.second),"3 End hour, minute, second\n")
            
            # totalr = now2.second - now.second
            # print(totalr,"total 22")
            year = timezone.now().year
            queryset = self.filter_queryset(self.get_queryset()).order_by('-pk')
            # queryset = PosHaud.objects.filter(sa_date__year=year).order_by('-pk')
            serializer_class =  BillingSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action,)
            v = result.get('data')
            d = v.get('dataList')
            # sa_total = "{:.2f}".format(sum([float(i['sa_totamt']) for i in d]))
            # result.update({'sa_total':sa_total})
            # now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"3 End hour, minute, second\n")
            # totalh = now1.second - now2.second
            # print(totalh," total")
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 

    def get_object(self, pk):
        try:
            return PosHaud.objects.get(pk=pk)
        except PosHaud.DoesNotExist:
            raise Http404 

    def retrieve(self, request, pk=None):
        try:
            poshaud = self.get_object(pk)
            serializer = PodhaudSerializer(poshaud)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
            'data': serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    @transaction.atomic
    @action(detail=False, methods=['POST'], name='changeprice')
    def changeprice(self, request):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
                ori_total_amt = 0; ori_paid_amt = 0; sum_total_amt = 0; sum_paid_amt = 0
                for idx, i in enumerate(request.data, start=1): 
                    daudobj = PosDaud.objects.filter(pk=i['id']).first()
                    if daudobj:
                        ori_total_amt += float(daudobj.dt_transacamt)
                        ori_paid_amt += float(daudobj.dt_deposit)
                        sum_total_amt += float(i['dt_transacamt'])
                        sum_paid_amt += float(i['dt_deposit'])

                bal_total_amt = ori_total_amt - sum_total_amt
                bal_paid_amt = ori_paid_amt - sum_paid_amt
                if bal_total_amt != 0 or bal_paid_amt != 0:
                    raise Exception('Balance Total Amount and Balance Paid Amount should be 0!!') 
                gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()

                for idx, req in enumerate(request.data, start=1): 
                    # print(req,"req")
                    # print(req['dt_transacamt'],"ll")
                  
                    daud_obj = PosDaud.objects.filter(pk=req['id']).first()
                    if daud_obj:
                        outstanding_acc = float(req['dt_transacamt']) - float(req['dt_deposit'])
                        
                        calcgst = 0
                        if gst:
                            calcgst = gst.item_value if gst and gst.item_value else 0.0
                        if calcgst > 0:
                            sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
                            if sitegst:
                                if sitegst.site_is_gst == False:
                                    calcgst = 0
                        # print(calcgst,"0 calcgst")
                        gst_amt_collect = 0
                        if calcgst > 0:
                            if gst and gst.is_exclusive == True:
                                gst_amt_collect = float(req['dt_deposit']) * (calcgst/ 100)
                            else:
                                gst_amt_collect = float(req['dt_deposit']) * calcgst / (100+calcgst)
                              

                        PosDaud.objects.filter(pk=req['id']).update(dt_price="{:.2f}".format(float(req['dt_price'])),
                        dt_discamt="{:.2f}".format(float(req['dt_discamt'])),dt_discpercent=0,
                        dt_promoprice="{:.2f}".format(float(req['dt_promoprice'])),dt_amt="{:.2f}".format(float(req['dt_transacamt'])),
                        dt_transacamt="{:.2f}".format(float(req['dt_transacamt'])),dt_deposit="{:.2f}".format(float(req['dt_deposit'])),
                        topup_outstanding=outstanding_acc if outstanding_acc is not None and outstanding_acc > 0 else 0,gst_amt_collect="{:.2f}".format(float(gst_amt_collect)))
                        
                        price_ids = priceChangeLog.objects.filter(sa_transacno=daud_obj.sa_transacno,
                        itemsite_code=daud_obj.itemsite_code,dt_itemno=daud_obj.dt_itemno,
                        dt_lineno=daud_obj.dt_lineno).order_by('lineno')

                        if not price_ids:
                            lineno = 1
                        else:
                            rec = price_ids.last()
                            lineno = float(rec.lineno) + 1  

                        priceChangeLog(sa_transacno=daud_obj.sa_transacno,itemsite_code=daud_obj.itemsite_code,
                        dt_itemno=daud_obj.dt_itemno,dt_lineno=daud_obj.dt_lineno,lineno=lineno,
                        price=daud_obj.dt_price,discAmt=daud_obj.dt_discamt,discPrice=daud_obj.dt_promoprice,
                        transacAmount=daud_obj.dt_transacamt,depositAmount=daud_obj.dt_deposit,
                        newPrice="{:.2f}".format(float(req['dt_price'])),newDiscAmt="{:.2f}".format(float(req['dt_discamt'])),
                        newDiscPrice="{:.2f}".format(float(req['dt_promoprice'])),newTransacAmount="{:.2f}".format(float(req['dt_transacamt'])),
                        newDepositAmount="{:.2f}".format(float(req['dt_deposit']))).save()   

                        posdisc_ids = PosDisc.objects.filter(sa_transacno=daud_obj.sa_transacno,
                        dt_itemno=daud_obj.dt_itemno,dt_lineno=daud_obj.dt_lineno).order_by('pk').first()
                        other_ids = PosDisc.objects.filter(sa_transacno=daud_obj.sa_transacno,
                        dt_itemno=daud_obj.dt_itemno,dt_lineno=daud_obj.dt_lineno).exclude(pk=posdisc_ids.pk).delete()
                        if posdisc_ids:
                            PosDisc.objects.filter(pk=posdisc_ids.pk).update(disc_amt="{:.2f}".format(float(req['dt_discamt'])),
                            disc_percent=0,dt_auto=0,dt_price="{:.2f}".format(float(req['dt_price'])),istransdisc=False)


                        multi_ids = Multistaff.objects.filter(sa_transacno=daud_obj.sa_transacno,
                        item_code=daud_obj.dt_itemno,dt_lineno=daud_obj.dt_lineno).order_by('pk')
                        # print(multi_ids,"multi_ids")
                        mcount = multi_ids.count()
                        if multi_ids:
                            unit_amount = float(req['dt_transacamt']) / mcount
                            amt = "{:.2f}".format(float(unit_amount))  
                            lval = float(req['dt_transacamt']) - (float(amt) * (mcount -1))
                            for idx, reqt in enumerate(multi_ids, start=1): 
                                if idx == mcount:
                                    reqt.salesamt="{:.2f}".format(float(lval))
                                else:
                                    reqt.salesamt="{:.2f}".format(float(unit_amount))
                                reqt.save() 

                            # tmulti_ids = Tmpmultistaff.objects.filter(sa_transacno=daud_obj.sa_transacno,
                            # item_code=daud_obj.dt_itemno,dt_lineno=daud_obj.dt_lineno).order_by('pk')
                            tmulti_ids = Tmpmultistaff.objects.filter(
                            item_code=daud_obj.dt_itemno[:-4],dt_lineno=daud_obj.dt_lineno).order_by('pk')
                            if tmulti_ids:
                                for idx, reqy in enumerate(tmulti_ids, start=1): 
                                    if idx == mcount:
                                        reqy.salesamt="{:.2f}".format(float(lval))
                                    else:
                                        reqy.salesamt="{:.2f}".format(float(unit_amount))
                                    reqy.save() 

                        # print(req['dt_transacamt'],"req['dt_transacamt']")
                        
                        if int(daud_obj.dt_itemnoid.item_div) == 3 and daud_obj.record_detail_type == 'SERVICE':
                            treat_ids = TreatmentAccount.objects.filter(ref_transacno=daud_obj.sa_transacno,type='Deposit', 
                            dt_lineno = daud_obj.dt_lineno).order_by('pk').first()
                            if treat_ids:
                                Price = float(req['dt_transacamt'])
                                Unit_Amount = Price / daud_obj.dt_qty

                                desc = "Total Service Amount : "+str("{:.2f}".format(float(req['dt_transacamt'])))
                                TreatmentAccount.objects.filter(pk=treat_ids.pk).update(description=desc,
                                amount="{:.2f}".format(float(req['dt_deposit'])),balance="{:.2f}".format(float(req['dt_deposit'])),
                                outstanding="{:.2f}".format(float(outstanding_acc)) if outstanding_acc is not None and outstanding_acc > 0 else 0,deposit="{:.2f}".format(float(req['dt_deposit'])))
                                

                                otreat_ids = TreatmentAccount.objects.filter(ref_transacno=daud_obj.sa_transacno,
                                treatment_parentcode=treat_ids.treatment_parentcode).exclude(type='Deposit').order_by('pk')
                                balance = float(req['dt_deposit']); outstanding = outstanding_acc
                                for idx, i in enumerate(otreat_ids, start=1):
                                    if i.type in ['Sales','CANCEL']:
                                        amount = -float("{:.2f}".format(float(Unit_Amount * i.qty )))
                                        balance =  balance - (Unit_Amount * i.qty)
                                        outstanding = outstanding_acc
                                    elif i.type == 'Top Up':     
                                        if idx == 1:
                                            bval = float(req['dt_deposit']) + i.amount
                                            balance += bval
                                            oval = outstanding_acc - i.amount
                                            outstanding += oval
                                        else:
                                            bval = balance + i.amount
                                            balance += bval
                                            oval = outstanding - i.amount
                                            outstanding += oval


                                    i.amount = amount
                                    i.balance = "{:.2f}".format(float(balance))
                                    i.outstanding = "{:.2f}".format(float(outstanding))
                                    i.save()

                           

                                tret_ids = Treatment.objects.filter(sa_transacno=daud_obj.sa_transacno,
                                treatment_parentcode=treat_ids.treatment_parentcode).order_by('pk').values_list('pk', flat=True).distinct()
                                Treatment.objects.filter(pk__in=list(tret_ids)).update(price="{:.2f}".format(float(req['dt_transacamt'])),
                                unit_amount="{:.2f}".format(float(Unit_Amount)))

                                open_ids = Treatment.objects.filter(sa_transacno=daud_obj.sa_transacno,
                                treatment_parentcode=treat_ids.treatment_parentcode,status='Done').order_by('pk')
                                for i in open_ids:
                                    helper_ids =ItemHelper.objects.filter(sa_transacno=daud_obj.sa_transacno,
                                    line_no=daud_obj.dt_lineno,item_code=i.treatment_code).order_by('pk')
                                    for h in helper_ids:
                                        share_amt = float(Unit_Amount) / float(helper_ids.count())
                                        if h.amount > 0:
                                            h.amount = Unit_Amount
                                        elif h.amount < 0:
                                            h.amount = -float("{:.2f}".format(Unit_Amount))

                                        if h.share_amt > 0:
                                            h.share_amt = share_amt
                                        elif h.share_amt < 0:
                                            h.share_amt  = share_amt

                                        h.save() 

                                    ihelper_ids =TmpItemHelper.objects.filter(sa_transacno=daud_obj.sa_transacno,
                                    line_no=daud_obj.dt_lineno,item_code=i.treatment_code).order_by('pk')
                                    for hl in ihelper_ids:
                                        if hl.amount > 0:
                                            hl.amount = Unit_Amount
                                        elif hl.amount < 0:
                                            hl.amount = -float("{:.2f}".format(Unit_Amount))

                                        hl.save() 
                                       
                        
                        elif int(daud_obj.dt_itemnoid.item_div) == 1 and daud_obj.record_detail_type == 'PRODUCT':
                            depoids = DepositAccount.objects.filter(ref_transacno=daud_obj.sa_transacno,type='CANCEL', 
                            ).order_by('pk')
                            if not depoids: 
                                depo_ids = DepositAccount.objects.filter(ref_transacno=daud_obj.sa_transacno,type='Deposit', 
                                dt_lineno=daud_obj.dt_lineno).order_by('pk').first()  
                                if depo_ids:
                                    desc = "Total Product Amount : "+str("{:.2f}".format(float(req['dt_transacamt'])))

                                    DepositAccount.objects.filter(pk=depo_ids.pk).update(description=desc,
                                    amount="{:.2f}".format(float(req['dt_deposit'])),balance="{:.2f}".format(float(req['dt_deposit'])),
                                    outstanding="{:.2f}".format(float(outstanding_acc)) if outstanding_acc is not None and outstanding_acc > 0 else 0,deposit="{:.2f}".format(float(req['dt_deposit'])))
                                    

                                    odepo_ids = DepositAccount.objects.filter(ref_transacno=daud_obj.sa_transacno,ref_productcode=depo_ids.ref_productcode, 
                                    ).exclude(type='Deposit').order_by('pk')  
                                    if odepo_ids:
                                        balance = 0; outstanding = 0
                                        for idx, i in enumerate(odepo_ids, start=1):
                                            if idx == 1:
                                                bval = float(req['dt_deposit']) + i.amount
                                                balance += bval
                                                oval = outstanding_acc - i.amount
                                                outstanding += oval
                                            else:
                                                bval = balance + i.amount
                                                balance += bval
                                                oval = outstanding - i.amount
                                                outstanding += oval

                                            
                                            i.balance = "{:.2f}".format(float(balance))
                                            i.outstanding = "{:.2f}".format(float(outstanding))
                                            i.save()

                result = {'status': status.HTTP_200_OK , "message": "Updated Succesfully", 'error': False}
                return Response(result, status=status.HTTP_200_OK)                                    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         
        
                        


class SiteApptSettingViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = SiteApptSettingSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        queryset = ItemSitelist.objects.none()

        # if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
        queryset = ItemSitelist.objects.filter(pk=site.pk,itemsite_isactive=True).order_by('-pk')
       
        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


    def get_object(self, pk):
        try:
            return ItemSitelist.objects.get(pk=pk)
        except ItemSitelist.DoesNotExist:
            raise Http404


    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            instance = self.get_object(pk)
           
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid(): 
                serializer.save()

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_200_OK)
            
            
            data = serializer.errors
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
             
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        
        

class CustomerAccountViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CustomerAccountSerializer

    # def get_queryset(self):
    #     fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
    #     site = fmspw[0].loginsite

    #     system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
    #     value_name='Other Outlet Customer Listings',isactive=True).first()
    #     if system_setup and system_setup.value_data == 'True':
    #         queryset = Customer.objects.filter(cust_isactive=True).exclude(site_code__isnull=True).only('cust_isactive').order_by('-pk')
    #     else:
    #         queryset = Customer.objects.filter(cust_isactive=True,site_code=site.itemsite_code).only('cust_isactive').order_by('-pk')

    #     q = self.request.GET.get('search', None)
    #     value = self.request.GET.get('sortValue', None)
    #     key = self.request.GET.get('sortKey', None)

    #     if q:
    #         queryset = queryset.filter(Q(cust_name__icontains=q) | 
    #         Q(cust_email__icontains=q) | Q(cust_code__icontains=q) | Q(cust_phone2__icontains=q) | Q(cust_phone1__icontains=q) |
    #         Q(cust_nric__icontains=q)  | Q(cust_refer__icontains=q) )[:20]

    #     tr_balance = 0.0 ; tr_outstanding = 0.0; tr_check = False
    #     pr_balance = 0.0 ; pr_outstanding = 0.0; pr_check = False
    #     pre_balance = 0.0 ; pre_outstanding = 0.0; pre_check = False
    #     cust_lst = []

    #     for obj in queryset: 
    #         tr_acc = TreatmentAccount.objects.filter(cust_code=obj.cust_code,type='Deposit').exclude(
    #         sa_status="VOID").only('cust_code','type').order_by('pk')
            
            
    #         for i in tr_acc: 
    #             last_tracc_ids = TreatmentAccount.objects.filter(ref_transacno=i.sa_transacno,
    #             treatment_parentcode=i.treatment_parentcode
    #             ).only('ref_transacno','treatment_parentcode').order_by('-pk').first()
    #             if last_tracc_ids:
    #                 tr_balance += last_tracc_ids.balance if last_tracc_ids.balance else 0
    #                 tr_outstanding += last_tracc_ids.outstanding if last_tracc_ids.outstanding else 0 

    #         depo_ids = DepositAccount.objects.filter(cust_code=obj.cust_code,type='Deposit', 
    #         outstanding__gt=0).order_by('pk')        
                    
    #         for j in depo_ids:
    #             dacc_ids = DepositAccount.objects.filter(ref_transacno=j.sa_transacno,
    #             ref_productcode=j.treat_code).order_by('id').order_by('sa_date','sa_time','id').last()
    #             if dacc_ids:
    #                 pr_balance += dacc_ids.balance if dacc_ids.balance else 0
    #                 pr_outstanding += dacc_ids.outstanding if dacc_ids.outstanding else 0

    #         pre_acc = PrepaidAccount.objects.filter(cust_code=obj.cust_code,
    #         status=True,remain__gt=0).only('remain','cust_code','sa_status').order_by('pk')
    #         for k in pre_acc:
    #             lst_preacc_ids = PrepaidAccount.objects.filter(pp_no=k.pp_no,
    #             status=True,line_no=k.line_no).order_by('-pk').only('pp_no','status','line_no').first()
    #             if lst_preacc_ids:
    #                 pre_balance += lst_preacc_ids.remain if lst_preacc_ids.remain else 0
    #                 pre_outstanding += lst_preacc_ids.outstanding if lst_preacc_ids.outstanding else 0
                            
    #         custlst = {'cust_code': obj.cust_code, 'cust_name': obj.cust_name,
    #         'service_balance': tr_balance,'service_outstanding': tr_outstanding, 'service': tr_check,
    #         'product_balance': pr_balance,'product_outstanding': pr_outstanding, 'product': pr_check,
    #         'prepaid_balance': pre_balance,'prepaid_outstanding': pre_outstanding, 'prepaid': pre_check}

    #         if not any(d['cust_code'] == obj.cust_code for d in cust_lst):
    #             cust_lst.append(custlst)


    #     return custlst

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            site_code = site.itemsite_code
            
            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()
            if system_setup and system_setup.value_data == 'True':
                other_site = True
            else:
                other_site = False

            # print(other_site,"other_site")    

            start = datetime.datetime.strptime(request.GET.get("start"), "%Y/%m/%d")
            # print(start,"ll")
            end = datetime.datetime.strptime(request.GET.get("end"), "%Y/%m/%d")
            # print(end,"end")
            q = self.request.GET.get('search', None)
            # print(q,"q")
            custcode_lst =[]
            if q:
                # print("iff")
                queryset = Customer.objects.filter(Q(cust_name__icontains=q) | 
                Q(cust_email__icontains=q) | Q(cust_code__icontains=q) | Q(cust_phone2__icontains=q) | Q(cust_phone1__icontains=q) |
                Q(cust_nric__icontains=q)  | Q(cust_refer__icontains=q) )[:20]
                # print(queryset,"queryset")

                custcode_lst = [i.cust_code for i in queryset]
                # print(custcode_lst,"kk")
            
            
            # custcode_range = ""

            # if custcode_lst != []:
            #     custcode_range = " AND da.Cust_code IN '%s'" % (custcode_lst)
            
            # print(custcode_lst,"custcode_lst")
            # print(tuple(custcode_lst),"ll")
            c_range = "("+str(custcode_lst[0])+")" if len(custcode_lst) == 1 else tuple(custcode_lst)   
            # print(c_range,"c_range")

            

            final_lst = []
            if other_site == True:
                if custcode_lst == []:
                    raw_q = "SELECT da.Cust_code AS CustCode,ph.sa_custname AS CustName ,da.sa_Transacno,da.sa_date, da.sa_time,da.Site_Code AS Site_Code,(SELECT TOP 1 Balance FROM Deposit_Account WHERE ID = MAX(da.ID)) AS Balance,(SELECT TOP 1 Outstanding FROM Deposit_Account WHERE ID = MAX(da.ID)) AS Outstanding FROM Deposit_Account da INNER JOIN pos_haud ph ON da.sa_Transacno = ph.sa_Transacno WHERE da.sa_date >= '%s' AND da.sa_date <= '%s'  GROUP BY da.Cust_code, da.sa_Transacno, ph.sa_custname, da.sa_date, da.sa_time, da.Site_Code"% (start, end)
                else:
                    raw_q = "SELECT da.Cust_code AS CustCode,ph.sa_custname AS CustName ,da.sa_Transacno,da.sa_date, da.sa_time,da.Site_Code AS Site_Code,(SELECT TOP 1 Balance FROM Deposit_Account WHERE ID = MAX(da.ID)) AS Balance,(SELECT TOP 1 Outstanding FROM Deposit_Account WHERE ID = MAX(da.ID)) AS Outstanding FROM Deposit_Account da INNER JOIN pos_haud ph ON da.sa_Transacno = ph.sa_Transacno WHERE da.sa_date >= '%s' AND da.sa_date <= '%s' AND da.Cust_code IN %s GROUP BY da.Cust_code, da.sa_Transacno, ph.sa_custname, da.sa_date, da.sa_time, da.Site_Code"% (start, end, c_range)

            else:
                if custcode_lst == []:
                    raw_q = "SELECT da.Cust_code AS CustCode,ph.sa_custname AS CustName ,da.sa_Transacno,da.sa_date, da.sa_time, da.Site_Code AS Site_Code,(SELECT TOP 1 Balance FROM Deposit_Account WHERE ID = MAX(da.ID)) AS Balance,(SELECT TOP 1 Outstanding FROM Deposit_Account WHERE ID = MAX(da.ID)) AS Outstanding FROM Deposit_Account da INNER JOIN pos_haud ph ON da.sa_Transacno = ph.sa_Transacno WHERE ph.ItemSite_Code = '%s' AND da.Site_Code = '%s' AND da.sa_date >= '%s' AND da.sa_date <= '%s'  GROUP BY da.Cust_code, da.sa_Transacno, ph.sa_custname, da.sa_date, da.sa_time, da.Site_Code"% (site_code,site_code,start, end)
                else:
                    raw_q = "SELECT da.Cust_code AS CustCode,ph.sa_custname AS CustName ,da.sa_Transacno,da.sa_date, da.sa_time, da.Site_Code AS Site_Code,(SELECT TOP 1 Balance FROM Deposit_Account WHERE ID = MAX(da.ID)) AS Balance,(SELECT TOP 1 Outstanding FROM Deposit_Account WHERE ID = MAX(da.ID)) AS Outstanding FROM Deposit_Account da INNER JOIN pos_haud ph ON da.sa_Transacno = ph.sa_Transacno WHERE ph.ItemSite_Code = '%s' AND da.Site_Code = '%s' AND da.sa_date >= '%s' AND da.sa_date <= '%s' AND da.Cust_code IN %s  GROUP BY da.Cust_code, da.sa_Transacno, ph.sa_custname, da.sa_date, da.sa_time, da.Site_Code"% (site_code,site_code,start, end, c_range)


             
            # print(raw_q,"raw_q")
            with connection.cursor() as cursor:
                # print("iff")
                cursor.execute(raw_q)
                raw_qs = cursor.fetchall()
                # print(raw_qs,"raw_qs")
                desc = cursor.description
                for i, row in enumerate(raw_qs):
                    d = dict(zip([col[0] for col in desc], row))
                    # print(d,"d")
                    if d['Outstanding'] and float(d['Outstanding']) > 0:
                        datetime_obj = parser.parse(str(d['sa_date'])).date()
                        sadate = datetime.datetime.strptime(str(datetime_obj), "%Y-%m-%d").strftime("%d-%m-%Y")
                        if not any(d['CustCode'] == de['CustCode'] for de in final_lst):
                            val = {'CustCode': d['CustCode'],'Site_Code': d['Site_Code'],'CustName': d['CustName'],'sa_date':sadate,'product_bal': float("{:.2f}".format(d['Balance'])) if d['Balance'] else 0,'product_out': float("{:.2f}".format(d['Outstanding'])) if d['Outstanding'] else 0}
                            final_lst.append(val)
                        else:
                            for r in final_lst:
                                if d['CustCode'] in r.values():
                                    if 'product_bal' not in r:
                                        r.update({'product_bal': float("{:.2f}".format(d['Balance'])) if d['Balance'] else 0})
                                    else:
                                        r['product_bal'] += float("{:.2f}".format(d['Balance'])) if d['Balance'] else 0
                                    if 'product_out' not in r:
                                        r.update({'product_out': float("{:.2f}".format(d['Outstanding'])) if d['Outstanding'] else 0})
                                    else:
                                        r['product_out'] += float("{:.2f}".format(d['Outstanding'])) if d['Outstanding'] else 0


               
            if other_site == True:
                if custcode_lst == []:
                    raw_d = "SELECT A.CustCode,A.CUST_NAME AS CustName, B.Balance, B.Outstanding , A.sa_date, A.sa_time, A.Site_Code FROM(SELECT TOP 100 PERCENT ta.Cust_code AS CustCode, t.dt_LineNo, t.Item_Code, t.Treatment_ParentCode, MAX(ta.ID) AS MAX_TA_ID , t.CUST_NAME, ta.sa_date, ta.sa_time,t.Site_Code FROM Treatment_Account AS ta INNER JOIN Treatment AS t ON ta.Treatment_ParentCode = t.Treatment_ParentCode WHERE ta.sa_status != 'VOID' AND ta.sa_date >= '%s' and ta.sa_date <= '%s'  GROUP BY ta.Cust_code, t.dt_LineNo, t.Item_Code, t.Treatment_ParentCode, t.CUST_NAME, ta.sa_date, ta.sa_time,t.Site_Code ORDER BY ta.Cust_code, t.dt_LineNo, t.Site_Code) AS A INNER JOIN (SELECT ID, Balance, Outstanding FROM Treatment_Account) AS B ON A.MAX_TA_ID = B.ID GROUP BY A.CustCode,A.CUST_NAME, B.Balance, B.Outstanding, A.sa_date, A.sa_time, A.Site_Code"% (start, end)
                else:
                    raw_d = "SELECT A.CustCode,A.CUST_NAME AS CustName, B.Balance, B.Outstanding , A.sa_date, A.sa_time, A.Site_Code FROM(SELECT TOP 100 PERCENT ta.Cust_code AS CustCode, t.dt_LineNo, t.Item_Code, t.Treatment_ParentCode, MAX(ta.ID) AS MAX_TA_ID , t.CUST_NAME, ta.sa_date, ta.sa_time,t.Site_Code FROM Treatment_Account AS ta INNER JOIN Treatment AS t ON ta.Treatment_ParentCode = t.Treatment_ParentCode WHERE ta.sa_status != 'VOID' AND ta.sa_date >= '%s' and ta.sa_date <= '%s' AND ta.Cust_code IN %s  GROUP BY ta.Cust_code, t.dt_LineNo, t.Item_Code, t.Treatment_ParentCode, t.CUST_NAME, ta.sa_date, ta.sa_time, t.Site_Code ORDER BY ta.Cust_code, t.dt_LineNo, t.Site_Code) AS A INNER JOIN (SELECT ID, Balance, Outstanding FROM Treatment_Account) AS B ON A.MAX_TA_ID = B.ID GROUP BY A.CustCode,A.CUST_NAME, B.Balance, B.Outstanding, A.sa_date, A.sa_time, A.Site_Code"% (start, end, c_range)

            else:
                if custcode_lst == []:
                    raw_d = "SELECT A.CustCode,A.CUST_NAME AS CustName, B.Balance, B.Outstanding , A.sa_date, A.sa_time, A.Site_Code FROM(SELECT TOP 100 PERCENT ta.Cust_code AS CustCode, t.dt_LineNo, t.Item_Code, t.Treatment_ParentCode, MAX(ta.ID) AS MAX_TA_ID , t.CUST_NAME, ta.sa_date, ta.sa_time,t.Site_Code FROM Treatment_Account AS ta INNER JOIN Treatment AS t ON ta.Treatment_ParentCode = t.Treatment_ParentCode WHERE ta.Site_Code = '%s' AND t.Site_Code = '%s' AND ta.sa_status != 'VOID' AND ta.sa_date >= '%s' and ta.sa_date <= '%s'  GROUP BY ta.Cust_code, t.dt_LineNo, t.Item_Code, t.Treatment_ParentCode, t.CUST_NAME, ta.sa_date, ta.sa_time, t.Site_Code ORDER BY ta.Cust_code, t.dt_LineNo,t.Site_Code) AS A INNER JOIN (SELECT ID, Balance, Outstanding FROM Treatment_Account) AS B ON A.MAX_TA_ID = B.ID GROUP BY A.CustCode,A.CUST_NAME, B.Balance, B.Outstanding, A.sa_date, A.sa_time, A.Site_Code"% (site_code,site_code,start, end)
                else:
                    raw_d = "SELECT A.CustCode,A.CUST_NAME AS CustName, B.Balance, B.Outstanding , A.sa_date, A.sa_time, A.Site_Code FROM(SELECT TOP 100 PERCENT ta.Cust_code AS CustCode, t.dt_LineNo, t.Item_Code, t.Treatment_ParentCode, MAX(ta.ID) AS MAX_TA_ID , t.CUST_NAME, ta.sa_date, ta.sa_time,t.Site_Code FROM Treatment_Account AS ta INNER JOIN Treatment AS t ON ta.Treatment_ParentCode = t.Treatment_ParentCode WHERE ta.Site_Code = '%s' AND t.Site_Code = '%s' AND ta.sa_status != 'VOID' AND ta.sa_date >= '%s' and ta.sa_date <= '%s' AND ta.Cust_code IN %s  GROUP BY ta.Cust_code, t.dt_LineNo, t.Item_Code, t.Treatment_ParentCode, t.CUST_NAME, t.sa_date, ta.sa_time, t.Site_Code ORDER BY ta.Cust_code, t.dt_LineNo,t.Site_Code) AS A INNER JOIN (SELECT ID, Balance, Outstanding FROM Treatment_Account) AS B ON A.MAX_TA_ID = B.ID GROUP BY A.CustCode,A.CUST_NAME, B.Balance, B.Outstanding, A.sa_date, A.sa_time, A.Site_Code"% (site_code,site_code,start, end, c_range)

            # print(raw_d,"raw_d")
            with connection.cursor() as cursor:
                # print("iff raw_d")
                cursor.execute(raw_d)
                raw_ds = cursor.fetchall()
                # print(raw_ds,"raw_ds")
                descs = cursor.description
                for i, rows in enumerate(raw_ds):
                    t = dict(zip([col[0] for col in descs], rows))
                    # print(t,"t")
                    if t['Outstanding'] and float(t['Outstanding']) > 0:
                        datetime_ob = parser.parse(str(t['sa_date'])).date()
                        sadate = datetime.datetime.strptime(str(datetime_ob), "%Y-%m-%d").strftime("%d-%m-%Y")
                        if not any(t['CustCode'] == te['CustCode'] for te in final_lst):
                            # print("iff")
                            t_val = {'CustCode': t['CustCode'],'Site_Code': t['Site_Code'],'CustName': t['CustName'],'sa_date':sadate,'treat_bal': float("{:.2f}".format(t['Balance'])) if t['Balance'] else 0,'treat_out': float("{:.2f}".format(t['Outstanding'])) if t['Outstanding'] else 0}
                            final_lst.append(t_val)
                        else:
                            # print("elsee")
                            # print(final_lst,"final_lst")
                            for j in final_lst:
                                # print(j,"jj")
                                if t['CustCode'] in j.values():
                                    if 'treat_bal' not in j:
                                        j.update({'treat_bal': float("{:.2f}".format(t['Balance'])) if t['Balance'] else 0})
                                    else:    
                                        j['treat_bal'] += float("{:.2f}".format(t['Balance'])) if t['Balance'] else 0
                                    if 'treat_out' not in j:
                                        j.update({'treat_out': float("{:.2f}".format(t['Outstanding'])) if t['Outstanding'] else 0})
                                    else:    
                                        j['treat_out'] += float("{:.2f}".format(t['Outstanding'])) if t['Outstanding'] else 0
                                            

            if other_site == True:      
                acc_ids = PrepaidAccount.objects.filter(sa_date__date__gte=start,sa_date__date__lte=end,outstanding__gt = 0,status=True).order_by('id').order_by('-pk').values('cust_code'
                ).order_by('cust_code').annotate(cust_name=F('cust_name'),sa_date=F('sa_date'),Site_Code=F('site_code'),total_remain=Sum('remain'),total_outstanding=Sum('outstanding')).order_by('-outstanding')
            else:
                acc_ids = PrepaidAccount.objects.filter(sa_date__date__gte=start,sa_date__date__lte=end,outstanding__gt = 0,status=True,site_code=site_code).order_by('id').order_by('-pk').values('cust_code'
                ).order_by('cust_code').annotate(cust_name=F('cust_name'),sa_date=F('sa_date'),Site_Code=F('site_code'),total_remain=Sum('remain'),total_outstanding=Sum('outstanding')).order_by('-outstanding')

            
            if custcode_lst != []:
                accids = acc_ids.filter(cust_code__in=custcode_lst)
            else:
                accids = acc_ids


            # print(accids,"accids")
            for i, rowp in enumerate(accids):
                # print(t,"t")
                datetimep = parser.parse(str(rowp['sa_date'])).date()
                # print(datetimep,"datetimep")
                sadate = datetime.datetime.strptime(str(datetimep), "%Y-%m-%d").strftime("%d-%m-%Y")
                if not any(rowp['cust_code'] == pe['CustCode'] for pe in final_lst):
                    p_val = {'CustCode': rowp['cust_code'],'Site_Code': rowp['Site_Code'],'CustName': rowp['cust_name'],'sa_date':sadate,'pre_bal': float("{:.2f}".format(rowp['total_remain'])) if rowp['total_remain'] else 0,'pre_out': float("{:.2f}".format(rowp['total_outstanding'])) if rowp['total_outstanding'] else 0}
                    final_lst.append(p_val)
                else:
                    for k in final_lst:
                        if rowp['cust_code'] in k.values():
                            if 'pre_bal' not in k:
                                k.update({'pre_bal': float("{:.2f}".format(rowp['total_remain'])) if rowp['total_remain'] else 0})
                            else:    
                                k['pre_bal'] += float("{:.2f}".format(rowp['total_remain'])) if rowp['total_remain'] else 0
                            if 'pre_out' not in k:
                                k.update({'pre_out': float("{:.2f}".format(rowp['total_outstanding'])) if rowp['total_outstanding'] else 0})
                            else:
                                k['pre_out'] += float("{:.2f}".format(rowp['total_outstanding'])) if rowp['total_outstanding'] else 0

            # print(final_lst,"final_lst")

            for fo in final_lst:
                cust_obj = Customer.objects.filter(cust_code=fo['CustCode'],cust_isactive=True).order_by('-pk').first()
                fo['cust_refer'] = cust_obj.cust_refer if cust_obj and cust_obj.cust_refer else ""
                if 'product_bal' in fo or 'product_out' in fo:
                    fo['product'] = True
                    fo['product_bal'] = "{:.2f}".format(fo['product_bal'])
                    fo['product_out'] = "{:.2f}".format(fo['product_out'])
                else:
                    fo['product'] = False
                    fo['product_bal'] = ""
                    fo['product_out'] = ""


                if 'treat_bal' in fo or 'treat_out' in fo:
                    fo['treat'] = True
                    fo['treat_bal'] = "{:.2f}".format(fo['treat_bal'])
                    fo['treat_out'] = "{:.2f}".format(fo['treat_out'])
                else:
                    fo['treat'] = False
                    fo['treat_bal'] = ""
                    fo['treat_out'] = ""


                if 'pre_bal' in fo or 'pre_out' in fo:
                    fo['prepaid'] = True
                    fo['pre_bal'] = "{:.2f}".format(fo['pre_bal'])
                    fo['pre_out'] = "{:.2f}".format(fo['pre_out'])
                else:
                    fo['prepaid'] = False
                    fo['pre_bal'] = ""
                    fo['pre_out'] = ""


                fo['iscurrent'] = ""
                if fo['Site_Code'] == site.itemsite_code:
                    fo['iscurrent'] = True
                elif fo['Site_Code'] != site.itemsite_code:
                    fo['iscurrent'] = False 


                # fo['is_allow']  = False
                # if fo['Site_Code']:
                #     if system_setup and system_setup.value_data == 'True':
                #         if fo['Site_Code'] != site.itemsite_code or fo['Site_Code'] == site.itemsite_code:
                #             fo['is_allow'] = True
                #     else:
                #         if fo['Site_Code'] == site.itemsite_code:
                #             fo['is_allow'] = True        

            final_val = sorted(final_lst, key=lambda d: (d['treat_bal'], d['treat_out'], d['product_bal'], d['product_out'], d['pre_bal'],d['pre_out']) , reverse=True)
            if final_val != []:
                limit = request.GET.get('limit',12)
                page= request.GET.get('page',1)
                paginator = Paginator(final_val, limit)
                total = len(final_val)

                total_page = 1

                if len(final_val) > int(limit):
                    total_page = math.ceil(len(final_val)/int(limit))

                if int(page) > total_page:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Content",'error': False, 
                    'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                    "total_pages":total_page}}, 
                    'dataList': []}}

                try:
                    queryset_data = paginator.page(page)
                except PageNotAnInteger:
                    queryset_data = paginator.page(1)
                    page= 1 
                except EmptyPage:
                    queryset_data = paginator.page(paginator.num_pages)    

                data_final = queryset_data.object_list

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,
                "total_pages":total_page}}, 'dataList': data_final}}
            
                return Response(result, status=status.HTTP_200_OK) 
            
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


class TreatmentUsageListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentUsageListSerializer
    queryset = TreatmentUsage.objects.filter(isactive=True).order_by('-pk')

    
    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            system_obj = Systemsetup.objects.filter(title='Other Outlet Customer Listings',
            value_name='Other Outlet Customer Listings',isactive=True).first()
            system_setup = Systemsetup.objects.filter(title='Other Outlet Customer Treatment Usage',
            value_name='Other Outlet Customer Treatment Usage',isactive=True).first()

            from_date = self.request.GET.get('from_date',None)
            to_date = self.request.GET.get('to_date',None)
            treatment = self.request.GET.get('treatment_desc',None)
            product = self.request.GET.get('item_desc',None)
            if not from_date or not to_date:
                result = {'status': status.HTTP_200_OK,"message":"Please Give From Date Or To Date!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
                
            if system_setup and system_setup.value_data == 'True' and system_obj and system_obj.value_data == 'True':
                query_haud = PosHaud.objects.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).order_by('pk').values_list('sa_transacno', flat=True).distinct()
                queryset = TreatmentUsage.objects.filter(isactive=True,sa_transacno__in=list(query_haud)).exclude(site_code__isnull=True).only('isactive').order_by('-pk')
            else:
                query_haud = PosHaud.objects.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date,itemsite_code=site.itemsite_code).order_by('pk').values_list('sa_transacno', flat=True).distinct()
                queryset = TreatmentUsage.objects.filter(isactive=True,sa_transacno__in=list(query_haud),site_code=site.itemsite_code).only('isactive').order_by('-pk')
            
            if treatment:
                treat_id = treatment.split(',')
                stocklst = Stock.objects.filter(pk__in=treat_id).order_by('item_name').values_list('item_code',flat=True).distinct()
                tlst = [str(i)+"0000" for i in list(stocklst)]
                treat_ids = Treatment.objects.filter(item_code__in=tlst).values_list('sa_transacno', flat=True).distinct()
                queryset = queryset.filter(sa_transacno__in=list(treat_ids)).order_by('-pk')
            if product:
                product_id = product.split(',')
                pstocklst = Stock.objects.filter(pk__in=product_id).order_by('item_name').values_list('item_code',flat=True).distinct()
                plst = [str(i)+"0000" for i in list(pstocklst)]
                queryset = queryset.filter(item_code__in=plst).order_by('-pk')
            
            # print(queryset,"queryset")
            if queryset:
                site_code = site.itemsite_code
                serializer_class = TreatmentUsageListSerializer
                total = len(queryset)
                state = status.HTTP_200_OK
                message = "Listed Succesfully"
                error = False
                data = None
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_200_OK) 
            
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK) 

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 

class ServiceListAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Stock.objects.filter(item_isactive=True).order_by('id')
    serializer_class = TreatmentUsageStockSerializer

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            query_set = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_div="3").order_by('item_name')
           
            if query_set:
                serializer = self.get_serializer(query_set, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    

    
class ProductListAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Stock.objects.filter(item_isactive=True).order_by('id')
    serializer_class = TreatmentUsageStockSerializer

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            query_set = Stock.objects.filter(item_isactive=True).filter(Q(item_div="2") | Q(item_div="1")).order_by('pk')
         
            if query_set:
                serializer = self.get_serializer(query_set, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    

          

class PayModePieDashboardViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []
    queryset = PosTaud.objects.filter().order_by('-pk')

    
    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).order_by('-pk').first()
            site = fmspw.loginsite
            today_date = date.today()
            # print(today_date,"today_date")
            yesterday = today_date - timedelta(days = 1)
            # print(yesterday,"yesterday")
            
            dt = datetime.datetime.strptime(str(today_date), '%Y-%m-%d')
            start = dt - timedelta(days=dt.weekday())
            
            startWeek = str(start).split(" ")[0]
            # print(startWeek,"startWeek")
            end = start + timedelta(days=6)
            endWeek = str(end).split(" ")[0]
            # print(endWeek,"endWeek")

            start_date = start - timedelta(days=7)
            laststartWeek = str(start_date).split(" ")[0]
            # print(laststartWeek,"laststartWeek")
            end_date = end - timedelta(days=7)
            lastendWeek = str(end_date).split(" ")[0]
            # print(lastendWeek,"lastendWeek")
           
           

            k_type = self.request.GET.get('type',None)
            if not k_type:
                raise Exception("Please Give Type!!")

            data = [];text = ""
            gt1_ids = Paytable.objects.filter(gt_group='GT1',pay_isactive=True).order_by('-pk') 
            gt1_lst = list(set([i.pay_code for i in gt1_ids if i.pay_code]))
            # print(gt1_lst,"gt1_lst")

            if k_type == 'today':
                text = "Today's Collection by Paymode"
                taud_salesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
                pay_type__in=gt1_lst).order_by('-pk').values('pay_type').order_by('-pay_type').annotate(name=F('pay_desc'),color=F('pay_typeid__pay_color'),y=Count('pay_desc'),z=Sum('pay_amt'),percent=ExpressionWrapper(Sum('pay_amt') * Count('pay_desc') / 100, output_field=FloatField())).order_by('-y')
                
                data = list(taud_salesids)
            elif k_type == 'yesterday':
                text = "Yesterday's Collection by Paymode"
                
                taud_salesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=yesterday,
                pay_type__in=gt1_lst).order_by('-pk').values('pay_type').order_by('-pay_type').annotate(name=F('pay_desc'),color=F('pay_typeid__pay_color'),y=Count('pay_desc'),z=Sum('pay_amt'),percent=ExpressionWrapper(Sum('pay_amt') * Count('pay_desc') / 100, output_field=FloatField())).order_by('-y')
                
                data = list(taud_salesids)

            elif k_type == 'thisweek': 
                text = "This Week's Collection by Pay Mode" 
                taud_salesids = PosTaud.objects.filter(sa_date__date__gte=startWeek,sa_date__date__lte=endWeek,itemsite_code=site.itemsite_code,
                pay_type__in=gt1_lst).order_by('-pk').values('pay_desc').order_by('-pay_desc').annotate(name=F('pay_desc'),color=F('pay_typeid__pay_color'),y=Count('pay_desc'),z=Sum('pay_amt'),percent=ExpressionWrapper(Sum('pay_amt') * Count('pay_desc') / 100, output_field=FloatField())).order_by('-y')
                
                data = list(taud_salesids)

                
            elif k_type == 'lastweek':
                text = "Last Week's Collection by Pay Mode"  
                taud_salesids = PosTaud.objects.filter(sa_date__date__gte=laststartWeek,sa_date__date__lte=lastendWeek,itemsite_code=site.itemsite_code,
                pay_type__in=gt1_lst).order_by('-pk').values('pay_desc').order_by('-pay_desc').annotate(name=F('pay_desc'),color=F('pay_typeid__pay_color'),y=Count('pay_desc'),z=Sum('pay_amt'),percent=ExpressionWrapper(Sum('pay_amt') * Count('pay_desc') / 100, output_field=FloatField())).order_by('-y')
                
                data = list(taud_salesids)
            elif k_type == 'thismonth': 
                text = "This Month's Collection by Pay Mode" 
                taud_salesids = PosTaud.objects.filter(sa_date__month=today_date.month,sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                pay_type__in=gt1_lst).order_by('-pk').values('pay_desc').order_by('-pay_desc').annotate(name=F('pay_desc'),color=F('pay_typeid__pay_color'),y=Count('pay_desc'),z=Sum('pay_amt'),percent=ExpressionWrapper(Sum('pay_amt') * Count('pay_desc') / 100, output_field=FloatField())).order_by('-y')
                
                data = list(taud_salesids)
              
            elif k_type == 'lastmonth':
                text = "Last Month's Collection by Pay Mode"
                taud_salesids = PosTaud.objects.filter(sa_date__month=today_date.month-1,sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                pay_type__in=gt1_lst).order_by('-pk').values('pay_desc').order_by('-pay_desc').annotate(name=F('pay_desc'),color=F('pay_typeid__pay_color'),y=Count('pay_desc'),z=Sum('pay_amt'),percent=ExpressionWrapper(Sum('pay_amt') * Count('pay_desc') / 100, output_field=FloatField())).order_by('-y')
                
                data = list(taud_salesids)
                
               
            elif k_type == 'ytd':  
                text = "Yearly's Collection by Pay Mode" 
                taud_salesids = PosTaud.objects.filter(sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                pay_type__in=gt1_lst).order_by('-pk').values('pay_desc').order_by('-pay_desc').annotate(name=F('pay_desc'),color=F('pay_typeid__pay_color'),y=Count('pay_desc'),z=Sum('pay_amt'),percent=ExpressionWrapper(Sum('pay_amt') * Count('pay_desc') / 100, output_field=FloatField())).order_by('-y')
                
                data = list(taud_salesids)
            elif k_type == 'lastyear': 
                text = "Last Year's Collection by Pay Mode" 
                taud_salesids = PosTaud.objects.filter(sa_date__year=today_date.year-1,itemsite_code=site.itemsite_code,
                pay_type__in=gt1_lst).order_by('-pk').values('pay_desc').order_by('-pay_desc').annotate(name=F('pay_desc'),color=F('pay_typeid__pay_color'),y=Count('pay_desc'),z=Sum('pay_amt'),percent=ExpressionWrapper(Sum('pay_amt') * Count('pay_desc') / 100, output_field=FloatField())).order_by('-y')
                data = list(taud_salesids) 
                  
            
                      
            chartData = {
                'chart': {
                    'plotBackgroundColor': None,
                    'plotBorderWidth': None,
                    'plotShadow': False,
                    'type': "pie",
                },
                'title': {
                    'text': text,
                },
                'tooltip': {
                    'pointFormat': 
                        "<b>count: {point.y}</b><br/>" + "<b>Amount($): {point.z:.2f}</b>",
                },
                'accessibility': {
                    'point': {
                        'valueSuffix': "%",
                    }
                },
                'plotOptions':{
                    'pie':{
                        'allowPointSelect':True,
                        'innerSize':"40%",
                        'cursor':"pointer",
                        'dataLabels':{
                        'enabled':True,
                        'format':"<b>{point.name}</b>: {point.percent:.2f} %",
                        },
                    },
                },
                'series': [
                    {
                        'name': "Count",
                        'colorByPoint': True,
                        'data': data
                    },
                ],
                },

            
            # print(chartData,"chartData")
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data':  chartData}
            return Response(data=result, status=status.HTTP_200_OK)  
         
        
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


    @action(detail=False, methods=['get'], name='piedivision')
    def piedivision(self, request):
        try: 
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).order_by('-pk').first()
            site = fmspw.loginsite
            today_date = date.today()
            # print(today_date,"today_date")
            yesterday = today_date - timedelta(days = 1)
            # print(yesterday,"yesterday")
            
            dt = datetime.datetime.strptime(str(today_date), '%Y-%m-%d')
            start = dt - timedelta(days=dt.weekday())
            
            startWeek = str(start).split(" ")[0]
            # print(startWeek,"startWeek")
            end = start + timedelta(days=6)
            endWeek = str(end).split(" ")[0]
            # print(endWeek,"endWeek")

            start_date = start - timedelta(days=7)
            laststartWeek = str(start_date).split(" ")[0]
            # print(laststartWeek,"laststartWeek")
            end_date = end - timedelta(days=7)
            lastendWeek = str(end_date).split(" ")[0]
            # print(lastendWeek,"lastendWeek")
           
           

            k_type = self.request.GET.get('type',None)
            if not k_type:
                raise Exception("Please Give Type!!")

            div_ids = ItemDiv.objects.filter(itm_isactive=True).order_by('-itm_seq')
            # print(div_ids,"div_ids")

            data = [];text = ""

            if k_type == 'today':
                text = "Today's Collection by Division"
                for i in div_ids:
                    div_salesids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
                    dt_itemnoid__item_div=i.itm_code).order_by('-pk').values('dt_itemnoid__item_div'
                    ).annotate(name=F('dt_itemnoid__Item_Divid__itm_desc'),color=F('dt_itemnoid__Item_Divid__pay_color'),y=Count('dt_itemnoid__Item_Divid__itm_desc')).order_by('-y')
                
                    data.extend(list(div_salesids))
            elif k_type == 'yesterday':
                text = "Yesterday's Collection by Division"
                
                for i in div_ids:
                    div_salesids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=yesterday,
                    dt_itemnoid__item_div=i.itm_code).order_by('-pk').values('dt_itemnoid__item_div'
                    ).annotate(name=F('dt_itemnoid__Item_Divid__itm_desc'),color=F('dt_itemnoid__Item_Divid__pay_color'),y=Count('dt_itemnoid__Item_Divid__itm_desc')).order_by('-y')
                
                    data.extend(list(div_salesids))

            elif k_type == 'thisweek': 
                text = "This Week's Collection by Division"
               

                for i in div_ids:
                    # print(i,"iithisweek")
                    div_salesids = PosDaud.objects.filter(sa_date__date__gte=startWeek,sa_date__date__lte=endWeek,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_div=i.itm_code).order_by('-pk').values('dt_itemnoid__item_div'
                    ).annotate(name=F('dt_itemnoid__Item_Divid__itm_desc'),color=F('dt_itemnoid__Item_Divid__pay_color'),y=Count('dt_itemnoid__Item_Divid__itm_desc')).order_by('-y')
                    # print(div_salesids,"div_salesids")
                    data.extend(list(div_salesids))

                
            elif k_type == 'lastweek':
                text = "Last Week's Collection by Division"
                for i in div_ids:
                    div_salesids = PosDaud.objects.filter(sa_date__date__gte=laststartWeek,sa_date__date__lte=lastendWeek,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_div=i.itm_code).order_by('-pk').values('dt_itemnoid__item_div'
                    ).annotate(name=F('dt_itemnoid__Item_Divid__itm_desc'),color=F('dt_itemnoid__Item_Divid__pay_color'),y=Count('dt_itemnoid__Item_Divid__itm_desc')).order_by('-y')
                
                    data.extend(list(div_salesids))

            elif k_type == 'thismonth': 
                text = "This Month's Collection by Division"

                for i in div_ids:
                    # print(i,"ii")
                    div_salesids = PosDaud.objects.filter(sa_date__month=today_date.month,sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_div=i.itm_code).order_by('-pk').values('dt_itemnoid__item_div'
                    ).annotate(name=F('dt_itemnoid__Item_Divid__itm_desc'),color=F('dt_itemnoid__Item_Divid__pay_color'),y=Count('dt_itemnoid__Item_Divid__itm_desc')).order_by('-y')
                    # print(div_salesids,"div_salesids")
                    data.extend(list(div_salesids))

               
            elif k_type == 'lastmonth':
                text = "Last Month's Collection by Division"

                for i in div_ids:
                    # print(i,"div_ids")
                    div_salesids = PosDaud.objects.filter(sa_date__month=today_date.month-1,sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_div=i.itm_code).order_by('-pk').values('dt_itemnoid__item_div'
                    ).annotate(name=F('dt_itemnoid__Item_Divid__itm_desc'),color=F('dt_itemnoid__Item_Divid__pay_color'),y=Count('dt_itemnoid__Item_Divid__itm_desc')).order_by('-y')
                    # print(div_salesids,"div_salesids")
                    data.extend(list(div_salesids))

               
            elif k_type == 'ytd':  
                text = "Yearly's Collection by Division"
                for i in div_ids:
                    # print(i,"ii")
                    div_salesids = PosDaud.objects.filter(sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_div=i.itm_code).order_by('-pk').values('dt_itemnoid__item_div'
                    ).annotate(name=F('dt_itemnoid__Item_Divid__itm_desc'),color=F('dt_itemnoid__Item_Divid__pay_color'),y=Count('dt_itemnoid__Item_Divid__itm_desc')).order_by('-y')
                
                    data.extend(list(div_salesids))

               
            elif k_type == 'lastyear': 
                text = "Last Year's Collection by Division"
                
                for i in div_ids:
                    div_salesids = PosDaud.objects.filter(sa_date__year=today_date.year-1,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_div=i.itm_code).order_by('-pk').values('dt_itemnoid__item_div'
                    ).annotate(name=F('dt_itemnoid__Item_Divid__itm_desc'),color=F('dt_itemnoid__Item_Divid__pay_color'),y=Count('dt_itemnoid__Item_Divid__itm_desc')).order_by('-y')
                
                    data.extend(list(div_salesids))

                        

            chartData = {
                'chart': {
                    'plotBackgroundColor': None,
                    'plotBorderWidth': None,
                    'plotShadow': False,
                    'type': "pie",
                },
                'title': {
                    'text': text,
                },
                'tooltip': {
                    'pointFormat': 
                        "<b>count: {point.y}</b><br/>" + "<b>Amount($): {point.z:.2f}</b>",
                },
                'accessibility': {
                    'point': {
                        'valueSuffix': "%",
                    }
                },
                'plotOptions':{
                    'pie':{
                        'allowPointSelect':True,
                        'innerSize':"40%",
                        'cursor':"pointer",
                        'dataLabels':{
                        'enabled':True,
                        'format':"<b>{point.name}</b>: {point.percent:.2f} %",
                        },
                    },
                },
                'series': [
                    {
                        'name': "Count",
                        'colorByPoint': True,
                        'data': data
                    },
                ],
                },

            
            # print(chartData,"chartData")
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data':  chartData}
            return Response(data=result, status=status.HTTP_200_OK)  
            
        except Exception as e:
          invalid_message = str(e)
          return general_error_response(invalid_message)


    @action(detail=False, methods=['get'], name='piedepartment')
    def piedepartment(self, request):
        try: 
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).order_by('-pk').first()
            site = fmspw.loginsite
            today_date = date.today()
            # print(today_date,"today_date")
            yesterday = today_date - timedelta(days = 1)
            # print(yesterday,"yesterday")
            
            dt = datetime.datetime.strptime(str(today_date), '%Y-%m-%d')
            start = dt - timedelta(days=dt.weekday())
            
            startWeek = str(start).split(" ")[0]
            # print(startWeek,"startWeek")
            end = start + timedelta(days=6)
            endWeek = str(end).split(" ")[0]
            # print(endWeek,"endWeek")

            start_date = start - timedelta(days=7)
            laststartWeek = str(start_date).split(" ")[0]
            # print(laststartWeek,"laststartWeek")
            end_date = end - timedelta(days=7)
            lastendWeek = str(end_date).split(" ")[0]
            # print(lastendWeek,"lastendWeek")
           
           

            k_type = self.request.GET.get('type',None)
            if not k_type:
                raise Exception("Please Give Type!!")

            dept_ids = ItemDept.objects.filter(is_service=True, itm_status=True).order_by('-pk')
            # print(dept_ids,"dept_ids")

            data = [];text = ""

            if k_type == 'today':
                text = "Today's Collection by Department"
                for i in dept_ids:
                    dep_salesids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
                    dt_itemnoid__item_dept=i.itm_code).order_by('-pk').values('dt_itemnoid__item_dept'
                    ).annotate(name=F('dt_itemnoid__Item_Deptid__itm_desc'),color=F('dt_itemnoid__Item_Deptid__pay_color'),y=Count('dt_itemnoid__item_dept')).order_by('-y')
                
                    data.extend(list(dep_salesids))

            elif k_type == 'yesterday':
                text = "Yesterday's Collection by Department"
                
                for i in dept_ids:
                    div_salesids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=yesterday,
                    dt_itemnoid__item_dept=i.itm_code).order_by('-pk').values('dt_itemnoid__item_dept'
                    ).annotate(name=F('dt_itemnoid__Item_Deptid__itm_desc'),color=F('dt_itemnoid__Item_Deptid__pay_color'),y=Count('dt_itemnoid__item_dept')).order_by('-y')
                
                    data.extend(list(div_salesids))

            elif k_type == 'thisweek': 
                text = "This Week's Collection by Department"

                for i in dept_ids:
                    div_salesids = PosDaud.objects.filter(sa_date__date__gte=startWeek,sa_date__date__lte=endWeek,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_dept=i.itm_code).order_by('-pk').values('dt_itemnoid__item_dept',
                    ).annotate(name=F('dt_itemnoid__Item_Deptid__itm_desc'),color=F('dt_itemnoid__Item_Deptid__pay_color'),y=Count('dt_itemnoid__item_dept')).order_by('-y')
                
                    data.extend(list(div_salesids))

                
            elif k_type == 'lastweek':
                text = "Last Week's Collection by Department"
                for i in dept_ids:
                    div_salesids = PosDaud.objects.filter(sa_date__date__gte=laststartWeek,sa_date__date__lte=lastendWeek,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_dept=i.itm_code).order_by('-pk').values('dt_itemnoid__item_dept'
                    ).annotate(name=F('dt_itemnoid__Item_Deptid__itm_desc'),color=F('dt_itemnoid__Item_Deptid__pay_color'),y=Count('dt_itemnoid__item_dept')).order_by('-y')
                
                    data.extend(list(div_salesids))

            elif k_type == 'thismonth': 
                text = "This Month's Collection by Department"

                for i in dept_ids:
                    div_salesids = PosDaud.objects.filter(sa_date__month=today_date.month,sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_dept=i.itm_code).order_by('-pk').values('dt_itemnoid__item_dept'
                    ).annotate(name=F('dt_itemnoid__Item_Deptid__itm_desc'),color=F('dt_itemnoid__Item_Deptid__pay_color'),y=Count('dt_itemnoid__item_dept')).order_by('-y')
                
                    data.extend(list(div_salesids))

               
            elif k_type == 'lastmonth':
                text = "Last Month's Collection by Department"

                for i in dept_ids:
                    div_salesids = PosDaud.objects.filter(sa_date__month=today_date.month-1,sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_dept=i.itm_code).order_by('-pk').values('dt_itemnoid__item_dept'
                    ).annotate(name=F('dt_itemnoid__Item_Deptid__itm_desc'),color=F('dt_itemnoid__Item_Deptid__pay_color'),y=Count('dt_itemnoid__item_dept')).order_by('-y')
                
                    data.extend(list(div_salesids))

               
            elif k_type == 'ytd':  
                text = "Yearly's Collection by Department"
                for i in dept_ids:
                    # print(i,"i.itm_code")
                    div_salesids = PosDaud.objects.filter(sa_date__year=today_date.year,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_dept=i.itm_code).order_by('-pk').values('dt_itemnoid__item_dept'
                    ).annotate(name=F('dt_itemnoid__Item_Deptid__itm_desc'),color=F('dt_itemnoid__Item_Deptid__pay_color'),y=Count('dt_itemnoid__item_dept')).order_by('-y')
                    # print(div_salesids,"div_salesids")
                    data.extend(list(div_salesids))

               
            elif k_type == 'lastyear': 
                text = "Last Year's Collection by Department"
                
                for i in dept_ids:
                    div_salesids = PosDaud.objects.filter(sa_date__year=today_date.year-1,itemsite_code=site.itemsite_code,
                    dt_itemnoid__item_dept=i.itm_code).order_by('-pk').values('dt_itemnoid__item_dept'
                    ).annotate(name=F('dt_itemnoid__Item_Deptid__itm_desc'),color=F('dt_itemnoid__Item_Deptid__pay_color'),y=Count('dt_itemnoid__item_dept')).order_by('-y')
                
                    data.extend(list(div_salesids))
        

            chartData = {
                'chart': {
                    'plotBackgroundColor': None,
                    'plotBorderWidth': None,
                    'plotShadow': False,
                    'type': "pie",
                },
                'title': {
                    'text': text,
                },
                'tooltip': {
                    'pointFormat': 
                        "<b>count: {point.y}</b><br/>" + "<b>Amount($): {point.z:.2f}</b>",
                },
                'accessibility': {
                    'point': {
                        'valueSuffix': "%",
                    }
                },
                'plotOptions':{
                    'pie':{
                        'allowPointSelect':True,
                        'innerSize':"40%",
                        'cursor':"pointer",
                        'dataLabels':{
                        'enabled':True,
                        'format':"<b>{point.name}</b>: {point.percent:.2f} %",
                        },
                    },
                },
                'series': [
                    {
                        'name': "Count",
                        'colorByPoint': True,
                        'data': data
                    },
                ],
                },

            
            # print(chartData,"chartData")
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data':  chartData}
            return Response(data=result, status=status.HTTP_200_OK)  
            
        except Exception as e:
          invalid_message = str(e)
          return general_error_response(invalid_message)     
               
        

# class PayModePieDashboardViewset(viewsets.ModelViewSet):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]
#     serializer_class = []
#     queryset = []

    
#     def list(self, request):
#         try:
#             fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
#             site = fmspw[0].loginsite
#             k_type = self.request.GET.get('type',None)
#             if not k_type:
#                 raise Exception("Please Give Type!!")

#             data = [];text = ""
#             if k_type == 'today':
#                 text = "Collection by Today Pay Mode"
#                 data = [
#                         {
#                         'name': "Chrome",
#                         'y': 61.41,
#                         'sliced': True,
#                         'selected': True,
#                         },
#                         {
#                         'name': "Internet Explorer",
#                         'y': 11.84,
#                         },
#                         {
#                         'name': "Firefox",
#                         'y': 10.85,
#                         },
#                         {
#                         'name': "Edge",
#                         'y': 4.67,
#                         },
#                         {
#                         'name': "Safari",
#                         'y': 4.18,
#                         },
#                     ]
#             elif k_type == 'yesterday':  
#                 text = "Collection by Yesterday Pay Mode"
#                 data = [
#                         {
#                         'name': "Cash",
#                         'y': 34.41,
#                         'sliced': True,
#                         'selected': True,
#                         },
#                         {
#                         'name': "Card",
#                         'y': 10.84,
#                         },
#                         {
#                         'name': "Master",
#                         'y': 9.85,
#                         },
#                         {
#                         'name': "Visa",
#                         'y': 14.67,
#                         },
#                         {
#                         'name': "Credit",
#                         'y': 40.18,
#                         },
#                     ]
#             elif k_type == 'thisweek':  
#                 text = "Collection by This Week Pay Mode"
#                 data = [
#                         {
#                         'name': "PAYPAL",
#                         'y': 14.41,
#                         'sliced': True,
#                         'selected': True,
#                         },
#                         {
#                         'name': "BDAY VOUCHER",
#                         'y': 8.84,
#                         },
#                         {
#                         'name': "CAPITOL VOUCHER",
#                         'y': 19.85,
#                         },
#                         {
#                         'name': "DIANPING",
#                         'y': 4.67,
#                         },
#                         {
#                         'name': "SELETAR VOUCHER",
#                         'y': 10.18,
#                         },
#                     ]
#             elif k_type == 'lastweek':  
#                 text = "Collection by Last Week Pay Mode"
#                 data = [
#                         {
#                         'name': "HILLION VOUCHER",
#                         'y': 6.41,
#                         'sliced': True,
#                         'selected': True,
#                         },
#                         {
#                         'name': "WECHAT",
#                         'y': 5.84,
#                         },
#                         {
#                         'name': "OUTSTANDING",
#                         'y': 17.85,
#                         },
#                         {
#                         'name': "CHARGE",
#                         'y': 12.67,
#                         },
#                         {
#                         'name': "ASIAMALLVC",
#                         'y': 7.18,
#                         },
#                     ]
#             elif k_type == 'thismonth': 
#                 text = "Collection by This Month Pay Mode" 
#                 data = [
#                         {
#                         'name': "AMARA SETTLEMENT",
#                         'y': '13.41',
#                         'sliced': True,
#                         'selected': True,
#                         },
#                         {
#                         'name': "NOVOTEL SETTLEMENT",
#                         'y': 14.84,
#                         },
#                         {
#                         'name': "ACTIVEPASS",
#                         'y': 10.85,
#                         },
#                         {
#                         'name': "SC24",
#                         'y': 18.67,
#                         },
#                         {
#                         'name': "SC12",
#                         'y': 17.18,
#                         },
#                     ]
#             elif k_type == 'lastmonth':  
#                 text = "Collection by Last Month Pay Mode" 
#                 data = [
#                         {
#                         'name': "SC06",
#                         'y': 10.41,
#                         'sliced': True,
#                         'selected': True,
#                         },
#                         {
#                         'name': "JCB",
#                         'y': 11.84,
#                         },
#                         {
#                         'name': "KFIT",
#                         'y': 7.85,
#                         },
#                         {
#                         'name': "CASH VOUCHER",
#                         'y': 12.67,
#                         },
#                         {
#                         'name': "FOC VOUCHER",
#                         'y': 10.18,
#                         },
#                     ]
#             elif k_type == 'ytd':  
#                 text = "Collection by This Year Pay Mode" 
#                 data = [
#                         {
#                         'name': "CONCOURSE CARD",
#                         'y': 12.41,
#                         'sliced': True,
#                         'selected': True,
#                         },
#                         {
#                         'name': "DEAL",
#                         'y': 13.84,
#                         },
#                         {
#                         'name': "OLD BILL",
#                         'y': 14.85,
#                         },
#                         {
#                         'name': "IPP INSTALLMENT PLAN",
#                         'y': 15.67,
#                         },
#                         {
#                         'name': "TRANSFER Account",
#                         'y': 18.18,
#                         },
#                     ]        
#             elif k_type == 'lastyear':  
#                 text = "Collection by Last Year Pay Mode" 
#                 data = [
#                         {
#                         'name': "GMARKET",
#                         'y': 14.41,
#                         'sliced': True,
#                         'selected': True,
#                         },
#                         {
#                         'name': "BONUS POINT",
#                         'y': 17.84,
#                         },
#                         {
#                         'name': "PREPAID",
#                         'y': 16.85,
#                         },
#                         {
#                         'name': "GROUPON",
#                         'y': 19.67,
#                         },
#                         {
#                         'name': "VANIDAY",
#                         'y': 18.18,
#                         },
#                     ]         
            
#             chartData = {
#                         'chart': {
#                             'plotBackgroundColor': None,
#                             'plotBorderWidth': None,
#                             'plotShadow': False,
#                             'type': "pie",
#                         },
#                         'title': {
#                             'text': text,
#                         },
#                         'tooltip': {
#                             'pointFormat': "{series.name}: <b>{point.percentage:.1f}%</b>",
#                         },
#                         'accessibility': {
#                             'point': {
#                             'valueSuffix': "%",
#                             },
#                         },     
#                         'plotOptions': {
#                             'pie': {
#                             'allowPointSelect': True,
#                             'innerSize': "40%",
#                             'cursor': "pointer",
#                             'dataLabels': {
#                                 'enabled': True,
#                                 'format': "<b>{point.name}</b>: {point.percentage:.1f} %",
#                             },
#                             },
#                         },
#                         'series': [
#                             {
#                             'name': "",
#                             'colorByPoint': True,
#                             'data': data
#                             },
#                         ],
#                         },
#             result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
#             'data':  chartData}
#             return Response(data=result, status=status.HTTP_200_OK)  
        
#         except Exception as e:
#             invalid_message = str(e)
#             return general_error_response(invalid_message)    

class PrepaidAccountListAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    # serializer_class = PrepaidAccountListSerializer
    serializer_class = []

    def list(self, request):
        try:
           
            query_set = PrepaidAccount.objects.filter(status=True).values('cust_code').order_by('cust_code'
            ).annotate(qty=Count('pp_no'),cust_name=F('cust_name'),pp_amt=Sum('pp_amt'),
            pp_total=Sum('pp_total'),remain=Sum('remain'))
            # print(query_set,"query_set")

            q = self.request.GET.get('search',None)

            if q is not None:
                query_set = PrepaidAccount.objects.filter(status=True).filter(Q(cust_name__icontains=q) 
                | Q(cust_code__icontains=q)).values('cust_code').order_by('cust_code'
                ).annotate(qty=Count('cust_code'),cust_name=F('cust_name'),pp_amt=Sum('pp_amt'),
                pp_total=Sum('pp_total'),remain=Sum('remain'))

            if query_set:
                full_tot = query_set.count()
                try:
                    limit = int(request.GET.get("limit",10))
                except:
                    limit = 10
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(query_set, limit)
                total_page = paginator.num_pages

                try:
                    queryset = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page

                # print(queryset,"queryset") 
                # print(queryset.object_list,"object_list") 
               
                # serializer = self.get_serializer(queryset, many=True)
                # print(serializer.data,"serializer")
                resData = {
                    'dataList': queryset.object_list,
                    'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
                    }
                }
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  resData}
                v = result.get('data')
                d = v.get("dataList")
                for dat in d:
                    dat["pp_amt"] = "{:.2f}".format(float(dat['pp_amt']))
                    dat["pp_total"] = "{:.2f}".format(float(dat['pp_total']))
                    dat["remain"] = "{:.2f}".format(float(dat['remain']))
                       
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    

    
class TreatmentOpenListAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:
            query_set = Treatment.objects.filter(status='Open').values('course','cust_code').order_by('course'
            ).annotate(qty=Count('status'),cust_name=F('cust_name'),unit_amount=Sum('unit_amount'))
            q = self.request.GET.get('search',None)

            if q is not None:
                query_set = Treatment.objects.filter(status='Open').filter(Q(cust_name__icontains=q) 
                | Q(cust_code__icontains=q)).values('course','cust_code').order_by('course'
                ).annotate(qty=Count('status'),cust_name=F('cust_name'),unit_amount=Sum('unit_amount'))

                        
            if query_set:
                full_tot = query_set.count()
                try:
                    limit = int(request.GET.get("limit",10))
                except:
                    limit = 10
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(query_set, limit)
                total_page = paginator.num_pages

                try:
                    queryset = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page

                # serializer = self.get_serializer(queryset, many=True)
                resData = {
                    'dataList': queryset.object_list,
                    'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
                    }
                }
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  resData}
                v = result.get('data')
                d = v.get("dataList")
                for dat in d:
                    dat["unit_amount"] = "{:.2f}".format(float(dat['unit_amount']))
                       
            
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    

class TreatmentDoneListAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:
            query_set = Treatment.objects.filter(status='Done').values('course','cust_code').order_by('course'
            ).annotate(qty=Count('status'),cust_name=F('cust_name'),unit_amount=Sum('unit_amount'))    
            q = self.request.GET.get('search',None)

            if q is not None: 
                query_set = Treatment.objects.filter(status='Done').filter(Q(cust_name__icontains=q) 
                | Q(cust_code__icontains=q)).values('course','cust_code').order_by('course'
                ).annotate(qty=Count('status'),cust_name=F('cust_name'),unit_amount=Sum('unit_amount'))    
                  
            if query_set:
                full_tot = query_set.count()
                try:
                    limit = int(request.GET.get("limit",10))
                except:
                    limit = 10
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(query_set, limit)
                total_page = paginator.num_pages
                print(total_page,"total_page")
                try:
                    queryset = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page

                # serializer = self.get_serializer(queryset, many=True)
                resData = {
                    'dataList': queryset.object_list,
                    'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
                    }
                }
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  resData}
                v = result.get('data')
                d = v.get("dataList")
                for dat in d:
                    dat["unit_amount"] = "{:.2f}".format(float(dat['unit_amount']))
                       
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


class VoucherAccListAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:
            query_set =  VoucherRecord.objects.filter(isvalid=True).values('cust_code').order_by('cust_code'
            ).annotate(qty=Count('cust_code'),cust_name=F('cust_name'),value=Sum('value'))

            q = self.request.GET.get('search',None)

            if q is not None: 
                query_set =  VoucherRecord.objects.filter(isvalid=True).filter(Q(cust_name__icontains=q) 
                | Q(cust_code__icontains=q)).values('cust_code').order_by('cust_code'
                ).annotate(qty=Count('cust_code'),cust_name=F('cust_name'),value=Sum('value'))


            if query_set:
                full_tot = query_set.count()
                try:
                    limit = int(request.GET.get("limit",10))
                except:
                    limit = 10
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(query_set, limit)
                total_page = paginator.num_pages

                try:
                    queryset = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page

                # serializer = self.get_serializer(queryset, many=True)
                resData = {
                    'dataList': queryset.object_list,
                    'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
                    }
                }
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  resData}
                v = result.get('data')
                d = v.get("dataList")
                for dat in d:
                    dat["value"] = "{:.2f}".format(float(dat['value']))
                       
            
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    

class HoldItemListAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:
            query_set =  Holditemdetail.objects.filter(status='OPEN').values('sa_custno').order_by('sa_custno'
            ).annotate(sa_custname=F('sa_custname'),qty=Count('status'),hi_amt=Sum('hi_amt'),
            hi_qty=Sum('hi_qty'),holditemqty=Sum('holditemqty'))
            q = self.request.GET.get('search',None)

            if q is not None: 
                query_set =  Holditemdetail.objects.filter(status='OPEN').filter(Q(sa_custname__icontains=q) 
                | Q(sa_custno__icontains=q)).values('sa_custno').order_by('sa_custno'
                ).annotate(sa_custname=F('sa_custname'),qty=Count('sa_custno'),hi_amt=Sum('hi_amt'),
                hi_qty=Sum('hi_qty'),holditemqty=Sum('holditemqty'))
                        
            if query_set:
                full_tot = query_set.count()
                try:
                    limit = int(request.GET.get("limit",10))
                except:
                    limit = 10
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(query_set, limit)
                total_page = paginator.num_pages

                try:
                    queryset = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page

                # serializer = self.get_serializer(queryset, many=True)
                resData = {
                    'dataList': queryset.object_list,
                    'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
                    }
                }
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  resData}
                v = result.get('data')
                d = v.get("dataList")
                for dat in d:
                    dat["hi_amt"] = "{:.2f}".format(float(dat['hi_amt']))
                       
            
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


class CreditNoteListAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def list(self, request):
        try:
            query_set =  CreditNote.objects.filter(status='OPEN').values('cust_code').order_by('cust_code'
            ).annotate(cust_name=F('cust_name'),qty=Count('status'),amount=Sum('amount'),
            balance=Sum('balance'))
            q = self.request.GET.get('search',None)

            if q is not None: 
                query_set =  CreditNote.objects.filter(status='OPEN').filter(Q(cust_code__icontains=q) 
                | Q(cust_name__icontains=q)).values('cust_code').order_by('cust_code'
                ).annotate(cust_name=F('cust_name'),qty=Count('cust_code'),amount=Sum('amount'),
                balance=Sum('balance'))

                        
            if query_set:
                full_tot = query_set.count()
                try:
                    limit = int(request.GET.get("limit",10))
                except:
                    limit = 10
                try:
                    page = int(request.GET.get("page",1))
                except:
                    page = 1

                paginator = Paginator(query_set, limit)
                total_page = paginator.num_pages

                try:
                    queryset = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page

                # serializer = self.get_serializer(queryset, many=True)
                resData = {
                    'dataList': queryset.object_list,
                    'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
                    }
                }
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  resData}
                v = result.get('data')
                d = v.get("dataList")
                for dat in d:
                    dat["amount"] = "{:.2f}".format(float(dat['amount']))
                    dat["balance"] = "{:.2f}".format(float(dat['balance']))
                       
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


class VoucherPromoViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = VoucherPromo.objects.filter(isactive=True).order_by('-pk')
    serializer_class = VoucherPromoSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        queryset = VoucherPromo.objects.filter(isactive=True).order_by('-pk')
       
        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = VoucherPromoSerializer
            
            queryset = self.filter_queryset(self.get_queryset())

            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    @transaction.atomic
    def create(self, request):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite

                if not 'voucher_desc' in request.data or not request.data['voucher_desc']:
                    raise Exception('Please give voucher desc!!.') 
                
                if not 'sms_text' in request.data or not request.data['sms_text']:
                    raise Exception('Please give sms text!!.')

                if not 'price' in request.data or not request.data['price']:
                    raise Exception('Please give price!!.') 

                # if not 'isdiscount' in request.data or request.data['isdiscount'] is not None:
                #     raise Exception('Please give isdiscount !!.') 
                
                # if not 'conditiontype1' in request.data or not request.data['conditiontype1']:
                #     raise Exception('Please give conditiontype1!!.')

                # if not 'conditiontype2' in request.data or not request.data['conditiontype2']:
                #     raise Exception('Please give conditiontype2!!.')     
     
                check_ids = VoucherPromo.objects.filter(voucher_desc=request.data['voucher_desc']).order_by('-pk')
                if check_ids:
                    msg = "VoucherPromo {0} this voucher desc already record exist!!".format(str(request.data['voucher_desc']))
                    raise Exception(msg) 

                # vcheck_ids = VoucherPromo.objects.filter(price=request.data['price'],
                # isdiscount=request.data['isdiscount'],conditiontype1=request.data['conditiontype1'],
                # conditiontype2=request.data['conditiontype2']).order_by('-pk')
                # if vcheck_ids:
                #     msg = "VoucherPromo {0} this price,discount,conditiontype1 & 2 already record exist!!".format(str(request.data['conditiontype1']))
                #     raise Exception(msg) 
                       
               
                serializer = VoucherPromoSerializer(data=request.data)
                if serializer.is_valid():
                    control_obj = ControlNo.objects.filter(control_description__iexact="VoucherPromo").first()
                    if not control_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"VoucherPromo Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    vo_code = str(control_obj.control_no)
                    
                    k = serializer.save(voucher_code=vo_code)
                    if k:
                        control_obj.control_no = int(control_obj.control_no) + 1
                        control_obj.save()
                    
                    result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                    'error': False}
                    return Response(result, status=status.HTTP_201_CREATED)
                

                data = serializer.errors

                if 'non_field_errors' in data:
                    message = data['non_field_errors'][0]
                else:
                    first_key = list(data.keys())[0]
                    message = str(first_key)+":  "+str(data[first_key][0])

                result = {'status': status.HTTP_400_BAD_REQUEST,"message":message,
                'error': True, 'data': serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         

    @transaction.atomic
    def partial_update(self, request, pk=None):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
                site = fmspw.loginsite
                ref = self.get_object(pk)
                if not 'voucher_desc' in request.data or not request.data['voucher_desc']:
                    raise Exception('Please give voucher desc!!.') 
                
                if not 'sms_text' in request.data or not request.data['sms_text']:
                    raise Exception('Please give sms text!!.') 

                if not 'price' in request.data or not request.data['price']:
                    raise Exception('Please give price!!.') 
         
                check_ids = VoucherPromo.objects.filter(~Q(pk=ref.pk)).filter(voucher_desc=request.data['voucher_desc']).order_by('-pk')
                if check_ids:
                    msg = "VoucherPromo {0} this voucher desc already record exist!!".format(str(request.data['voucher_desc']))
                    raise Exception(msg) 
                    
                serializer = self.get_serializer(ref, data=request.data, partial=True)
                if serializer.is_valid():
                
                    serializer.save()
                    
                    result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)

                
                data = serializer.errors

                if 'non_field_errors' in data:
                    message = data['non_field_errors'][0]
                else:
                    first_key = list(data.keys())[0]
                    message = str(first_key)+":  "+str(data[first_key][0])

                result = {'status': status.HTTP_400_BAD_REQUEST,"message":message,
                'error': True, 'data': serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   
    
    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            pro = self.get_object(pk)
            serializer = VoucherPromoSerializer(pro, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


   
    def destroy(self, request, pk=None):
        try:
            request.data["isactive"] = False
            ref = self.get_object(pk)
            serializer = VoucherPromoSerializer(ref, data=request.data ,partial=True)
            state = status.HTTP_204_NO_CONTENT
            if serializer.is_valid():
                serializer.save()
                result = {'status': status.HTTP_200_OK,"message":"Deleted Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)
            
            # print(serializer.errors,"jj")
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",
            'error': True,'data': serializer.errors }
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          


    def get_object(self, pk):
        try:
            return VoucherPromo.objects.get(pk=pk)
        except VoucherPromo.DoesNotExist:
            raise Exception('VoucherPromo Does not Exist') 
    

    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def addvoucher(self, request): 
        try:  
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
                site = fmspw.loginsite
                if 'sa_transacno' not in request.data or not request.data['sa_transacno']:
                    raise Exception('Please give sa transacno!!.') 
                
                if 'voucherpromo_id' not in request.data or not request.data['voucherpromo_id']:
                    raise Exception('Please give voucherpromo id!!.') 
                satransacno = request.data['sa_transacno']
                hdr = PosHaud.objects.filter(sa_transacno=satransacno).only('sa_transacno').order_by("-pk").first()
                if not hdr:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud ID does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                vopr_obj = VoucherPromo.objects.filter(isactive=True,pk=request.data['voucherpromo_id']).order_by('-pk').first()
                if not vopr_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucherpromo id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
                
                vorecontrolobj = ControlNo.objects.filter(control_description__iexact="Public Voucher",Site_Codeid__pk=fmspw.loginsite.pk).first()
                if not vorecontrolobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher Record Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                voucher_code = str(vorecontrolobj.control_prefix)+str(vorecontrolobj.Site_Codeid.itemsite_code)+str(vorecontrolobj.control_no)
                cust_obj = hdr.sa_custnoid  

                ex_ids = VoucherRecord.objects.filter(sa_transacno=satransacno,voucher_name=vopr_obj.voucher_desc)  
                if ex_ids:
                    raise Exception('This Voucher Promo already given for this customer account invoice !!')
                
                vo_rec = VoucherRecord(sa_transacno=satransacno,voucher_name=vopr_obj.voucher_desc,
                voucher_no=voucher_code,value="{:.2f}".format(float(vopr_obj.price)) if vopr_obj.price else 0,
                cust_codeid=cust_obj,cust_code=cust_obj.cust_code,
                cust_name=cust_obj.cust_name,percent=0,site_codeid=site,site_code=site.itemsite_code,
                issued_expiry_date=None,issued_staff=fmspw.Emp_Codeid.emp_code,
                onhold=0,paymenttype=None,remark=None,type_code=vorecontrolobj.control_prefix,used=0,
                ref_fullvoucherno=None,ref_rangefrom=None,ref_rangeto=None,site_allocate=None,dt_lineno=1,
                isdiscount=vopr_obj.isdiscount,conditiontype1=vopr_obj.conditiontype1,
                conditiontype2=vopr_obj.conditiontype2)
                vo_rec.save()
                vo_rec.sa_date = hdr.sa_date
                vo_rec.save()

                if vo_rec.pk:
                    vorecontrolobj.control_no = int(vorecontrolobj.control_no) + 1
                    vorecontrolobj.save()

              
                # client = Client(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)
                # # receiver = cust_obj.cust_phone2
                # receiver = "8124042939"
                # message = client.messages.create(
                #         body=vopr_obj.sms_text,
                #         from_=SMS_SENDER,
                #         to=receiver
                #     )   

                sms_process = SmsProcessLog(sms_username=fmspw.pw_userlogin,
                sms_phone=cust_obj.cust_phone2,sms_msg=vopr_obj.sms_text,
                sms_datetime=datetime.datetime.now(),send_datetime=datetime.datetime.now(),
                site_code=site.itemsite_code,vendor_type=4,isactive=1,sms_task_number=1,
                sms_portno=0,sms_sendername=fmspw.pw_userlogin,sms_campaignname="webfe voucher sms",
                sms_scheduleid=0,sms_type='Immediately'  )

               
                sms_process.save() 
                                            

                    
                result = {'status': status.HTTP_200_OK,"message":"Voucher Added Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)                
 



       

    
    
        
 
       


       
