from rest_framework import serializers
from .models import (Employee_Salary,AllowanceList,DeductionList,PaymentList)
# from cl_app.models import ItemSitelist, SiteGroup
# from custom.models import EmpLevel,Room,VoucherRecord
from cl_table.models import Fmspw
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from rest_framework import status
from django.db.models import Q
import datetime
from django.db.models import Count
from django.db.models import Sum
from datetime import date
from django.db.models.functions import Coalesce


class EmployeeSalarySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Employee_Salary
        fields = ['id','empid','emp_name','site_code','basicsalary','salarystatus']


    def to_representation(self, value):
        totallowancelist = [];totdeductionlist =[];addpaymentlist = []
        allow_ids = AllowanceList.objects.filter(emp_salaryid=value.pk).order_by('-pk')
        if allow_ids:
            totallowancelist = [{'allow_id':i.pk,'desc': i.desc,
            'type': i.type_nameid.pk if i.type_nameid  else "",
            'typeName': i.type_nameid.typename if i.type_nameid and i.type_nameid.typename else "", 
            'amount': "{:.2f}".format(float(i.amount))} for i in allow_ids]
                    
        deduction_ids = DeductionList.objects.filter(emp_salaryid=value.pk).order_by('-pk')
        if deduction_ids:
            totdeductionlist = [{'deduct_id': i.pk,'desc': i.desc,
            'type': i.type_nameid.pk if i.type_nameid  else "",
            'typeName': i.type_nameid.typename if i.type_nameid and i.type_nameid.typename else "", 
            'amount': "{:.2f}".format(float(i.amount))} for i in deduction_ids]

            
        addpaymen_ids = PaymentList.objects.filter(emp_salaryid=value.pk).order_by('-pk')
        if addpaymen_ids:
            addpaymentlist = [{'pay_id': i.pk,'desc': i.desc,
            'type': i.type_nameid.pk if i.type_nameid  else "",
            'typeName': i.type_nameid.typename if i.type_nameid and i.type_nameid.typename else "", 
            'amount': "{:.2f}".format(float(i.amount))} for i in addpaymen_ids]
        
       

        mapped_object =    {
                "payrollId": value.pk,
                "empid": value.empid.pk,
                "EmpName": value.empid.emp_name if value.empid and value.empid.emp_name else "",
                "EmpCode": value.empid.emp_code if value.empid and value.empid.emp_code else "",
                'FromDate': datetime.datetime.strptime(str(value.from_date),'%Y-%m-%d').strftime("%Y-%m-%d") if value.from_date else "",
                'toDate': datetime.datetime.strptime(str(value.to_date), '%Y-%m-%d').strftime("%Y-%m-%d") if value.to_date else "",
                "nric": value.empid.emp_nric if value.empid and value.empid.emp_nric else "",
                'site_code': value.site_code,
                'emp_level_id': value.empid.EMP_TYPEid.pk if value.empid and value.empid.EMP_TYPEid else "", 
                'BasicSalary': value.basicsalary,
                'checkbox': False,
                'hourlySalHour': value.hourlysalhour,
                'hourlySalRate': value.hourlysalrate,
                'firstOverTimeRate': value.firstovertimerate,
                'firstOverTimeHour': value.firstovertimehour,
                'totOTPay': value.tototpay,
                'totCommission': value.totcommission,
                'totAllowance': value.totallowance,
                'totDeduct': value.totdeduct,
                'AddPay': value.addpay,
                'netPay': value.netpay,
                'empCPFCont': value.empcpfcont,
                'dateofPay': datetime.datetime.strptime(str(value.dateofpay), '%Y-%m-%d').strftime("%Y-%m-%d") if value.dateofpay else "",
                'modeofPayId_text': value.modeofPayid.modename  if value.modeofPayid else "",
                'modeofPay': value.modeofPayid.pk  if value.modeofPayid else "",
                'secondOverTimeHour': value.secondovertimehour,
                'secondOverTimeRate': value.secondovertimerate,
                'TotAllowanceList': totallowancelist,
                'TotDeductionList': totdeductionlist,
                'AddPaymentList': addpaymentlist,
        }       
      
       
        return mapped_object   



class AllowanceListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Employee_Salary
        fields = ['id','emp_salaryid','desc','type_nameid','amount']
