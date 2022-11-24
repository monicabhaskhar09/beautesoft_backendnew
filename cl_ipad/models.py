from operator import mod
from xml.dom.minidom import Document
from django.db import models, transaction
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User, Group
from django.db.models import F
from django.utils import timezone
from cl_app.models import ItemSitelist

# Create your models here.

class WebConsultation_Hdr(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    doc_no = models.CharField(db_column='DocNo', max_length=255, blank=True, null=True)
    cust_code = models.CharField(db_column='CustCode', max_length=255, blank=True, null=True)
    cust_codeid = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True) 
    site_code = models.CharField(db_column='Site_Code', max_length=50, null=True, blank=True)  # Field name made lowercase.
    site_codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT,  null=True)
    doc_date = models.DateTimeField(db_column='DocDate', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(default=True)
    consultant_code = models.CharField(db_column='Consultant_Code', max_length=50, null=True, blank=True)  # Field name made lowercase.
    emp_codeid   = models.ForeignKey('cl_table.Employee', on_delete=models.PROTECT, null=True) #, null=True
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'WebConsultation_Hdr'
        # unique_together = [['cust_code','site_code','consultant_code','doc_date']]

    def __str__(self):
        return str(self.doc_no)   


class WebConsultation_Question(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    question_group = models.CharField(db_column='QuestionGroup', max_length=200, blank=True, null=True)
    question_number = models.IntegerField(db_column='QuestionNumber', blank=True, null=True)  # Field name made lowercase.
    page_number = models.IntegerField(db_column='PageNumber', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(default=True)
    question_type = models.IntegerField(db_column='QuestionType', blank=True, null=True)  # Field name made lowercase.
    image = models.ImageField(db_column='image', blank=True, null=True,upload_to='img')  # Field name made lowercase. 
    question_english = models.CharField(db_column='QuestionEnglish', max_length=500, blank=True, null=True)
    question_chinese = models.CharField(db_column='QuestionChinese', max_length=500, blank=True, null=True)
    question_others = models.CharField(db_column='QuestionOthers', max_length=500, blank=True, null=True)
    site_ids = models.ManyToManyField('cl_app.ItemSitelist',blank=True)

    class Meta:
        db_table = 'WebConsultation_Question'

    def __str__(self):
        return str(self.question_group)   
