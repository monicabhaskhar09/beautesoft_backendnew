from django.shortcuts import render
from cl_table.authentication import ExpiringTokenAuthentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from cl_app.permissions import authenticated_only
from .models import (Reportmaster)
from .serializers import (ReportmasterSerializer)
from cl_table.models import (Fmspw,Employee,ControlNo,Customer,PosHaud,PosDaud,Title,Paytable)
from rest_framework import status,viewsets,mixins
from rest_framework.response import Response
from custom.views import response, get_client_ip, round_calc
from cl_app.utils import general_error_response
from django.db import transaction, connection
import datetime
from datetime import date, timedelta
from cl_app.models import ItemSitelist
from django.db.models import Q
from rest_framework.decorators import action
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator, InvalidPage
from Cl_beautesoft.settings import SMS_ACCOUNT_SID, SMS_AUTH_TOKEN, SMS_SENDER, SITE_ROOT
from rest_framework.generics import GenericAPIView, CreateAPIView

# Create your views here.

class ReportmasterViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Reportmaster.objects.filter(inactive="N").order_by('-pk')
    serializer_class = ReportmasterSerializer

    def get_queryset(self):
      
        queryset = Reportmaster.objects.filter(inactive="N").order_by('-pk')
        q = self.request.GET.get('search',None)
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | 
            Q(description__icontains=q))[:20]

        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            serializer_class = ReportmasterSerializer
            
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

                if not 'name' in request.data or not request.data['name']:
                    raise Exception('Please give name!!.') 

                if not 'image' in request.data or not request.data['image']:
                    raise Exception('Please give image!!.') 

                control_obj = ControlNo.objects.filter(control_description__iexact="Reportmaster").first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reportmaster Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                code_no = str(control_obj.control_prefix)+str(control_obj.control_no)    
                      
                check_ids = Reportmaster.objects.filter(name=request.data['name']).order_by('-pk')
                if check_ids:
                    msg = "Reportmaster name {0} already exist or inactive !!".format(str(request.data['name']))
                    raise Exception(msg) 
                    

                serializer = ReportmasterSerializer(data=request.data)
                if serializer.is_valid():
                    
                    k = serializer.save(inactive="N",code=code_no)
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
                rep = self.get_object(pk)
              
                    
                serializer = self.get_serializer(rep, data=request.data, partial=True)
                if serializer.is_valid():
                
                    serializer.save(inactive="N")
                    
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
            rep = self.get_object(pk)
            serializer = ReportmasterSerializer(rep, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 


   
    def destroy(self, request, pk=None):
        try:
            request.data["inactive"] = None
            ref = self.get_object(pk)
            serializer = ReportmasterSerializer(ref, data=request.data ,partial=True)
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
            return Reportmaster.objects.get(pk=pk)
        except Reportmaster.DoesNotExist:
            raise Exception('Reportmaster Does not Exist') 

# Collection By Outlet
def dictfetchall(self,cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class PaymentPaytableListAPIView(GenericAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get_paytable(self):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT Distinct pay_code [code],pay_description [name] FROM PAYTABLE WHERE pay_isactive='True'  ORDER BY pay_description;")
            res = dictfetchall(self, cursor)
            return res
        except Paytable.DoesNotExist:
            raise Exception('Paytable Does not Exist') 
    
    def get(self, request):
        try:    
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            fk_id = self.get_paytable()

            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully",
            'error': False,'data': fk_id}
        

            return Response(result, status=status.HTTP_200_OK)
    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          

class siteListingAPIView(GenericAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get_sitelisting(self,empcode):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT TOP(100) ItemSite_Code as itemcode, ItemSite_Desc as itemdesc FROM Item_SiteList WHERE ItemSite_Isactive='True' AND itemsite_code in (SELECT Site_Code from Emp_SiteList WHERE emp_code = %s and isactive=1) ORDER BY itemdesc;",[empcode])
            res = dictfetchall(self, cursor)
            return res
        except Paytable.DoesNotExist:
            raise Exception('Paytable Does not Exist') 
    
    def get(self, request):
        try:    
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            empcode = fmspw.Emp_Codeid.emp_code
            # select Distinct pay_code [Code],pay_description [Name]  from PAYTABLE where pay_isactive=1 Order By pay_description
            fk_id = self.get_sitelisting(empcode)

            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully",
            'error': False,'data': fk_id}
        
            return Response(result, status=status.HTTP_200_OK)
    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        

class ReportTitleListAPIView(GenericAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get_report_titlelisting(self,sitecode):
        try:
            cursor = connection.cursor()
            # select TOP 1 product_license,ID,Title,Comp_Title1,Comp_Title2,Comp_Title3,Comp_Title4,Footer_1,Footer_2,Footer_3,Footer_4 from Title 
            # where 
            # --product_license=@siteCode
            # product_license in (Select Item From dbo.LISTTABLE(@siteCode,','))
            # order by ID
            cursor.execute("SELECT TOP(1) product_license,id,title,comp_title1,comp_title2,comp_title3,comp_title4,footer_1,footer_2,footer_3,footer_4  FROM Title WHERE product_license = %s  ORDER BY id;",[sitecode])
            res = dictfetchall(self, cursor)
            return res
        except Paytable.DoesNotExist:
            raise Exception('Paytable Does not Exist') 
    
    def post(self, request):
        try:    
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            from_date = self.request.data.get('from_date',None)
            to_date = self.request.data.get('to_date',None)
            report_title = self.request.data.get('report_title',None)
            if not from_date:
                raise Exception('Please give from_date !!') 
              
            if not to_date:
                raise Exception('Please give to_date !!') 

            if not report_title:
                raise Exception('Please give report_title !!') 

               
            site_code = self.request.data.get('site_code',None)
            if not site_code:
                raise Exception('Please give site_code !!') 
               
            
            site_codelst = site_code.split(",")
            site_least = ItemSitelist.objects.filter(itemsite_code__in=site_codelst).order_by('itemsite_id').first()
            if not site_least:
                raise Exception('Selected site doesnt exist !!') 
               

            from_date = datetime.datetime.strptime(str(from_date), "%Y-%m-%d").strftime("%d/%m/%Y")
            to_date = datetime.datetime.strptime(str(to_date), "%Y-%m-%d").strftime("%d/%m/%Y") 
            sitecode = site_least.itemsite_code
            fk_id = self.get_report_titlelisting(sitecode)
            # print(fk_id)

            now = datetime.datetime.now()
            dt_string = now.strftime("%d/%m/%Y | %H:%M:%S %I:%M:%S %p")
            vals = {'report_title': "Collection By Outlet",'outlet': site.itemsite_desc,
                'from_date': from_date, 'to_date':to_date ,'print_by': fmspw.pw_userlogin,
                'print_time': dt_string ,'site': site_code}
            if fk_id:
                fk_id[0].update(vals)
            else:
                vals.update({"product_license": "","id": "","title":"","comp_title1": "","comp_title2": "",
                "comp_title3": "","comp_title4": "","footer_1": "","footer_2": "","footer_3": "",
                "footer_4": ""})
                fk_id.append(vals)

                

            # print(fk_id,"fk_id")

            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully",
            'error': False,'data': fk_id}
        
            return Response(result, status=status.HTTP_200_OK)
    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        


class CollectionbyOutletViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = []
    serializer_class = []

    def get_sales_collection(self):
        pass

         
      

        return queryset

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            from_date = self.request.data.get('from_date',None)
            to_date = self.request.data.get('to_date',None)
            if not from_date:
                raise Exception('Please give from_date !!') 
              
            if not to_date:
                raise Exception('Please give to_date !!') 

              

            start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()

            serializer_class = ReportmasterSerializer
            
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
    

    def get(self,request):

        try:
            start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True).\
                exclude(itemsite_code__icontains="HQ").\
                values_list('itemsite_code', flat=True)

        if _siteCodes:
            site_code_list = _siteCodes.split(",")
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)
        site_code_q = ', '.join(['\''+str(code)+'\'' for code in site_code_list])
        raw_q = f"SELECT MAX(e.display_name) Consultant, " \
                        f"cast(SUM(pd.dt_deposit/100*ms.ratio) AS decimal(9,2)) amount, " \
                        f"pd.ItemSite_Code AS siteCode, MAX(e.emp_name) FullName " \
                f"FROM pos_daud pd " \
                f"INNER JOIN multistaff ms ON pd.sa_transacno = ms.sa_transacno and pd.dt_lineno = ms.dt_lineno " \
                f"LEFT JOIN employee e on ms.emp_code = e.emp_code " \
                f"WHERE pd.ItemSite_Code IN ({site_code_q})" \
                f"AND pd.sa_date BETWEEN '{start_date}' AND '{end_date}' " \
                f"GROUP BY ms.emp_code, pd.ItemSite_Code " \
                f"ORDER BY Amount DESC"

        with connection.cursor() as cursor:
            cursor.execute(raw_q)
            raw_qs = cursor.fetchall()
            desc = cursor.description
            # responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]
            # for row in raw_qs:
            data_list = []
            site_total_dict = {}
            for i,row in enumerate(raw_qs):
                _d = dict(zip([col[0] for col in desc], row))
                _d['id'] = i+1
                data_list.append(_d)
                site_total_dict[_d['Consultant']] = round(site_total_dict.get(_d['Consultant'], 0) + _d['amount'], 2)

            responseData = {"data": data_list, "chart": site_total_dict}
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
            return Response(result, status=status.HTTP_200_OK)
