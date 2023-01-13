from django.db import models
from cl_table.models import (Employee)
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from custom.models import EmpLevel,SalarySubTypeLookup,ModeOfPayment


# Create your models here.
class Employee_Salary(models.Model):

    SA_STATUS = [
        ("New", "New"),
        ("Open", "Open"),
        ("Posted", "Posted"),
    ]


    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    empid = models.ForeignKey(Employee, on_delete=models.PROTECT,blank=True,null=True)
    emp_name = models.CharField(db_column='Emp_name', max_length=600, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=100, blank=True, null=True)
    basicsalary = models.FloatField(db_column='basicsalary',blank=True, null=True)
    hourlysalhour = models.FloatField(db_column='hourlySalHour', blank=True, null=True)  # Field name made lowercase.
    hourlysalrate = models.FloatField(db_column='hourlySalRate', blank=True, null=True)  # Field name made lowercase.
    firstovertimerate = models.FloatField(db_column='firstOverTimeRate', blank=True, null=True)  # Field name made lowercase.
    firstovertimehour = models.FloatField(db_column='firstOverTimeHour', blank=True, null=True)  # Field name made lowercase.
    secondovertimehour = models.FloatField(db_column='secondOverTimeHour', blank=True, null=True)  # Field name made lowercase.
    secondovertimerate = models.FloatField(db_column='secondOverTimeRate', blank=True, null=True)  # Field name made lowercase.
    tototpay = models.FloatField(db_column='totOTPay', blank=True, null=True)  # Field name made lowercase.
    totcommission = models.FloatField(db_column='totCommission', blank=True, null=True)  # Field name made lowercase.
    totallowance = models.FloatField(db_column='totAllowance', blank=True, null=True)  # Field name made lowercase.
    totdeduct = models.FloatField(db_column='totDeduct', blank=True, null=True)  # Field name made lowercase.
    addpay = models.FloatField(db_column='AddPay', blank=True, null=True)  # Field name made lowercase.
    netpay = models.FloatField(db_column='netPay', blank=True, null=True)  # Field name made lowercase.
    empcpfcont = models.FloatField(db_column='empCPFCont', blank=True, null=True)  # Field name made lowercase.
    dateofpay = models.DateField(blank=True, null=True)
    modeofPayid =  models.ForeignKey('custom.ModeOfPayment', on_delete=models.PROTECT,blank=True,null=True)   
    salarystatus = models.CharField(max_length=250,choices=SA_STATUS, null=True, blank=True,default="New")
    salarymonth = models.CharField(db_column='salarly_month', max_length=100, blank=True, null=True)
    from_date =  models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    # isactive = models.BooleanField(db_column='isactive',default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

   

    class Meta:
        db_table = 'Employee_Salary'

    def __str__(self):
        return str(self.emp_name)   
 

class AllowanceList(models.Model):
    
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    emp_salaryid  = models.ForeignKey(Employee_Salary, on_delete=models.PROTECT,blank=True,null=True) 
    desc = models.TextField(null=True)
    type_nameid = models.ForeignKey('custom.SalarySubTypeLookup', on_delete=models.PROTECT,null=True)
    amount = models.FloatField(db_column='amount', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'AllowanceList'

    def __str__(self):
        return str(self.desc)   


class DeductionList(models.Model):
    
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    emp_salaryid  = models.ForeignKey(Employee_Salary, on_delete=models.PROTECT,blank=True,null=True) 
    desc = models.TextField(null=True)
    type_nameid = models.ForeignKey('custom.SalarySubTypeLookup', on_delete=models.PROTECT,null=True)
    amount = models.FloatField(db_column='amount', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'DeductionList'

    def __str__(self):
        return str(self.desc)


class PaymentList(models.Model):
    
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    emp_salaryid  = models.ForeignKey(Employee_Salary, on_delete=models.PROTECT,blank=True,null=True) 
    desc = models.TextField(null=True)
    type_nameid = models.ForeignKey('custom.SalarySubTypeLookup', on_delete=models.PROTECT,null=True)
    amount = models.FloatField(db_column='amount', blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        db_table = 'PaymentList'

    def __str__(self):
        return str(self.desc)




