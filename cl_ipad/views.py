from django.shortcuts import render
from cl_table.authentication import ExpiringTokenAuthentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from cl_app.permissions import authenticated_only
from .serializers import (WebConsultationHdrSerializer,WebConsultationDtlSerializer,WebConsultationQuestionSerializer,
WebConsultation_AnalysisResultSerializer,WebConsultation_ReferralSerializer,
WebConsultation_Referral_HdrSerializer,TransactionCustomerSerializer,
TransactionPosDaudSerializer,TNCMasterSerializer,WebConsultationQuestionMultichoiceSerializer,
TNC_HeaderSerializer,TNC_DetailformSerializer,WebConsultationQuestionsub_questionsSerializer,
WebConsultationQuestionprintSerializer,WebConsultation_AnalysisResultprintSerializer,
WebConsultation_ReferralprintSerializer,WebConsultation_Referral_HdrprintSerializer)
from .models import (WebConsultation_Hdr,WebConsultation_Dtl,WebConsultation_Question,WebConsultation_AnalysisResult,
WebConsultation_Referral,WebConsultation_Referral_Hdr,TNC_Master,TNC_Header,TNC_Detail,
WebConsultation_QuestionMultichoice,WebConsultation_Questionsub_questions)
from cl_table.models import (Fmspw,Employee,ControlNo,Customer,PosHaud,PosDaud,Title)
from rest_framework import status,viewsets,mixins
from rest_framework.response import Response
from custom.views import response, get_client_ip, round_calc
from cl_app.utils import general_error_response
from django.db import transaction, connection
from datetime import timedelta
import datetime
from datetime import date, timedelta
from cl_app.models import ItemSitelist
from django.db.models import Q
from rest_framework.decorators import action
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator, InvalidPage
from Cl_beautesoft.settings import SMS_ACCOUNT_SID, SMS_AUTH_TOKEN, SMS_SENDER, SITE_ROOT
from rest_framework.generics import GenericAPIView, CreateAPIView

# Create your views here.

class WebConsultationHdrViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_Hdr.objects.filter(isactive=True).order_by('-pk')
    serializer_class = WebConsultationHdrSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        cust_id = self.request.GET.get('cust_id',None)
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)
        form_no = self.request.GET.get('form_no',None)
        consultant_id = self.request.GET.get('consultant_id',None)
            
        # if not cust_id:
        #     raise Exception('Please give Customer ID!!') 
            
        queryset = WebConsultation_Hdr.objects.filter(isactive=True,site_codeid=site).order_by('-pk')
        if cust_id:
            queryset = queryset.filter(cust_codeid__pk=cust_id).order_by('-pk')

        if from_date and to_date:
            queryset = queryset.filter(doc_date__date__gte=from_date,doc_date__date__lte=to_date).order_by('-pk')
        
        if form_no:
            queryset = queryset.filter(doc_no__icontains=form_no).order_by('-pk')

        if consultant_id:
            queryset = queryset.filter(emp_codeid__pk=consultant_id).order_by('-pk')
            
       
        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = WebConsultationHdrSerializer
            
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

                if not 'cust_codeid' in request.data or not request.data['cust_codeid']:
                    raise Exception('Please give Customer ID!!.') 

                if not 'emp_codeid' in request.data or not request.data['emp_codeid']:
                    raise Exception('Please give Employee ID!!.') 

                emp_obj = Employee.objects.filter(pk=request.data['emp_codeid'],emp_isactive=True).order_by('-pk').first()    
                if not emp_obj:
                    raise Exception('Employee ID Does not exist!!.') 

                cust_obj = Customer.objects.filter(cust_isactive=True,pk=request.data['cust_codeid']).only('cust_isactive').order_by('-pk').first()        
                if not cust_obj:
                    raise Exception('Customer ID Does not exist!!.') 

                 
               

                # if not 'site_codeid' in request.data or not request.data['site_codeid']:
                #     request.data["site_codeid"] = site.pk
                # else:
                #     if request.data['site_codeid']:
                #         siteobj = ItemSitelist.objects.filter(pk=request.data['site_codeid'],itemsite_isactive=True).first() 
                #         if not siteobj:
                #             result = {'status': status.HTTP_400_BAD_REQUEST,
                #             "message":"ItemSitelist ID does not exist!!",'error': True} 
                #             return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                # if siteobj:
                #     sitev = siteobj
                # else:
                #     sitev = site

                control_obj = ControlNo.objects.filter(control_description__iexact="Web Consultation",
                Site_Codeid__pk=site.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Web Consultation Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                doc_no = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)    
                         

                
                check_ids = WebConsultation_Hdr.objects.filter(site_code=site.itemsite_code,
                cust_codeid=cust_obj,emp_codeid=emp_obj,doc_date__date=date.today()).order_by('-pk')
                if check_ids:
                    msg = "Customer {0} already consulted by this staff !!".format(str(cust_obj.cust_name))
                    raise Exception(msg) 
                    

                serializer = WebConsultationHdrSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save(cust_code=cust_obj.cust_code,
                    consultant_code=emp_obj.emp_code,doc_no=doc_no,
                    site_code=site.itemsite_code,site_codeid=site,
                    doc_date=date.today(),isactive=True)
                    if k.pk:
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
                if not 'cust_codeid' in request.data or not request.data['cust_codeid']:
                    raise Exception('Please give Customer ID!!.') 

                if not 'emp_codeid' in request.data or not request.data['emp_codeid']:
                    raise Exception('Please give Employee ID!!.') 

                emp_obj = Employee.objects.filter(pk=request.data['emp_codeid'],emp_isactive=True).order_by('-pk').first()      
                if not emp_obj:
                    raise Exception('Employee ID Does not exist!!.') 

                cust_obj = Customer.objects.filter(cust_isactive=True,pk=request.data['cust_codeid']).only('cust_isactive').order_by('-pk').first()      
                if not cust_obj:
                    raise Exception('Customer ID Does not exist!!.') 

               
                check_ids = WebConsultation_Hdr.objects.filter(~Q(pk=ref.pk)).filter(site_codeid__pk=ref.site_codeid.pk,
                cust_codeid=cust_obj,emp_codeid=emp_obj,doc_date=ref.doc_date).order_by('-pk')
                if check_ids:
                    msg = "Customer {0} already consulted by this staff  !!".format(str(cust_obj.cust_name))
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
            ref = self.get_object(pk)
            serializer = WebConsultationHdrSerializer(ref, context={'request': self.request})
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
            serializer = WebConsultationHdrSerializer(ref, data=request.data ,partial=True)
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
            return WebConsultation_Hdr.objects.get(pk=pk)
        except WebConsultation_Hdr.DoesNotExist:
            raise Exception('WebConsultation_Hdr Does not Exist') 

class WebConsultationDtlViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_Dtl.objects.filter().order_by('-pk')
    serializer_class = WebConsultationDtlSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        doc_no = self.request.GET.get('doc_no',None)
            
        if not doc_no:
            raise Exception('Please give doc_no') 
        
        queryset = WebConsultation_Dtl.objects.filter(doc_no=doc_no).order_by('-pk')
       
        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
           
            serializer_class = WebConsultationDtlSerializer
            
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

                

                for idx, reqt in enumerate(request.data):    
                    # print(reqt,"reqt")
                    serializer = WebConsultationDtlSerializer(data=reqt)
                    if serializer.is_valid():
                        if not 'doc_no' in reqt or not reqt['doc_no']:
                            raise Exception('Please give doc_no!!.') 
 
                        if not 'question_number' in reqt or not reqt['question_number']:
                            raise Exception('Please give question_number!!.') 

                        if not 'answer' in reqt or reqt['answer'] is None:
                            raise Exception('Please give answer!!.') 
                        
                        check_ids = False
                        if 'subquestion_number' in reqt and reqt['subquestion_number']:
                            check_ids = WebConsultation_Dtl.objects.filter(doc_no=reqt['doc_no'],
                            question_number=reqt['question_number'],subquestion_number=reqt['subquestion_number']).order_by('-pk')
                        else:
                            check_ids = WebConsultation_Dtl.objects.filter(doc_no=reqt['doc_no'],
                            question_number=reqt['question_number']).order_by('-pk')
                        if not check_ids:
                            k = serializer.save()

    
                    else:
                        data = serializer.errors

                        if 'non_field_errors' in data:
                            message = data['non_field_errors'][0]
                        else:
                            first_key = list(data.keys())[0]
                            message = str(first_key)+":  "+str(data[first_key][0])

                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":message,
                        'error': True, 'data': serializer.errors}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

                      
                result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_201_CREATED)
            
                
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
    
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def updatemulti(self, request): 
        try:  
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite

                for idx, reqt in enumerate(request.data):    
                    # print(reqt,"reqt")
                    if not 'id' in reqt or not reqt['id']:
                        raise Exception('Please give id!!.') 

                    if not 'answer' in reqt or reqt['answer'] is None:
                        raise Exception('Please give answer!!.') 
                
                   
                    ref = self.get_object(reqt['id'])
                    serializer = WebConsultationDtlSerializer(ref, data=reqt, partial=True)
                    if serializer.is_valid():
                            
                        serializer.save()

    
                    else:
                        data = serializer.errors

                        if 'non_field_errors' in data:
                            message = data['non_field_errors'][0]
                        else:
                            first_key = list(data.keys())[0]
                            message = str(first_key)+":  "+str(data[first_key][0])

                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":message,
                        'error': True, 'data': serializer.errors}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

                      
                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_200_OK)
            
                
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
                if not 'question_number' in request.data or not request.data['question_number']:
                    raise Exception('Please give question number!!.') 

                if not 'answer' in request.data or request.data['answer'] is None:
                    raise Exception('Please give answer!!.') 

                
                # check_ids = WebConsultation_Dtl.objects.filter(~Q(pk=ref.pk)).filter(doc_no=ref.doc_no,
                # question_number=request.data['question_number']).order_by('-pk')
                # if check_ids:
                #     msg = "WebConsultation Dtl {0} already record exist !!".format(str(ref.doc_no))
                #     raise Exception(msg) 
                    
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
            ref = self.get_object(pk)
            serializer = WebConsultationDtlSerializer(ref, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


   
    def destroy(self, request, pk=None):
        try:
            ref = self.get_object(pk)
            serializer = WebConsultationDtlSerializer(ref, data=request.data ,partial=True)
            state = status.HTTP_204_NO_CONTENT
            if serializer.is_valid():
                # serializer.save()
                ref.delete()

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
            return WebConsultation_Dtl.objects.get(pk=pk)
        except WebConsultation_Dtl.DoesNotExist:
            raise Exception('WebConsultation_Dtl Does not Exist') 

class WebConsultation_Questionsub_questionsViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_Questionsub_questions.objects.filter().order_by('-pk')
    serializer_class = WebConsultationQuestionsub_questionsSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        questionid = self.request.GET.get('questionid',None)
            
        if not questionid:
            raise Exception('Please give questionid') 

        q_ids = WebConsultation_Question.objects.filter(id=questionid)  
        if not q_ids:
            raise Exception('WebConsultation_Question ID does not') 

        
        queryset = WebConsultation_Questionsub_questions.objects.filter(questionid__pk=questionid).order_by('-pk')
       
        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = WebConsultationQuestionsub_questionsSerializer
            
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

                if not 'questionid' in request.data or not request.data['questionid']:
                    raise Exception('Please give questionid!!.') 

                if not 'options' in request.data or not request.data['options']:
                    raise Exception('Please give options!!.') 
                
                if not 'sub_question_english' in request.data or not request.data['sub_question_english']:
                    raise Exception('Please give sub question english!!.') 
                
                if not 'sub_question_chinese' in request.data or not request.data['sub_question_chinese']:
                    raise Exception('Please give sub question chinese!!.') 
                

                check_ids = WebConsultation_Questionsub_questions.objects.filter(questionid__pk=request.data['questionid'],
                sub_question_english=request.data['sub_question_english']).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this {0} and questionid!!".format(str(request.data['sub_question_english']))
                    raise Exception(msg) 
                    

                serializer = WebConsultationQuestionsub_questionsSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save()
                    
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
                if not 'questionid' in request.data or not request.data['questionid']:
                    raise Exception('Please give questionid!!.') 

                if not 'options' in request.data or not request.data['options']:
                    raise Exception('Please give options!!.') 
                
                if not 'sub_question_english' in request.data or not request.data['sub_question_english']:
                    raise Exception('Please give sub question english!!.') 
                
                if not 'sub_question_chinese' in request.data or not request.data['sub_question_chinese']:
                    raise Exception('Please give sub question chinese!!.') 
                
               
                check_ids = WebConsultation_Questionsub_questions.objects.filter(~Q(pk=ref.pk)).filter(questionid__pk=request.data['questionid'],
                sub_question_english=request.data['sub_question_english']).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this {0} and questionid!!".format(str(request.data['sub_question_english']))
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
            ref = self.get_object(pk)
            serializer = WebConsultationQuestionsub_questionsSerializer(ref, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


   
    def destroy(self, request, pk=None):
        try:
            ref = self.get_object(pk)
            serializer = WebConsultationQuestionsub_questionsSerializer(ref, data=request.data ,partial=True)
            state = status.HTTP_204_NO_CONTENT
            if serializer.is_valid():
                ref.delete()
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
            return WebConsultation_Questionsub_questions.objects.get(pk=pk)
        except WebConsultation_Questionsub_questions.DoesNotExist:
            raise Exception('WebConsultation Question subquestions Does not Exist') 
        
    



class WebConsultationQuestionMultichoiceViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_QuestionMultichoice.objects.filter().order_by('-pk')
    serializer_class = WebConsultationQuestionMultichoiceSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        questionid = self.request.GET.get('questionid',None)
            
        if not questionid:
            raise Exception('Please give questionid') 

        q_ids = WebConsultation_Question.objects.filter(id=questionid)  
        if not q_ids:
            raise Exception('WebConsultation_Question ID does not') 
    
        
        queryset = WebConsultation_QuestionMultichoice.objects.filter(questionid__pk=questionid).order_by('-pk')
       
        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = WebConsultationQuestionMultichoiceSerializer
            
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

                if not 'questionid' in request.data or not request.data['questionid']:
                    raise Exception('Please give questionid!!.') 

                if not 'choice' in request.data or not request.data['choice']:
                    raise Exception('Please give choice!!.') 
                
              

               
                check_ids = WebConsultation_QuestionMultichoice.objects.filter(questionid__pk=request.data['questionid'],
                choice=request.data['choice']).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this {0} and questionid!!".format(str(request.data['choice']))
                    raise Exception(msg) 
                    

                serializer = WebConsultationQuestionMultichoiceSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save()
                    
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
                if not 'questionid' in request.data or not request.data['questionid']:
                    raise Exception('Please give questionid!!.') 

                if not 'choice' in request.data or not request.data['choice']:
                    raise Exception('Please give choice!!.') 
                
               
                check_ids = WebConsultation_QuestionMultichoice.objects.filter(~Q(pk=ref.pk)).filter(questionid__pk=request.data['questionid'],
                choice=request.data['choice']).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this {0} and questionid!!".format(str(request.data['choice']))
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
            ref = self.get_object(pk)
            serializer = WebConsultationQuestionMultichoiceSerializer(ref, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


   
    def destroy(self, request, pk=None):
        try:
            ref = self.get_object(pk)
            serializer = WebConsultationQuestionMultichoiceSerializer(ref, data=request.data ,partial=True)
            state = status.HTTP_204_NO_CONTENT
            if serializer.is_valid():
                ref.delete()
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
            return WebConsultation_QuestionMultichoice.objects.get(pk=pk)
        except WebConsultation_QuestionMultichoice.DoesNotExist:
            raise Exception('WebConsultation QuestionMultichoice Does not Exist') 
    



class WebConsultationQuestionViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_Question.objects.filter(isactive=True).order_by('-pk')
    serializer_class = WebConsultationQuestionSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        queryset = WebConsultation_Question.objects.filter(isactive=True,site_ids__pk=site.pk).order_by('-pk')
       
        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = WebConsultationQuestionSerializer
            
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

                if not 'question_group' in request.data or not request.data['question_group']:
                    raise Exception('Please give question group!!.') 

                if not 'question_number' in request.data or not request.data['question_number']:
                    raise Exception('Please give question number!!.') 
                
                if not 'question_english' in request.data or not request.data['question_english']:
                    raise Exception('Please give question english!!.') 

                if not 'itemsite_ids' in request.data or not request.data['itemsite_ids']:
                    raise Exception('Please give site ids!.') 
                
                if not 'question_text' in request.data or request.data['question_text'] is None:
                    raise Exception('Please give question Text!!.') 


                requestData = request.data
                itemsite_ids = requestData.pop('itemsite_ids')
                multichoice_ids = requestData.pop('multichoice_ids')
                sub_questions = requestData.pop('sub_questions')
                # print(itemsite_ids,"itemsite_ids")
                res = str(itemsite_ids).split(',')
                # print(res,"res")
                sitelist = []
                # print(res,"res") 
                for i in res:
                    # print(i,"ii")
                    ex_ids = WebConsultation_Question.objects.filter(question_group=request.data['question_group'],
                    question_english=request.data['question_english'],site_ids__pk=i)
                    # print(ex_ids,"ex_ids")
                    if not ex_ids and i not in sitelist:
                        sitelist.append(i)
                
                # print(sitelist,"sitelist")
                if sitelist == []:
                    raise Exception('WebConsultation Question duplicate records wont allow') 

                if sitelist !=[]: 
                    serializer = WebConsultationQuestionSerializer(data=request.data)
                    if serializer.is_valid():
                        
                        k = serializer.save(isactive=True)
                        for div in sitelist:
                            k.site_ids.add(div)

                        if multichoice_ids != []:
                            for j in multichoice_ids:
                                check_ids = WebConsultation_QuestionMultichoice.objects.filter(questionid__pk=k.pk,
                                choice=j['choice']).order_by('-pk')
                                if not check_ids:
                                    c = WebConsultation_QuestionMultichoice(questionid=k,choice=j['choice'])
                                    c.save()

                        if sub_questions != []:
                            for l in sub_questions:
                                checkids = WebConsultation_Questionsub_questions.objects.filter(questionid__pk=k.pk,
                                sub_question_english=l['sub_question_english']).order_by('-pk')
                                if not checkids:
                                    s = WebConsultation_Questionsub_questions(questionid=k,
                                    options=l['options'],sub_question_english=l['sub_question_english'],
                                    sub_question_chinese=l['sub_question_chinese'])
                                    s.save()            

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
                if not 'question_group' in request.data or not request.data['question_group']:
                    raise Exception('Please give question group!!.') 

                if not 'question_number' in request.data or not request.data['question_number']:
                    raise Exception('Please give question number!!.') 
                
                if not 'question_english' in request.data or not request.data['question_english']:
                    raise Exception('Please give question english!!.') 

                if not 'itemsite_ids' in request.data or not request.data['itemsite_ids']:
                    raise Exception('Please give site ids!.') 
                
                if not 'question_text' in request.data or request.data['question_text'] is None:
                    raise Exception('Please give question Text!!.') 

                
                requestData = request.data
                itemsite_ids = requestData.pop('itemsite_ids')
                res = itemsite_ids.split(',')
                sitelist = []

                for i in res:
                    ex_ids = WebConsultation_Question.objects.filter(~Q(pk=ref.pk)).filter(question_group=request.data['question_group'],
                    question_english=request.data['question_english'],site_ids__pk=i)
                    if not ex_ids and i not in sitelist:
                        sitelist.append(i)
                
                if sitelist == []:
                    raise Exception('WebConsultation Question duplicate records wont allow') 


                if sitelist !=[]:
                
                    serializer = self.get_serializer(ref, data=request.data, partial=True)
                    if serializer.is_valid():
                    
                        k = serializer.save()
                        for existing in ref.site_ids.all():
                            ref.site_ids.remove(existing)

                        
                        for div in sitelist:
                            k.site_ids.add(div)

                        
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
            ref = self.get_object(pk)
            serializer = WebConsultationQuestionSerializer(ref, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


   
    def destroy(self, request, pk=None):
        try:
            # request.data["isactive"] = False
            ref = self.get_object(pk)
            serializer = WebConsultationQuestionSerializer(ref, data=request.data ,partial=True)
            state = status.HTTP_204_NO_CONTENT
            if serializer.is_valid():
                # serializer.save()
                WebConsultation_QuestionMultichoice.objects.filter(questionid__pk=ref.pk).delete()
                ref.delete()
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
            return WebConsultation_Question.objects.get(pk=pk)
        except WebConsultation_Question.DoesNotExist:
            raise Exception('WebConsultation Question Does not Exist') 
        
        
class WebConsultation_AnalysisResultViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_AnalysisResult.objects.filter(isactive=True).order_by('-pk')
    serializer_class = WebConsultation_AnalysisResultSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        
        doc_no = self.request.GET.get('doc_no',None)
            
        if not doc_no:
            raise Exception('Please give doc_no') 
        
       
        queryset = WebConsultation_AnalysisResult.objects.filter(isactive=True,
        doc_no=doc_no).order_by('-pk')
       
        return queryset      

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = WebConsultation_AnalysisResultSerializer
            
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

                if not 'age' in request.data or not request.data['age']:
                    raise Exception('Please give age!!.') 

                if not 'cust_weight' in request.data or not request.data['cust_weight']:
                    raise Exception('Please give customer weight!!.') 
                
                if not 'doc_no' in request.data or not request.data['doc_no']:
                    raise Exception('Please give doc no!!.') 

                if not 'cust_code' in request.data or not request.data['cust_code']:
                    raise Exception('Please give customer code!!.') 
                
                dcheck_ids = WebConsultation_AnalysisResult.objects.filter(doc_no=request.data['doc_no']).order_by('-pk')
                if dcheck_ids:
                    msg = "Already record there for this doc no {0}!!".format(str(request.data['doc_no']))
                    raise Exception(msg) 
                    

               
                check_ids = WebConsultation_AnalysisResult.objects.filter(site_code=site.itemsite_code,
                cust_code=request.data['cust_code'],create_date__date=date.today()).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this customer this site today date {0}!!".format(str(request.data['cust_code']))
                    raise Exception(msg) 
                    

                serializer = WebConsultation_AnalysisResultSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save(
                    site_code=site.itemsite_code,
                    create_date=date.today())
                    
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
                if not 'age' in request.data or not request.data['age']:
                    raise Exception('Please give age!!.') 

                if not 'cust_weight' in request.data or not request.data['cust_weight']:
                    raise Exception('Please give customer weight!!.') 

                if not 'doc_no' in request.data or not request.data['doc_no']:
                    raise Exception('Please give doc no!!.') 
    
                if not 'cust_code' in request.data or not request.data['cust_code']:
                    raise Exception('Please give customer code!!.') 
    
               
                check_ids = WebConsultation_AnalysisResult.objects.filter(~Q(pk=ref.pk)).filter(site_code=site.itemsite_code,
                cust_code=request.data['cust_code'],create_date=ref.create_date).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this customer this site today date {0}!!".format(str(request.data['cust_code']))
                    raise Exception(msg) 
                    
                serializer = self.get_serializer(ref, data=request.data, partial=True)
                if serializer.is_valid():
                
                    serializer.save(last_updatedate=date.today())
                    
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
            ref = self.get_object(pk)
            serializer = WebConsultation_AnalysisResultSerializer(ref, context={'request': self.request})
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
            serializer = WebConsultation_AnalysisResultSerializer(ref, data=request.data ,partial=True)
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
            return WebConsultation_AnalysisResult.objects.get(pk=pk)
        except WebConsultation_AnalysisResult.DoesNotExist:
            raise Exception('WebConsultation AnalysisResult Does not Exist') 
            

class WebConsultation_ReferralViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_Referral.objects.filter(isactive=True).order_by('-pk')
    serializer_class = WebConsultation_ReferralSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        doc_no = self.request.GET.get('doc_no',None)
            
        if not doc_no:
            raise Exception('Please give doc_no') 
        
       
        queryset = WebConsultation_Referral.objects.filter(isactive=True,
        doc_no=doc_no).order_by('-pk')
       
        return queryset      

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = WebConsultation_ReferralSerializer
            
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

                if not 'referral_name' in request.data or not request.data['referral_name']:
                    raise Exception('Please give referral name!!.') 

                if not 'referral_age' in request.data or not request.data['referral_age']:
                    raise Exception('Please give referral age!!.') 

                if not 'referral_contactno' in request.data or not request.data['referral_contactno']:
                    raise Exception('Please give referral contactno!!.') 
                    
                if not 'doc_no' in request.data or not request.data['doc_no']:
                    raise Exception('Please give doc no!!.') 

                if not 'cust_code' in request.data or not request.data['cust_code']:
                    raise Exception('Please give customer code!!.') 
    

               
                check_ids = WebConsultation_Referral.objects.filter(site_code=site.itemsite_code,
                cust_code=request.data['cust_code'],referral_name=request.data['referral_name'],
                create_date__date=date.today()).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this customer this site ,today date , referral name{0}!!".format(str(request.data['cust_code']))
                    raise Exception(msg) 
                    

                serializer = WebConsultation_ReferralSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save(
                    site_code=site.itemsite_code,
                    create_date=date.today())
                    
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
                if not 'referral_name' in request.data or not request.data['referral_name']:
                    raise Exception('Please give referral name!!.') 

                if not 'referral_age' in request.data or not request.data['referral_age']:
                    raise Exception('Please give referral age!!.') 

                if not 'referral_contactno' in request.data or not request.data['referral_contactno']:
                    raise Exception('Please give referral contactno!!.') 
                    
                if not 'doc_no' in request.data or not request.data['doc_no']:
                    raise Exception('Please give doc no!!.') 

                if not 'cust_code' in request.data or not request.data['cust_code']:
                    raise Exception('Please give customer code!!.') 
    
               
                check_ids = WebConsultation_Referral.objects.filter(~Q(pk=ref.pk)).filter(site_code=site.itemsite_code,
                cust_code=request.data['cust_code'],referral_name=request.data['referral_name'],
                create_date=ref.create_date).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this customer this site ,today date , referral name{0}!!".format(str(request.data['cust_code']))
                    raise Exception(msg) 
                    
                serializer = self.get_serializer(ref, data=request.data, partial=True)
                if serializer.is_valid():
                
                    serializer.save(last_updatedate=date.today())
                    
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
            ref = self.get_object(pk)
            serializer = WebConsultation_ReferralSerializer(ref, context={'request': self.request})
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
            serializer = WebConsultation_ReferralSerializer(ref, data=request.data ,partial=True)
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
            return WebConsultation_Referral.objects.get(pk=pk)
        except WebConsultation_Referral.DoesNotExist:
            raise Exception('WebConsultation Referral Does not Exist') 


class WebConsultation_Referral_HdrViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_Referral_Hdr.objects.filter(isactive=True).order_by('-pk')
    serializer_class = WebConsultation_Referral_HdrSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        doc_no = self.request.GET.get('doc_no',None)
            
        if not doc_no:
            raise Exception('Please give doc_no') 
        
        queryset = WebConsultation_Referral_Hdr.objects.filter(isactive=True,
        doc_no=doc_no).order_by('-pk')
       
        return queryset      

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = WebConsultation_Referral_HdrSerializer
            
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

                # if not 'signature_img' in request.data or not request.data['signature_img']:
                #     raise Exception('Please give signature img!!.') 

                # if not 'welcomedoor_signatureimg' in request.data or not request.data['welcomedoor_signatureimg']:
                #     raise Exception('Please give welcomedoor signatureimg!!.') 

                # if not 'create_by' in request.data or not request.data['create_by']:
                #     raise Exception('Please give create by!!.') 
                    
                if not 'doc_no' in request.data or not request.data['doc_no']:
                    raise Exception('Please give doc no!!.') 

                
               
                check_ids = WebConsultation_Referral_Hdr.objects.filter(site_code=site.itemsite_code,
                doc_no=request.data['doc_no'],
                create_date__date=date.today()).order_by('-pk')
                if check_ids:
                    msg = "Already record there for this customer this site ,today date , doc no {0}!!".format(str(request.data['doc_no']))
                    raise Exception(msg) 
                    

                serializer = WebConsultation_Referral_HdrSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save(isactive=True,
                    site_code=site.itemsite_code,
                    create_date=date.today(),create_by=fmspw[0].pw_userlogin)
                    
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
                if not 'signature_img' in request.data or not request.data['signature_img']:
                    raise Exception('Please give signature img!!.') 

                if not 'welcomedoor_signatureimg' in request.data or not request.data['welcomedoor_signatureimg']:
                    raise Exception('Please give welcomedoor signatureimg!!.') 

                if not 'last_updateby' in request.data or not request.data['last_updateby']:
                    raise Exception('Please give last updateby!!.') 
                    
                if not 'doc_no' in request.data or not request.data['doc_no']:
                    raise Exception('Please give doc no!!.') 

               
                check_ids = WebConsultation_Referral_Hdr.objects.filter(~Q(pk=ref.pk)).filter(site_code=site.itemsite_code,
                doc_no=request.data['doc_no'],
                create_date=ref.create_date).order_by('-pk').first()
                if check_ids:
                    msg = "Already record there for this customer this site ,today date , doc no {0}!!".format(str(request.data['doc_no']))
                    raise Exception(msg) 
                    
                serializer = self.get_serializer(ref, data=request.data, partial=True)
                if serializer.is_valid():
                
                    serializer.save(last_updatedate=date.today(),last_updateby=fmspw.pw_userlogin)
                    
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
            ref = self.get_object(pk)
            serializer = WebConsultation_Referral_HdrSerializer(ref, context={'request': self.request})
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
            serializer = WebConsultation_Referral_HdrSerializer(ref, data=request.data ,partial=True)
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
            return WebConsultation_Referral_Hdr.objects.get(pk=pk)
        except WebConsultation_Referral_Hdr.DoesNotExist:
            raise Exception('WebConsultation Referral Hdr Does not Exist') 

class TransactionCustomerViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TransactionCustomerSerializer

    def get_queryset(self):
        queryset = PosHaud.objects.none()
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)

        if not from_date:
            raise Exception('Please give from_date') 
        
        if not to_date:
            raise Exception('Please give to_date') 
       
       
        queryset = PosHaud.objects.filter(isvoid=False,ItemSite_Codeid__pk=site.pk,
        sa_transacno_type__in=['Receipt','Non Sales']).order_by('-pk')

        q = self.request.GET.get('search',None)
        if q:
            queryset = queryset.filter(Q(sa_custnoid__cust_name__icontains=q) | 
            Q(sa_custnoid__cust_code__icontains=q) |
            Q(sa_custnoid__cust_nric__icontains=q) | Q(sa_custnoid__cust_joindate__date__icontains=q) )
            # print(queryset,"queryset gg")
        
        query = list(set(queryset.values_list('sa_custnoid', flat=True).distinct()))
        if not from_date and not to_date:
            query = list(set(queryset.values_list('sa_custnoid', flat=True).distinct()))
        else:
            if from_date and to_date:  
                # queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).values('sa_custnoid','sa_custname','sa_custno','sa_custnoid__cust_joindate','sa_custnoid__cust_nric').distinct().order_by('sa_custnoid')
                query = list(set(queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).values_list('sa_custnoid', flat=True).distinct()))
            
        # print(query,"query")
        cust_ids = Customer.objects.filter(cust_isactive=True,pk__in=query).order_by('-pk')
        return cust_ids

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset()).order_by('-pk')
            serializer_class =  TransactionCustomerSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action,)
           
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def listdaud(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            from_date = self.request.GET.get('from_date',None)
            if not from_date:
                raise Exception('Please give from_date') 

            to_date = self.request.GET.get('to_date',None)
            if not to_date:
                raise Exception('Please give to_date') 
            cust_id = self.request.GET.get('cust_id',None)
            if not cust_id:
                raise Exception('Please give cust_id')

            cust_obj = Customer.objects.filter(pk=cust_id,cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

            h_ids = list(set(PosHaud.objects.filter(isvoid=False,ItemSite_Codeid__pk=site.pk,
            sa_transacno_type__in=['Receipt','Non Sales'],sa_custnoid=cust_obj,
            sa_date__date__gte=from_date,sa_date__date__lte=to_date).order_by('-pk').values_list('sa_transacno_ref', flat=True).distinct()))
            
            d_ids = list(set(TNC_Detail.objects.filter(receiptno__in=h_ids).values_list('receiptno', flat=True).distinct()))

            haud_ids = list(set(PosHaud.objects.filter(isvoid=False,ItemSite_Codeid__pk=site.pk,
            sa_transacno_type__in=['Receipt','Non Sales'],sa_custnoid=cust_obj,
            sa_date__date__gte=from_date,sa_date__date__lte=to_date).filter(~Q(sa_transacno_ref__in=d_ids)).order_by('-pk').values_list('sa_transacno', flat=True).distinct()))
            # print(haud_ids,"haud_ids") 
            
            queryset = PosDaud.objects.filter(sa_transacno__in=haud_ids,record_detail_type__in=['SERVICE','PACKAGE']).order_by('-pk')    
            # print(queryset,"queryset")
            
            full_tot = queryset.count()
            page= request.GET.get('page',1)
            limit = request.GET.get('limit',12)
           

            paginator = Paginator(queryset, limit)
            total_page = paginator.num_pages

            try:
                queryset = paginator.page(page)
            except (EmptyPage, InvalidPage):
                queryset = paginator.page(total_page) # last page

            serializer = TransactionPosDaudSerializer(queryset, many=True, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,
                "total":full_tot,"total_pages":total_page}}, 
                'dataList': serializer.data}}
            
          
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def listtncdetail(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite 
            from_date = self.request.GET.get('from_date',None)
            if not from_date:
                raise Exception('Please give from_date') 

            to_date = self.request.GET.get('to_date',None)
            if not to_date:
                raise Exception('Please give to_date') 
            cust_id = self.request.GET.get('cust_id',None)
            if not cust_id:
                raise Exception('Please give cust_id')

            cust_obj = Customer.objects.filter(pk=cust_id,cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
            queryset = TNC_Header.objects.filter(cust_code=cust_obj.cust_code,
            site_code=site.itemsite_code,sign_date__date__gte=from_date,
            sign_date__date__lte=to_date).order_by('-pk')
            # queryset = TNC_Detail.objects.filter(tncno__in=h_ids).order_by('-pk')

            
            full_tot = queryset.count()
            page= request.GET.get('page',1)
            limit = request.GET.get('limit',12)
           

            paginator = Paginator(queryset, limit)
            total_page = paginator.num_pages

            try:
                queryset = paginator.page(page)
            except (EmptyPage, InvalidPage):
                queryset = paginator.page(total_page) # last page

            serializer = TNC_HeaderSerializer(queryset, many=True, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,
                "total":full_tot,"total_pages":total_page}}, 
                'dataList': serializer.data}}
            
          
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def listtncformdetails(self, request):
        try: 
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite 
            tncno = self.request.GET.get('tncno',None)
            if not tncno:
                raise Exception('Please give tncno') 
            
            queryset = TNC_Detail.objects.filter(tncno=tncno).order_by('-pk')
            tnchdr = TNC_Header.objects.filter(tncno=tncno).order_by('-pk').first()
            if not queryset or not tnchdr:
                raise Exception('TNC_Detail or TNC_Header does not exist!!') 
            serializer = TNC_DetailformSerializer(queryset, many=True, context={'request': self.request})
            
            
            client_name = ''
            if tnchdr and tnchdr.cust_code:
                cust_obj = Customer.objects.filter(cust_code=tnchdr.cust_code,cust_isactive=True).first()
                if cust_obj and cust_obj.cust_name:
                    client_name = cust_obj.cust_name

            consultant_name = ''
            if tnchdr and tnchdr.consultant_code:
                emp_obj = Employee.objects.filter(emp_code=tnchdr.consultant_code,
                emp_isactive=True).first()
                if emp_obj and emp_obj.display_name:
                    consultant_name = emp_obj.display_name
         
            sign_date = ""
            if tnchdr and tnchdr.sign_date:
                splt = str(tnchdr.sign_date).split(" ") 
                sign_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
            
            signature1 = ""
            if tnchdr and tnchdr.signature1:
                signature1 = str(SITE_ROOT)+str(tnchdr.signature1)

            signature2 = ""
            if tnchdr and tnchdr.signature2:
                signature2 = str(SITE_ROOT)+str(tnchdr.signature2)
    

            header_data = {
                'client_code': tnchdr.cust_code if tnchdr and tnchdr.cust_code else "",
                'consultant_code': tnchdr.consultant_code if tnchdr and tnchdr.consultant_code else "",
                'client_name': client_name,'consultant_name':consultant_name,'sign_date':sign_date,
                'client_signature1' : signature1,'consultant_signature2' : signature2,
                }
            
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'header_data': header_data, 'data': serializer.data}
            
            return Response(result, status=status.HTTP_200_OK)
 

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
 



    
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def createtnc(self, request): 
        try:  
            with transaction.atomic():
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite

                if not self.request.data.get('daud_ids',None):
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                    "message":"Please Select Atleast Any 1 Package",'error': True}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


                daud_ids =  request.data['daud_ids'].split(',')
                posdaud_ids =  PosDaud.objects.filter(pk__in=daud_ids)  
                if not posdaud_ids:
                    raise Exception('PosDaud ids does not exist!!.') 
                     
                if not 'cust_code' in request.data or not request.data['cust_code']:
                    raise Exception('Please give customer code!!.') 

                if not 'consultant_code' in request.data or not request.data['consultant_code']:
                    raise Exception('Please give consultant code!!.') 
    

                if not 'signature1' in request.data or not request.data['signature1']:
                    raise Exception('Please give signature1!!.')

                if not 'signature2' in request.data or not request.data['signature2']:
                    raise Exception('Please give signature2!!.')

                control_obj = ControlNo.objects.filter(control_description__iexact="Customer Terms and conditions",Site_Codeid__pk=site.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer Terms and conditions Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                tncno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                check = False    
                if posdaud_ids:
                    for p in posdaud_ids:
                        haud_ids = PosHaud.objects.filter(sa_transacno=p.sa_transacno).first()
                        if haud_ids:
                            TNC_Detail(tncno=tncno,receipt_date=p.sa_date,receiptno=haud_ids.sa_transacno_ref,
                            package=p.dt_itemdesc,amount=p.dt_transacamt,dt_lineno=p.dt_lineno).save()
                            check = True

                    if check == True:
                        check_ids = TNC_Header.objects.filter(tncno=tncno)
                        if not check_ids:
                            TNC_Header(tncno=tncno,cust_code=request.data['cust_code'],
                            consultant_code=request.data['consultant_code'],
                            signature1=request.data['signature1'],
                            signature2=request.data['signature2'],
                            sign_date=date.today(),site_code=site.itemsite_code).save()
                            control_obj.control_no = int(control_obj.control_no) + 1
                            control_obj.save()
                            result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                            'error': False}
                            return Response(result, status=status.HTTP_201_CREATED)
                    else:
                        raise Exception('TNC not created !!.')


        except Exception as e:
           invalid_message = str(e)
           return general_error_response(invalid_message)     
          

class TNC_MasterViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = TNC_Master.objects.filter(isactive=True).order_by('-pk')
    serializer_class = TNCMasterSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        queryset = TNC_Master.objects.filter(isactive=True).order_by('-pk')
       
        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = TNCMasterSerializer
            
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

                if not 'sno' in request.data or not request.data['sno']:
                    raise Exception('Please give SNo!!.') 

                if not 'english' in request.data or not request.data['english']:
                    raise Exception('Please give English!!.')

                if not 'otherlanguage' in request.data or not request.data['otherlanguage']:
                    raise Exception('Please give OtherLanguage!!.')
                
                check_ids = TNC_Master.objects.filter(isactive=True,english=request.data['english'])
                if check_ids:
                    msg = "{0} already this record exist!!".format(str(request.data['english']))
                    raise Exception(msg) 
                    

                serializer = TNCMasterSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save()
                   
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
                if not 'sno' in request.data or not request.data['sno']:
                    raise Exception('Please give SNo!!.') 

                if not 'english' in request.data or not request.data['english']:
                    raise Exception('Please give English!!.')

                if not 'otherlanguage' in request.data or not request.data['otherlanguage']:
                    raise Exception('Please give OtherLanguage!!.')
                
               
                check_ids = TNC_Master.objects.filter(~Q(pk=ref.pk)).filter(english=request.data['english']).order_by('-pk')
                if check_ids:
                    msg = "{0} already this record exist  !!".format(str(request.data['english']))
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
            ref = self.get_object(pk)
            serializer = TNCMasterSerializer(ref, context={'request': self.request})
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
            serializer = TNCMasterSerializer(ref, data=request.data ,partial=True)
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
            return TNC_Master.objects.get(pk=pk)
        except TNC_Master.DoesNotExist:
            raise Exception('TNC_Master Does not Exist') 
    

class ClientDetailsListAPIView(GenericAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
          
    
    def get(self, request):
        try:    
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            title = Title.objects.filter(product_license=site.itemsite_code).first()
            logo = ""
            if title and title.logo_pic:
                logo = str(SITE_ROOT) + str(title.logo_pic)
            
            val = {'company_name': title.comp_title1 if title and title.comp_title1 else '',
            'client_name': title.trans_h1 if title and title.trans_h1 else '',
            'logo' : logo, 'address': title.trans_h2 if title and title.trans_h2 else '', 
            'sequoia_logo': str(SITE_ROOT) + 'img/beautesoftlogo.png'}
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully",
            'error': False,'data': val}
        

            return Response(result, status=status.HTTP_200_OK)
    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          


class WebConsultationPrintListAPIView(GenericAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
          
    
    def get(self, request):
        try:    
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            doc_no = self.request.GET.get('doc_no',None)
            if not doc_no:
                raise Exception('Please give doc_no') 

            webhdr_obj = WebConsultation_Hdr.objects.filter(doc_no=doc_no).first()  
            if not webhdr_obj:
                raise Exception('WebConsultation Hdr ID Doesnt exist!!') 
            
            doc_date = ""
            if webhdr_obj and webhdr_obj.doc_date:
                splt = str(webhdr_obj.doc_date).split(" ") 
                doc_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d/%m/%Y")
            
            cust_obj = Customer.objects.filter(cust_isactive=True,
            pk=webhdr_obj.cust_codeid.pk).only('cust_isactive').order_by('-pk').first()        
            if not cust_obj:
                raise Exception('Customer ID Does not exist!!.') 
            
            signature = ""
            if webhdr_obj and webhdr_obj.signature:
                signature = str(SITE_ROOT)+str(webhdr_obj.signature)

            val = {'date' : doc_date,
            'consultant': webhdr_obj.emp_codeid.display_name if webhdr_obj.emp_codeid and webhdr_obj.emp_codeid.display_name else "",
            'site': webhdr_obj.site_codeid.itemsite_desc +" ("+ webhdr_obj.site_codeid.itemsite_code +")" if webhdr_obj.site_codeid else "",
            'signature': signature}
            
            cust_val = {'name': cust_obj.cust_name if cust_obj.cust_name else "",
            'nric': cust_obj.cust_nric if cust_obj.cust_nric else "",
            'contact_no': cust_obj.cust_phone2 if cust_obj.cust_phone2 else "", 
            'birthday': cust_obj.cust_dob if cust_obj.cust_dob else "",
            'occupation': cust_obj.cust_occupation if cust_obj.cust_occupation else "", 
            'maritalStatus': cust_obj.cust_marital if cust_obj.cust_marital else "",
            'address1' : cust_obj.sgn_block if cust_obj.sgn_block else "", 
            'address2' : cust_obj.sgn_street if cust_obj.sgn_street else "",
            'address3' : cust_obj.sgn_unitno if cust_obj.sgn_unitno else "", 
            'address4' : cust_obj.cust_postcode if cust_obj.cust_postcode else "",
            'sex' : cust_obj.Cust_sexesid.itm_name.strip() if cust_obj.Cust_sexesid else "",
            'citizenship' : cust_obj.cust_nationality.strip() if cust_obj.cust_nationality else "",
            'race': cust_obj.cust_race if cust_obj.cust_race else "",
            'email': cust_obj.cust_email if cust_obj.cust_email else ""}


            quest_ids = WebConsultation_Question.objects.filter(isactive=True)
            qserializer = WebConsultationQuestionprintSerializer(quest_ids, many=True, context={'request': self.request})
            
            dtl_answerids = WebConsultation_Dtl.objects.filter(doc_no=doc_no).values('pk','question_number','answer','answer_text','subquestion_number')

            analysis_ids = WebConsultation_AnalysisResult.objects.filter(doc_no=doc_no).first()  
            aserializer = WebConsultation_AnalysisResultprintSerializer(analysis_ids, context={'request': self.request})

            refferal_ids = WebConsultation_Referral.objects.filter(doc_no=doc_no)
            rserializer = WebConsultation_ReferralprintSerializer(refferal_ids, many=True, context={'request': self.request})

            refferalhdr_ids = WebConsultation_Referral_Hdr.objects.filter(doc_no=doc_no).first() 
            rhdrserializer = WebConsultation_Referral_HdrprintSerializer(refferalhdr_ids,context={'request': self.request}) 
            
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully",
            'error': False,'data': val,'customer_data': cust_val,
            'question_data': qserializer.data,'answer_data': dtl_answerids,
            'analysis_result': aserializer.data, 'referral_list': rserializer.data,
            'referralhdr_list': rhdrserializer.data}
        

            return Response(result, status=status.HTTP_200_OK)
    


            

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          

    