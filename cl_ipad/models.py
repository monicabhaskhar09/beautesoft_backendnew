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
    signature = models.ImageField(db_column='Signature', blank=True, null=True,upload_to='img')  # Field name made lowercase.

    class Meta:
        db_table = 'WebConsultation_Hdr'
        # unique_together = [['cust_code','site_code','consultant_code','doc_date']]

    def __str__(self):
        return str(self.doc_no)   

class WebConsultation_Dtl(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    doc_no = models.CharField(db_column='DocNo', max_length=255, blank=True, null=True)
    question_number = models.CharField(db_column='questionNumber', max_length=10, null=True, blank=True)  # Field name made lowercase.
    answer = models.IntegerField(db_column='answer', null=True, blank=True)  # Field name made lowercase.
    answer_text = models.CharField(db_column='answerText', max_length=200, null=True, blank=True)  # Field name made lowercase.
    subquestion_number = models.CharField(db_column='subquestionNumber', max_length=10, null=True, blank=True)  # Field name made lowercase.
    image = models.ImageField(db_column='image', max_length=255, blank=True, null=True,upload_to='img')  # Field name made lowercase. 
    pic_data1 = models.TextField(blank=True, null=True)
    page_number = models.IntegerField(db_column='PageNumber', blank=True, null=True)  # Field name made lowercase.


    
    class Meta:
        db_table = 'WebConsultation_Dtl'

    def __str__(self):
        return str(self.doc_no)   


class WebConsultation_Question(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    question_group = models.CharField(db_column='QuestionGroup', max_length=200, blank=True, null=True)
    question_number = models.IntegerField(db_column='QuestionNumber', blank=True, null=True)  # Field name made lowercase.
    page_number = models.IntegerField(db_column='PageNumber', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(default=True)
    question_type = models.CharField(db_column='QuestionType', max_length=500, blank=True, null=True)  # Field name made lowercase.
    image = models.ImageField(db_column='image', blank=True, null=True,upload_to='img')  # Field name made lowercase. 
    question_english = models.CharField(db_column='QuestionEnglish', max_length=500, blank=True, null=True)
    question_chinese = models.CharField(db_column='QuestionChinese', max_length=500, blank=True, null=True)
    question_others = models.CharField(db_column='QuestionOthers', max_length=500, blank=True, null=True)
    site_ids = models.ManyToManyField('cl_app.ItemSitelist',blank=True)
    question_text = models.CharField(db_column='QuestionText',max_length=500,  blank=True, null=True)  # Field name made lowercase.
    option_type = models.IntegerField(db_column='option_type', blank=True, null=True)  # Field name made lowercase.
    mandatory = models.BooleanField(db_column='Mandatory',default=False)
    declaration_text = models.TextField(db_column='Declaration_Text', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        db_table = 'WebConsultation_Question'

    def __str__(self):
        return str(self.question_group) 

class WebConsultation_QuestionMultichoice(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    questionid   = models.ForeignKey('cl_ipad.WebConsultation_Question', on_delete=models.PROTECT, null=True) #, null=True
    choice = models.CharField(db_column='choice', max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'WebConsultation_QuestionMultichoice'

    def __str__(self):
        return str(self.choice)   

class WebConsultation_Questionsub_questions(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    questionid   = models.ForeignKey('cl_ipad.WebConsultation_Question', on_delete=models.PROTECT, null=True) #, null=True
    options = models.CharField(db_column='options', max_length=100, blank=True, null=True)
    sub_question_english = models.CharField(db_column='sub_question_english', max_length=500, blank=True, null=True)
    sub_question_chinese = models.CharField(db_column='sub_question_chinese', max_length=500, blank=True, null=True)
   

    class Meta:
        db_table = 'WebConsultation_Questionsub_questions'

    def __str__(self):
        return str(self.sub_question_english)   

class WebConsultation_AnalysisMaster(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    field_name = models.CharField(db_column='fieldName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    display_field_name = models.CharField(db_column='displayFieldName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    choice_name = models.CharField(db_column='choiceName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)
    header = models.BooleanField(db_column='header',default=False)
    body = models.BooleanField(db_column='body',default=False)
    footer = models.BooleanField(db_column='footer',default=False)
    mandatory = models.BooleanField(db_column='Mandatory',default=False)
    image = models.ImageField(db_column='image', blank=True, null=True,upload_to='img')  # Field name made lowercase. 
    is_image = models.BooleanField(db_column='is_image',default=False)
    seq = models.IntegerField(db_column='Seq', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        db_table = 'WebConsultation_AnalysisMaster'
        # unique_together = [['field_name','display_field_name','choice_name']]

    def __str__(self):
        return str(self.fieldName) 

class WebConsultation_AnalysisResult(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    doc_no = models.CharField(db_column='DocNo', max_length=255)
    cust_code = models.CharField(db_column='CustCode', max_length=255, blank=True, null=True)
    site_code = models.CharField(db_column='SiteCode', max_length=200, null=True, blank=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    cust_weight = models.FloatField(db_column='CustWeight', blank=True, null=True)  # Field name made lowercase.
    cust_height = models.FloatField(db_column='CustHeight', blank=True, null=True)  # Field name made lowercase.
    fat_mass = models.FloatField(db_column='FatMass', blank=True, null=True)  # Field name made lowercase.
    bmi = models.FloatField(db_column='BMI', blank=True, null=True)  # Field name made lowercase.
    target_weight = models.FloatField(db_column='TargetWeight', blank=True, null=True)  # Field name made lowercase.
    must_lose_weight = models.FloatField(db_column='MustLoseWeight', blank=True, null=True)  # Field name made lowercase.
    face_forehead = models.CharField(db_column='FaceForeHead', max_length=500, null=True, blank=True)  # Field name made lowercase.
    face_nosearea = models.CharField(db_column='FaceNoseArea', max_length=500, null=True, blank=True)  # Field name made lowercase.
    face_eyearea = models.CharField(db_column='FaceEyeArea', max_length=500, null=True, blank=True)  # Field name made lowercase.
    face_facearea = models.CharField(db_column='FaceFaceArea', max_length=500, null=True, blank=True)  # Field name made lowercase.
    face_neckarea = models.CharField(db_column='FaceNeckArea', max_length=500, null=True, blank=True)  # Field name made lowercase.
    face_remark = models.CharField(db_column='FaceRemark', max_length=500, null=True, blank=True)  # Field name made lowercase.
    waist_measure = models.FloatField(db_column='WaistMeasure', blank=True, null=True)  # Field name made lowercase.
    waist_remark = models.CharField(db_column='WaistRemark', max_length=500, null=True, blank=True)  # Field name made lowercase.
    tummy_measure = models.FloatField(db_column='TummyMeasure', blank=True, null=True)  # Field name made lowercase.
    tummy_remark = models.CharField(db_column='TummyRemark', max_length=500, null=True, blank=True)  # Field name made lowercase.
    buttock_measure = models.FloatField(db_column='ButtockMeasure', blank=True, null=True)  # Field name made lowercase.
    buttock_remark = models.CharField(db_column='ButtockRemark', max_length=500, null=True, blank=True)  # Field name made lowercase.
    thigh_measure = models.FloatField(db_column='ThighMeasure', blank=True, null=True)  # Field name made lowercase.
    thigh_remark = models.CharField(db_column='ThighRemark', max_length=500, null=True, blank=True)  # Field name made lowercase.
    lower_legmeasure = models.FloatField(db_column='LowerLegMeasure', blank=True, null=True)  # Field name made lowercase.
    lower_legremark = models.CharField(db_column='LowerLegRemark', max_length=500, null=True, blank=True)  # Field name made lowercase.
    arm_measure = models.FloatField(db_column='ArmMeasure', blank=True, null=True)  # Field name made lowercase.
    arm_remark = models.CharField(db_column='ArmRemark', max_length=500, null=True, blank=True)  # Field name made lowercase.
    rounded_shouldermeasure = models.FloatField(db_column='RoundedShoulderMeasure', blank=True, null=True)  # Field name made lowercase.
    rounded_shoulderremark = models.CharField(db_column='RoundedShoulderRemark', max_length=500, null=True, blank=True)  # Field name made lowercase.
    create_date = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
    create_by = models.CharField(db_column='CreateBy', max_length=500, null=True, blank=True)  # Field name made lowercase.
    last_updatedate = models.DateTimeField(db_column='LastUpdateDate', blank=True, null=True)  # Field name made lowercase.
    last_updateby = models.CharField(db_column='LastUpdateBy', max_length=500, null=True, blank=True)  # Field name made lowercase.
    therapist_id = models.CharField(db_column='TherapistID', max_length=500, null=True, blank=True)  # Field name made lowercase.
    image = models.ImageField(db_column='image', max_length=255, blank=True, null=True,upload_to='img')  # Field name made lowercase. 
    pic_data1 = models.TextField(blank=True, null=True)
    image1 = models.ImageField(db_column='image1', max_length=255, blank=True, null=True,upload_to='img')  # Field name made lowercase. 
    pic_data2 = models.TextField(blank=True, null=True)



    class Meta:
        db_table = 'WebConsultation_AnalysisResult'
        unique_together = (('doc_no'),)

    def __str__(self):
        return str(self.doc_no)   

class WebConsultation_Referral(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    cust_code = models.CharField(db_column='CustCode', max_length=255)
    doc_no = models.CharField(db_column='DocNo', max_length=255, blank=True, null=True)
    site_code = models.CharField(db_column='SiteCode', max_length=20, null=True, blank=True)  # Field name made lowercase.
    referral_name = models.CharField(db_column='ReferralName', max_length=255)
    referral_age =  models.IntegerField(db_column='ReferralAge')  # Field name made lowercase.
    referral_contactno = models.CharField(db_column='ReferralContactNo', max_length=255)
    isactive = models.BooleanField(db_column='IsActive',default=True)
    create_date = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
    create_by = models.CharField(db_column='CreateBy', max_length=20, null=True, blank=True)  # Field name made lowercase.
    last_updatedate = models.DateTimeField(db_column='LastUpdateDate', blank=True, null=True)  # Field name made lowercase.
    last_updateby = models.CharField(db_column='LastUpdateBy', max_length=20, null=True, blank=True)  # Field name made lowercase.
    referral_code = models.CharField(db_column='ReferralCode', max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'WebConsultation_Referral'
        # unique_together = (('doc_no'),)

    def __str__(self):
        return str(self.doc_no)


class WebConsultation_Referral_Hdr(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    doc_no = models.CharField(db_column='DocNo', max_length=255) 
    site_code = models.CharField(db_column='SiteCode', max_length=20, null=True, blank=True)  # Field name made lowercase.  
    isactive = models.BooleanField(db_column='IsActive',default=True)
    signature_img = models.ImageField(db_column='SignatureImg', blank=True, null=True,upload_to='img')  # Field name made lowercase.
    welcomedoor_signatureimg = models.ImageField(db_column='WelcomeDoorSignatureImg', blank=True, null=True,upload_to='img')  # Field name made lowercase.  
    create_date = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
    create_by = models.CharField(db_column='CreateBy', max_length=20, null=True, blank=True)  # Field name made lowercase.
    last_updatedate = models.DateTimeField(db_column='LastUpdateDate', blank=True, null=True)  # Field name made lowercase.
    last_updateby = models.CharField(db_column='LastUpdateBy', max_length=20, null=True, blank=True)  # Field name made lowercase.
    
    class Meta:
        db_table = 'WebConsultation_Referral_Hdr'
        # unique_together = (('doc_no'),)

    def __str__(self):
        return str(self.doc_no)

class TNC_Master(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    sno = models.CharField(db_column='SNo', max_length=20, null=True, blank=True)  # Field name made lowercase.  
    isactive = models.BooleanField(db_column='isActive',default=True)
    english = models.CharField(db_column='English', max_length=2000, null=True, blank=True)  # Field name made lowercase.
    otherlanguage = models.CharField(db_column='OtherLanguage', max_length=2000, null=True, blank=True)  # Field name made lowercase.    
    mandatory = models.BooleanField(db_column='Mandatory',null=True)
    is_declaration = models.BooleanField(db_column='Declaration',null=True)
    tnctext1 = models.CharField(db_column='Tnctext1', max_length=500, null=True, blank=True)  # Field name made lowercase.
    tnctext2 = models.CharField(db_column='Tnctext2', max_length=500, null=True, blank=True)  # Field name made lowercase.

    class Meta:
        db_table = 'TNC_Master'
        unique_together = (('english'),)

    def __str__(self):
        return str(self.english)

class TNC_Header(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    tncno = models.CharField(db_column='TNCNo', max_length=20)  # Field name made lowercase.  
    cust_code = models.CharField(db_column='CustCode', max_length=20, null=True, blank=True)
    consultant_code = models.CharField(db_column='ConsultantCode', max_length=20, null=True, blank=True)
    signature1 = models.ImageField(db_column='Signature1', blank=True, null=True,upload_to='img')  # Field name made lowercase.
    signature2 = models.ImageField(db_column='Signature2', blank=True, null=True,upload_to='img')  # Field name made lowercase.
    sign_date = models.DateTimeField(db_column='signDate', blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='ItemSite_Code', max_length=20, null=True, blank=True)  # Field name made lowercase.  

    class Meta:
        db_table = 'TNC_Header'
        unique_together = (('tncno'),)

    def __str__(self):
        return str(self.tncno)

class TNC_Detail(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)
    tncno = models.CharField(db_column='TNCNo', max_length=20, blank=True, null=True)  # Field name made lowercase.  
    receipt_date = models.DateTimeField(db_column='ReceiptDate', blank=True, null=True)  # Field name made lowercase.
    receiptno = models.CharField(db_column='ReceiptNo', max_length=20, blank=True, null=True)  # Field name made lowercase.  
    package = models.CharField(db_column='Package', max_length=80, blank=True, null=True)  # Field name made lowercase.  
    amount = models.DecimalField(db_column='Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo',blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'TNC_Detail'
        # unique_together = (('tncno'),)

    def __str__(self):
        return str(self.tncno)

       