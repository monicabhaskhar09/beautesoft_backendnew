from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import (EmployeeSalarySerializer)
from .models import (Employee_Salary,AllowanceList,DeductionList,PaymentList)
from cl_table.models import(Fmspw,Employee,Title)
# from cl_app.models import ItemSitelist, SiteGroup
from custom.models import SalarySubTypeLookup,ModeOfPayment
from cl_table.serializers import EmpLevel
from datetime import date, timedelta, datetime
import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import math
from rest_framework import serializers
from rest_framework.views import APIView
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from Cl_beautesoft.settings import EMAIL_HOST_USER, PDF_ROOT
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives, get_connection
from io import BytesIO
from rest_framework.decorators import action
from django.utils.html import strip_tags
from django.template.loader import get_template
import pdfkit
from rest_framework import generics
from pyvirtualdisplay import Display
from reportlab.pdfgen import canvas
from django.core.files.storage import default_storage
from Cl_beautesoft import settings
import os
import os.path
import tempfile
from django.db.models import Sum
from django.db.models import Count
from cl_app.permissions import authenticated_only
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions
from cl_app.utils import general_error_response
from Cl_beautesoft.settings import BASE_DIR
from django.db.models import Q
import string
from cl_table.authentication import ExpiringTokenAuthentication
import re
from dateutil.relativedelta import relativedelta
from rest_framework.decorators import api_view
from django.template.defaulttags import register
from django.db import transaction, connection
from django.db.models.functions import RowNumber, Coalesce
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout, get_user_model



# Create your views here.

class EmployeeSalaryViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Employee_Salary.objects.filter().order_by('-pk')
    serializer_class = EmployeeSalarySerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        month = self.request.GET.get('month',0)
        # print(month,"month")
        if month != 0:
            month = date.today().month

        # print(month,"month")   

        year = self.request.GET.get('year',0)
        if year != 0:
            year = date.today().year

        # print(year,"year")

        site_code = self.request.GET.get('site_code',None) 
        if not site_code:
            site_code = site.itemsite_code
        
        # print(site_code,"site_code") 
        active = self.request.GET.get('active',None)
        # print(active,"active")
        emplevel = self.request.GET.get('emplevel',None)
        # print(emplevel,"emplevel")
        status = self.request.GET.get('status',None)
        # print(status,"status")
        q = self.request.GET.get('search',None)
        # print(q,"QQ")
        queryset = Employee_Salary.objects.filter().order_by('-pk')
        # print(queryset,"queryset")
       
        if month:
            # print("month")
            queryset = Employee_Salary.objects.filter(from_date__month=month).order_by('-pk')
        if year:
            # print("year")
            queryset = queryset.filter(from_date__year=year).order_by('-pk')

        if site_code:
            # print("sitecode")
            queryset = queryset.filter(site_code=site_code).order_by('-pk')

        if active:
            # print("active")
            queryset = queryset.filter(empid__emp_isactive=active).order_by('-pk')
        if emplevel:
            # print("emplevel")
            level_obj = EmpLevel.objects.filter(pk=emplevel).first()
            if level_obj:
                queryset = queryset.filter(empid__EMP_TYPEid__pk=level_obj.pk).order_by('-pk')
        if status:
            # print("status")
            queryset = queryset.filter(salarystatus=status).order_by('-pk')

        if q is not None:
            # print("QQ ser")
            queryset = queryset.filter(Q(empid__emp_name__icontains=q)).order_by('-pk')
    
        # print("else")    

        return queryset


    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            serializer_class = EmployeeSalarySerializer
            queryset = self.filter_queryset(self.get_queryset())
            
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
                except (EmptyPage, InvalidPage):
                    queryset = paginator.page(total_page) # last page

                # print(queryset,"queryset")    
                data_list= [];totallowancelist = [];totdeductionlist=[];addpaymentlist=[]
                for allquery in queryset:


                    allow_ids = AllowanceList.objects.filter(emp_salaryid__pk=allquery.pk).order_by('-pk')
                    # print(allow_ids,"allow_ids")
                    if allow_ids:
                        totallowancelist = [{'allow_id':i.pk,'desc': i.desc,
                        'type': i.type_nameid.pk if i.type_nameid  else "",
                        'typeName': i.type_nameid.typename if i.type_nameid and i.type_nameid.typename else "", 
                        'amount': "{:.2f}".format(float(i.amount))} for i in allow_ids]
                    
                    deduction_ids = DeductionList.objects.filter(emp_salaryid__pk=allquery.pk).order_by('-pk')
                    if deduction_ids:
                        totdeductionlist = [{'deduct_id': i.pk,'desc': i.desc,
                        'type': i.type_nameid.pk if i.type_nameid  else "",
                        'typeName': i.type_nameid.typename if i.type_nameid and i.type_nameid.typename else "", 
                        'amount': "{:.2f}".format(float(i.amount))} for i in deduction_ids]

                    addpaymen_ids = PaymentList.objects.filter(emp_salaryid__pk=allquery.pk).order_by('-pk')
                    if addpaymen_ids:
                        addpaymentlist = [{'pay_id': i.pk,'desc': i.desc,
                        'type': i.type_nameid.pk if i.type_nameid  else "",
                        'typeName': i.type_nameid.typename if i.type_nameid and i.type_nameid.typename else "", 
                        'amount': "{:.2f}".format(float(i.amount))} for i in addpaymen_ids]
    
                    
                    title = Title.objects.filter(product_license=site.itemsite_code).first()
                    data_list.append({
                        "payrollId": allquery.pk,
                        "empid": allquery.empid.pk,
                        "EmpName": allquery.empid.emp_name if allquery.empid and allquery.empid.emp_name else "",
                        "EmpCode": allquery.empid.emp_code if allquery.empid and allquery.empid.emp_code else "",
                        'FromDate': datetime.datetime.strptime(str(allquery.from_date),'%Y-%m-%d').strftime('%Y-%m-%d') if allquery.from_date else "",
                        'toDate': datetime.datetime.strptime(str(allquery.to_date), '%Y-%m-%d').strftime('%Y-%m-%d') if allquery.to_date else "",
                        "nric": allquery.empid.emp_nric if allquery.empid and allquery.empid.emp_nric else "",
                        'site_code': allquery.site_code,
                        'emp_level_id': allquery.empid.EMP_TYPEid.pk if allquery.empid and allquery.empid.EMP_TYPEid else "", 
                        'emp_level_name': allquery.empid.EMP_TYPEid.level_desc if allquery.empid and allquery.empid.EMP_TYPEid else "", 
                        'BasicSalary': allquery.basicsalary ,
                        'salarystatus': allquery.salarystatus,
                        'checkbox': False,
                        'hourlySalHour': allquery.hourlysalhour,
                        'hourlySalRate': allquery.hourlysalrate,
                        'firstOverTimeRate': allquery.firstovertimerate,
                        'firstOverTimeHour': allquery.firstovertimehour,
                        'totOTPay': allquery.tototpay,
                        'totCommission': allquery.totcommission,
                        'totAllowance': allquery.totallowance,
                        'totDeduct': allquery.totdeduct,
                        'AddPay': allquery.addpay,
                        'netPay': allquery.netpay,
                        'empCPFCont': allquery.empcpfcont,
                        'dateofPay': datetime.datetime.strptime(str(allquery.dateofpay), '%Y-%m-%d').strftime('%Y-%m-%d') if allquery.dateofpay else "",
                        'modeofPayId_text': allquery.modeofPayid.modename if allquery.modeofPayid and allquery.modeofPayid.modename else "",
                        'modeofPay': allquery.modeofPayid.pk if allquery.modeofPayid else "",
                        'secondOverTimeHour': allquery.secondovertimehour,
                        'secondOverTimeRate': allquery.secondovertimerate,
                        'TotAllowanceList': totallowancelist,
                        'TotDeductionList': totdeductionlist,
                        'AddPaymentList': addpaymentlist,
                        'company_name': title.trans_h1 if title and title.trans_h1 else '', 
                        
                    })        
                    
                resData = {
                    'printData': data_list,
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
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   


    @transaction.atomic
    def create(self, request):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).order_by('-pk')
                site = fmspw[0].loginsite
                # print(request.data,"request.data")

                empsl_ids = Employee_Salary.objects.filter(from_date__lt=request.data['toDate'],
                to_date__gt=request.data['FromDate'],empid__pk=request.data['empid'],
                site_code=site.itemsite_code).order_by('-pk')
                # print(empsl_ids,"empsl_ids")

                if not empsl_ids:
                 
                    serializer = EmployeeSalarySerializer(data=request.data)
                    if serializer.is_valid():
                        # print("jjj")
                        emp_obj = Employee.objects.filter(pk=request.data['empid']).order_by('-pk').first()
                        # print(emp_obj,"emp_obj")
                        if not emp_obj:
                            raise Exception("Employee does not exist!!")
                        
                        smonth = date.today().month
                        if 'FromDate' in request.data: 
                            # print(smonth,"smonth")
                            if request.data['FromDate'] is not None:
                                # print("iff")
                                smonth = datetime.datetime.strptime(str(request.data['FromDate']),'%Y-%m-%d').strftime("%m")
                        
                        modeofpay_obj = ModeOfPayment.objects.none()
                        # print(modeofpay_obj,"modeofpay_obj")
                        if 'modeofPay' in request.data and request.data['modeofPay'] and int(request.data['modeofPay']) != 0:
                            modeofpay_obj = ModeOfPayment.objects.filter(pk=request.data['modeofPay']).order_by('-pk').first()
                            if not modeofpay_obj:
                                raise Exception("ModeOfPayment does not exist!!")


                        # print(smonth,"smonth")
                        k = serializer.save(emp_name=emp_obj.emp_name,
                        site_code=site.itemsite_code,salarymonth=smonth,from_date=request.data['FromDate'],
                        to_date=request.data['toDate'],basicsalary=request.data['BasicSalary'],
                        hourlysalhour=request.data['hourlySalHour'],hourlysalrate=request.data['hourlySalRate'],
                        firstovertimerate=request.data['firstOverTimeRate'],firstovertimehour=request.data['firstOverTimeHour'],
                        tototpay=request.data['totOTPay'],totcommission=request.data['totCommission'],
                        totallowance=request.data['totAllowance'],totdeduct=request.data['totDeduct'],
                        addpay=request.data['AddPay'],
                        netpay=request.data['netPay'],empcpfcont=request.data['empCPFCont'],
                        dateofpay=request.data['dateofPay'],
                        secondovertimehour=request.data['secondOverTimeHour'],secondovertimerate=request.data['secondOverTimeRate'],
                        modeofPayid=modeofpay_obj if modeofpay_obj else None,salarystatus="New")
                        # print("JIOOOOOOOOOOOOOOOO",k)
                        
                        allowancelst_ids = request.data.pop('TotAllowanceList')
                        # print(allowancelst_ids,"allowancelst_ids")
                        if allowancelst_ids != []:
                            for i in allowancelst_ids:
                                if 'allow_id' in i and  i['allow_id'] == None:
                                    lookup_ids = SalarySubTypeLookup.objects.filter(pk=i['type']).first()
                                    # {
                                    #     desc: "deducdesc",
                                    #     type: 1,
                                    #     typeName: "totdeductype1",
                                    #     amount: 200,
                                    # },
                                    if lookup_ids:
                                        AllowanceList(emp_salaryid=k,desc= i['desc'],
                                        type_nameid=lookup_ids,
                                        # type_name= i['typeName'],
                                        amount=i['amount']).save()
                        
                        deductlst_ids = request.data.pop('TotDeductionList')
                        # print(deductlst_ids,"deductlst_ids")
                        if deductlst_ids != []:
                            for j in deductlst_ids:
                                if 'deduct_id' in j and  j['deduct_id'] == None:
                                    slookup_ids = SalarySubTypeLookup.objects.filter(pk=j['type']).first()
                                    if slookup_ids:
                                        DeductionList(emp_salaryid=k,desc= j['desc'],
                                        type_nameid=slookup_ids,
                                        # type_name= j['typeName'],
                                        amount=j['amount']).save()
                        
                        paymentlst_ids = request.data.pop('AddPaymentList')
                        # print(paymentlst_ids,"paymentlst_ids")
                        if paymentlst_ids != []:
                            for l in paymentlst_ids:
                                if 'pay_id' in l and l['pay_id'] == None:
                                    salookup_ids = SalarySubTypeLookup.objects.filter(pk=l['type']).first()
                                    if salookup_ids:
                                        PaymentList(emp_salaryid=k,desc= l['desc'],
                                        type_nameid=salookup_ids,
                                        # type_name= l['typeName'],
                                        amount=l['amount']).save()
                    
                                    

                        result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                        'error': False}
                        return Response(result, status=status.HTTP_201_CREATED)
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee Salary Already Exists!!",
                    'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)


                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
                'error': True, 'data': serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
    
    def get_object(self, pk):
        try:
            return Employee_Salary.objects.get(pk=pk)
        except Employee_Salary.DoesNotExist:
            raise Exception('Employee Salary Record does not exist') 

   
    def retrieve(self, request, pk=None):
        try:
            empsalry = self.get_object(pk)
            serializer = EmployeeSalarySerializer(empsalry, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Sucessfully",
            'error': False, 'data': serializer.data} 
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
            

    def partial_update(self, request, pk=None):
        try:
            with transaction.atomic():
                obj = self.get_object(pk)
                # print(obj,"obj")
                requestData = request.data
                # print(requestData,"requestData")

                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).order_by('-pk')
                site = fmspw[0].loginsite
                # print(request.data,"request.data")

                serializer = EmployeeSalarySerializer(obj,data=requestData,partial=True)
                if serializer.is_valid():
                    # print("jjj")
                    emp_obj = Employee.objects.filter(pk=request.data['empid']).order_by('-pk').first()
                    # print(emp_obj,"emp_obj")
                    if not emp_obj:
                        raise Exception("Employee does not exist!!")
                    
                    smonth = date.today().month
                    if 'FromDate' in request.data: 
                        # print(smonth,"smonth")
                        if request.data['FromDate'] is not None:
                            # print("iff")
                            smonth = datetime.datetime.strptime(str(request.data['FromDate']),'%Y-%m-%d').strftime("%m")
                    
                    modeofpay_obj = None
                    # print(modeofpay_obj,"modeofpay_obj")
                    if 'modeofPay' in request.data and request.data['modeofPay']:
                        # print("iff")
                        modeofpay_obj = ModeOfPayment.objects.filter(pk=request.data['modeofPay']).order_by('-pk').first()
                        # print(modeofpay_obj,"modeofpay_obj") 
                        if not modeofpay_obj:
                            raise Exception("ModeOfPayment does not exist!!")

                    
                    
                    # print(smonth,"smonth")
                    k = serializer.save(emp_name=emp_obj.emp_name,empid=emp_obj,
                    site_code=site.itemsite_code,salarymonth=smonth,from_date=request.data['FromDate'],
                    to_date=request.data['toDate'],basicsalary=request.data['BasicSalary'],
                    hourlysalhour=request.data['hourlySalHour'],hourlysalrate=request.data['hourlySalRate'],
                    firstovertimerate=request.data['firstOverTimeRate'],firstovertimehour=request.data['firstOverTimeHour'],
                    tototpay=request.data['totOTPay'],totcommission=request.data['totCommission'],
                    totallowance=request.data['totAllowance'],totdeduct=request.data['totDeduct'],
                    addpay=request.data['AddPay'],
                    netpay=request.data['netPay'],empcpfcont=request.data['empCPFCont'],
                    dateofpay=request.data['dateofPay'],
                    modeofPayid=modeofpay_obj if modeofpay_obj else None,salarystatus="Open",
                    secondovertimehour=request.data['secondOverTimeHour'],secondovertimerate=request.data['secondOverTimeRate'],
                    )
                    # print("JIOOOOOOOOOOOOOOOO",k)
                    
                    allowancelst_ids = request.data.pop('TotAllowanceList')
                    # print(allowancelst_ids,"allowancelst_ids")
                    if allowancelst_ids != []:
                        var = [i['allow_id'] for i in allowancelst_ids if i['allow_id']]
                        # print(var,"var")
                        allown_ids = list(set(AllowanceList.objects.filter(emp_salaryid=k).order_by('-pk').values_list('pk',flat=True).distinct()))
                        # print(allown_ids,"allown_ids")
                        comp = list(set(allown_ids) - set(var))
                        # print(comp,"comp")
                        AllowanceList.objects.filter(pk__in=comp).delete()

                        for i in allowancelst_ids:
                            if 'type' in i and i['type']:
                                salookup_ids = SalarySubTypeLookup.objects.filter(pk=i['type']).first()
                                # print(salookup_ids,"salookup_ids")
                                if salookup_ids:
                                    if 'allow_id' in i and i['allow_id'] == None:
                                        c = AllowanceList(emp_salaryid=k,desc= i['desc'],
                                        type_nameid=salookup_ids,
                                        amount="{:.2f}".format(float(i['amount'])))
                                        # print(c,"c")
                                        c.save()
                                    else:
                                        if 'allow_id'in i and  i['allow_id']:
                                            AllowanceList.objects.filter(id=i['allow_id']).update(
                                            desc= i['desc'],type_nameid=salookup_ids,
                                            amount="{:.2f}".format(float(i['amount']))
                                            )
                                        
                       
                    deductlst_ids = request.data.pop('TotDeductionList')
                    # print(deductlst_ids,"deductlst_ids")
                    if deductlst_ids != []:
                        vard = [i['deduct_id'] for i in deductlst_ids if i['deduct_id']]
                        deductf_ids = list(set(DeductionList.objects.filter(emp_salaryid=k).order_by('-pk').values_list('pk',flat=True).distinct()))
                        compd = list(set(deductf_ids) - set(vard))
                        DeductionList.objects.filter(pk__in=compd).delete()
 
                        for j in deductlst_ids:
                            if 'type' in j and j['type']:
                                sa_lookup_ids = SalarySubTypeLookup.objects.filter(pk=j['type']).first()
                                if sa_lookup_ids:
                                    if 'deduct_id' in j and j['deduct_id'] == None:
                                        g= DeductionList(emp_salaryid=k,desc= j['desc'],type_nameid= sa_lookup_ids,
                                        amount="{:.2f}".format(float(j['amount']))
                                        )
                                        g.save()
                                       
                                    else:
                                        if 'deduct_id' in j and  j['deduct_id']:
                                            DeductionList.objects.filter(id=j['deduct_id']).update(
                                                desc=j['desc'],type_nameid=sa_lookup_ids,
                                                amount="{:.2f}".format(float(j['amount']))
                                                )

                       
                    
                    paymentlst_ids = request.data.pop('AddPaymentList')
                    # print(paymentlst_ids,"paymentlst_ids")
                    if paymentlst_ids != []:
                        varp = [i['pay_id'] for i in paymentlst_ids if i['pay_id']]
                        paylist_ids = list(set(PaymentList.objects.filter(emp_salaryid=k).order_by('-pk').values_list('pk',flat=True).distinct()))
                        compp = list(set(paylist_ids) - set(varp))
                        PaymentList.objects.filter(pk__in=compp).delete()
  
                        
                        for l in paymentlst_ids:
                            if 'type' in l and  l['type']:
                                salookupp_ids = SalarySubTypeLookup.objects.filter(pk=l['type']).first()
                                if salookupp_ids:
                                    if 'pay_id' in l and l['pay_id'] == None:
                                        pay = PaymentList(emp_salaryid=k,desc= l['desc'],
                                        type_nameid= salookupp_ids,
                                        amount="{:.2f}".format(float(l['amount']))
                                        )
                                        # print(pay,"pp")
                                        pay.save()
                                       
                                    else:
                                        if 'pay_id' in l and l['pay_id']:
                                            PaymentList.objects.filter(id=l['pay_id']).update(desc=l['desc'],
                                            type_nameid=salookupp_ids,amount="{:.2f}".format(float(l['amount']))
                                            )


                       
                    result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)
      
                result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "fail", 'error': True, "data": serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
    

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def postselected(self, request, pk=None):
        try:
            empsal = self.get_object(pk)  
            serializer = EmployeeSalarySerializer(empsal, data=request.data, partial=True, context={'request': self.request})
            if serializer.is_valid():
                if empsal.salarystatus == "Open":
                    serializer.save(salarystatus="Posted")
                else:
                    raise Exception("Can't Able to move posted status!!")

                result = {'status': status.HTTP_200_OK,"message":"Post Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            data = serializer.errors
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


    @transaction.atomic
    @action(detail=False, methods=['POST'], name='postselectedlist',
    permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def postselectedlist(self, request):
        try:
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
                if request.data.get('post_ids') is None and request.data.get('post_ids') == []:
                    raise Exception("Select checkbox before post selected button!!")
                
                # print(request.data.get('post_ids'),"request.data.get('post_ids')")
                empsal_ids = Employee_Salary.objects.filter(pk__in=request.data.get('post_ids'),
                salarystatus='Open').order_by('-pk').update(salarystatus='Posted') 
                if empsal_ids:
                    result = {'status': status.HTTP_200_OK,"message":"Updated Posted List Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Selected payslip are not in Open status!!",'error': False}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

              

   