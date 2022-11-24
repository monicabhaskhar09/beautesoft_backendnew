from django.shortcuts import render
from cl_table.authentication import ExpiringTokenAuthentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from cl_app.permissions import authenticated_only
from .serializers import (WebConsultationHdrSerializer,WebConsultationQuestionSerializer)
from .models import (WebConsultation_Hdr,WebConsultation_Question)
from cl_table.models import Fmspw,Employee,ControlNo,Customer
from rest_framework import status,viewsets,mixins
from rest_framework.response import Response
from custom.views import response, get_client_ip, round_calc
from cl_app.utils import general_error_response
from django.db import transaction, connection
from datetime import date, timedelta, datetime
from cl_app.models import ItemSitelist
from django.db.models import Q

# Create your views here.

class WebConsultationHdrViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_Hdr.objects.filter(isactive=True).order_by('-pk')
    serializer_class = WebConsultationHdrSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        queryset = WebConsultation_Hdr.objects.filter(isactive=True,site_codeid=site).order_by('-pk')
       
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
                doc_no = str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)    
                         

                
                check_ids = WebConsultation_Hdr.objects.filter(site_code=site.itemsite_code,
                cust_codeid=cust_obj,emp_codeid=emp_obj,doc_date=date.today()).order_by('-pk')
                if check_ids:
                    msg = "Customer {0} already consulted by this staff !!".format(str(cust_obj.cust_name))
                    raise Exception(msg) 
                    

                serializer = WebConsultationHdrSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save(cust_code=cust_obj.cust_code,
                    consultant_code=emp_obj.emp_code,doc_no=doc_no,
                    site_code=site.itemsite_code,site_codeid=site,
                    doc_date=date.today())
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
        

class WebConsultationQuestionViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = WebConsultation_Question.objects.filter(isactive=True).order_by('-pk')
    serializer_class = WebConsultationQuestionSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        queryset = WebConsultation_Question.objects.filter().order_by('-pk')
       
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
    

                requestData = request.data
                itemsite_ids = requestData.pop('itemsite_ids')
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
            request.data["isactive"] = False
            ref = self.get_object(pk)
            serializer = WebConsultationQuestionSerializer(ref, data=request.data ,partial=True)
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
            return WebConsultation_Question.objects.get(pk=pk)
        except WebConsultation_Question.DoesNotExist:
            raise Exception('WebConsultation Question Does not Exist') 
        
        