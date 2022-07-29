from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.http import HttpResponse
from django.template.loader import get_template
from django.template.loader import render_to_string
import datetime
import os
import math
import os.path
import tempfile
import pdfkit
from xhtml2pdf import pisa
from io import BytesIO
from pyvirtualdisplay import Display
from Cl_beautesoft import settings
from cl_table.models import (GstSetting,PosTaud,PosDaud,PosHaud,Fmspw,Title,PackageDtl,PackageHdr,Treatment,
TreatmentAccount,DepositAccount,PrepaidAccount,TemplateSettings,CreditNote,Tempcustsign,Systemsetup)
from custom.models import ItemCart, RoundSales
from cl_table.serializers import PosdaudSerializer
from Cl_beautesoft.settings import BASE_DIR
from django.utils import timezone
from fpdf import FPDF 
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.db.models import Sum


def round_calc(value):
    val = "{:.2f}".format(float(value))
    fractional = math.modf(float(val))
    data = "{:.2f}".format(float(fractional[0]))
    split_d = str(data).split('.')
    con = "0.0"+split_d[1][-1]
    round_ids = RoundSales.objects.filter(sales=float(con)).first()
    rounded = 0.0
    if type(val) == 'str':
        if '-' in str(round_ids.roundvalue):
            split_value = str(round_ids.roundvalue).split('-')
            rounded = str(val) - split_value[1]
        elif '+' in str(round_ids.roundvalue):
            split = str(round_ids.roundvalue).split('+')
            rounded = str(val) + split_value[1]
    elif type(val) == 'float': 
        if '-' in str(round_ids.roundvalue):
            split_value = str(round_ids.roundvalue).split('-')
            rounded = float(val) - float(split_value[1])
        elif '+' in str(round_ids.roundvalue):
            split = str(round_ids.roundvalue).split('+')
            rounded = float(val) + float(split_value[1])        
    return rounded    

# def receipt_calculation(request, daud):
#     # cart_ids = ItemCart.objects.filter(isactive=True,Appointment=app_obj,is_payment=True)
#     gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
#     subtotal = 0.0; discount = 0.0;discount_amt=0.0;additional_discountamt=0.0; 
#     trans_amt=0.0 ;deposit_amt =0.0; tax_amt = 0.0; billable_amount=0.0; total_balance = 0.0;total_qty = 0
#     for ct in daud:
#         c = ct.itemcart
#         subtotal += float(ct.dt_deposit)
#         trans_amt += float(ct.dt_amt)
#         deposit_amt += float(ct.dt_deposit)
#         # total = "{:.2f}".format(float(c.price) * int(c.quantity))
#         #subtotal += float(c.total_price)
#         discount_amt += float(c.discount_amt)
#         additional_discountamt += float(c.additional_discountamt)
#         #trans_amt += float(c.trans_amt)
#         #deposit_amt += float(c.deposit)
#         balance = float(c.trans_amt) - float(c.deposit)
#         total_balance += float(balance)
#         total_qty += int(c.quantity)

#     # disc_percent = 0.0
#     # if discount_amt > 0.0:
#     #     disc_percent = (float(discount_amt) * 100) / float(net_deposit) 
#     #     after_line_disc = net_deposit
#     # else:
#     #     after_line_disc = net_deposit

#     # add_percent = 0.0
#     # if additional_discountamt > 0.0:
#     #     # print(additional_discountamt,"additional_discountamt")
#     #     add_percent = (float(additional_discountamt) * 100) / float(net_deposit) 
#     #     after_add_disc = after_line_disc 
#     # else:
#     #     after_add_disc = after_line_disc   

#     if gst.is_exclusive == True:
#         tax_amt = deposit_amt * (gst.item_value / 100)
#         billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
#     else:
#         billable_amount = "{:.2f}".format(deposit_amt)

#     sub_total = "{:.2f}".format(float(subtotal))
#     round_val = float(round_calc(billable_amount)) # round()
#     billable_amount = float(billable_amount) + round_val 
#     sa_Round = round_val
#     discount = discount_amt + additional_discountamt
#     itemvalue = "{:.2f}".format(float(gst.item_value))

#     value = {'subtotal':sub_total,'discount': "{:.2f}".format(float(discount)),'trans_amt': "{:.2f}".format(float(trans_amt)),
#     'deposit_amt': "{:.2f}".format(float(deposit_amt)),'tax_amt':"{:.2f}".format(float(tax_amt)),
#     'tax_lable': "Tax Amount"+"("+str(itemvalue)+" "+"%"+")",'sa_Round': "{:.2f}".format(float(sa_Round)),
#     'billable_amount': "{:.2f}".format(float(billable_amount)),'balance': "{:.2f}".format(float(balance)),
#     'total_balance': "{:.2f}".format(float(total_balance)),'total_qty':total_qty}
#     return value

# def receipt_calculation(daud):
#     # cart_ids = ItemCart.objects.filter(isactive=True,Appointment=app_obj,is_payment=True)
#     gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
#     subtotal = 0.0; discount = 0.0;discount_amt=0.0;additional_discountamt=0.0; 
#     trans_amt=0.0 ;deposit_amt =0.0; tax_amt = 0.0; billable_amount=0.0; total_balance = 0.0;total_qty = 0
#     for ct in daud:
#         c = ct.itemcart
#         # total = "{:.2f}".format(float(c.price) * int(c.quantity))
#         subtotal += float(ct.dt_deposit)
#         trans_amt += float(ct.dt_amt)
#         deposit_amt += float(ct.dt_deposit)
#         #subtotal += float(c.total_price)
#         discount_amt += float(c.discount_amt)
#         additional_discountamt += float(c.additional_discountamt)
#         #trans_amt += float(c.trans_amt)
#         #deposit_amt += float(c.deposit)
#         balance = float(c.trans_amt) - float(c.deposit)
#         total_balance += float(balance)
#         total_qty += int(c.quantity)

#     if gst.is_exclusive == True:
#         tax_amt = deposit_amt * (gst.item_value / 100)
#         billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
#     else:
#         billable_amount = "{:.2f}".format(deposit_amt)

#     sub_total = "{:.2f}".format(float(subtotal))
#     round_val = float(round_calc(billable_amount)) # round()
#     billable_amount = float(billable_amount) + round_val 
#     sa_Round = round_val
#     discount = discount_amt + additional_discountamt
#     itemvalue = "{:.2f}".format(float(gst.item_value))

#     value = {'subtotal':sub_total,'discount': "{:.2f}".format(float(discount)),'trans_amt': "{:.2f}".format(float(trans_amt)),
#     'deposit_amt': "{:.2f}".format(float(deposit_amt)),'tax_amt':"{:.2f}".format(float(tax_amt)),
#     'tax_lable': "Tax Amount"+"("+str(itemvalue)+" "+"%"+")",'sa_Round': "{:.2f}".format(float(sa_Round)),
#     'billable_amount': "{:.2f}".format(float(billable_amount)),'balance': "{:.2f}".format(float(balance)),
#     'total_balance': "{:.2f}".format(float(total_balance)),'total_qty':total_qty}
#     return value


def GeneratePDF(self,request, sa_transacno):
    fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
    site = fmspw.loginsite 
    #sa_transacno = request.GET.get('sa_transacno',None)
    template_path = 'customer_receipt.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Customer Receipt Report.pdf"'
    gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
    #hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,ItemSite_Codeid__pk=site.pk).only('sa_transacno','ItemSite_Codeid').order_by("id")[:1]
    hdr = PosHaud.objects.filter(sa_transacno=sa_transacno).only('sa_transacno','ItemSite_Codeid').order_by("-id")[:1]
    if not hdr:
        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Does not exist in this outlet!!",'error': True} 
        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)   

    daud = PosDaud.objects.filter(sa_transacno=sa_transacno)
    if not daud:
        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"sa_transacno PosDaud Does not exist!!",'error': True}
        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)   
    
    taud = PosTaud.objects.filter(sa_transacno=sa_transacno)
    if not taud:
        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"sa_transacno Does not exist!!",'error': True} 
        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)   
    
    tot_qty = 0;tot_trans = 0 ; tot_depo = 0; tot_bal = 0;balance = 0;tot_price = 0;tot_disc =0
    total_netprice = 0
    dtl_serializer = PosdaudSerializer(daud, many=True)
    dtl_data = dtl_serializer.data
    for dat in dtl_data:
        d = dict(dat)
        #d_obj = PosDaud.objects.filter(pk=d['id'],ItemSite_Codeid__pk=site.pk).first()
        d_obj = PosDaud.objects.filter(pk=d['id']).first()
        tot_price += d_obj.dt_price
        total_netprice += d_obj.dt_price * d_obj.dt_qty
        package_desc = []; packages = ""
        if d['record_detail_type'] == "PACKAGE":
            package_dtl = PackageDtl.objects.filter(package_code=d['dt_combocode'],isactive=True)
            for i in package_dtl:
                desc = i.description
                package_desc.append(desc)
            packages = tuple(package_desc)

        if d['dt_status'] == 'SA' and d['record_detail_type'] == "TD":
            d['dt_transacamt'] = ""
            d['dt_deposit'] = ""
            balance = ""
            d['balance'] = ""
        else:    
            d['dt_transacamt'] = "{:.2f}".format(float(d_obj.dt_amt))
            d['dt_deposit'] = "{:.2f}".format(float(d['dt_deposit']))
            balance = float(d_obj.dt_amt) - float(d['dt_deposit'])
            d['balance'] = "{:.2f}".format(float(balance))
            tot_trans += float(d_obj.dt_amt)
            tot_depo += float(d['dt_deposit'])
            tot_bal += float(balance)
            
        tot_qty += int(d['dt_qty'])
        totdisc = d_obj.dt_price - d_obj.dt_promoprice
        tot_disc += totdisc
        
            
        # app_obj = Appointment.objects.filter(pk=d['Appointment']).first()
        # sales = "";service = ""
        # if 'itemcart' in d:
        #     cartobj = ItemCart.objects.filter(pk=d['itemcart']).first()
        #     if cartobj:
        #         if cartobj.sales_staff.all():
        #             for i in cartobj.sales_staff.all():
        #                 if sales == "":
        #                     sales = sales + i.display_name
        #                 elif not sales == "":
        #                     sales = sales +","+ i.display_name
        #         if cartobj.service_staff.all(): 
        #             for s in cartobj.service_staff.all():
        #                 if service == "":
        #                     service = service + s.display_name
        #                 elif not service == "":
        #                     service = service +","+ s.display_name 
        
        
        # daud_obj = PosDaud.objects.filter(pk=d['id']).first()
        # daud_obj.staffs = sales +" "+"/"+" "+ service
        # daud_obj.save()

        # if d['record_detail_type'] == "TD":
        #     d['staffs'] = "/"+ service
        # else:
        #     d['staffs'] = sales +" "+"/"+" "+ service
            
    # value = receipt_calculation(daud)
    # sub_data = {'subtotal': "{:.2f}".format(float(value['subtotal'])),'total_disc':"{:.2f}".format(float(value['discount'])),
    #         'trans_amt':"{:.2f}".format(float(value['trans_amt'])),'deposit_amt':"{:.2f}".format(float(value['deposit_amt'])),
    #         'tax_amt':"{:.2f}".format(float(value['tax_amt'])),'tax_lable': value['tax_lable'],
    #         'billing_amount':"{:.2f}".format(float(value['billable_amount'])),'balance':"{:.2f}".format(float(value['balance'])),
    #         'total_balance':"{:.2f}".format(float(value['total_balance'])),'total_qty': value['total_qty']} 
    
    #gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
    if gst and gst.is_exclusive == True and gst.item_value:
        tax_amt = tot_depo * (gst.item_value / 100)
        billable_amount = "{:.2f}".format(tot_depo + tax_amt)
    else:
        billable_amount = "{:.2f}".format(tot_depo)

    tot_payamt = 0.0
    for ta in taud:
        pay_amt = float(ta.pay_amt)
        tot_payamt += pay_amt


    sub_data = {'total_qty':str(tot_qty),'trans_amt':str("{:.2f}".format((tot_trans))),
    'deposit_amt':str("{:.2f}".format((tot_depo))),'total_balance':str("{:.2f}".format((tot_bal))),
    'subtotal':str("{:.2f}".format((tot_depo))),'billing_amount':"{:.2f}".format(float(tot_payamt)),
    'tot_disc':str("{:.2f}".format((tot_disc)))}

    split = str(hdr[0].sa_date).split(" ")
    #date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime('%d.%m.%Y')
    esplit = str(hdr[0].sa_time).split(" ")
    Time = str(esplit[1]).split(":")

    time = Time[0]+":"+Time[1]
    day = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime('%a')
    title = Title.objects.filter(product_license=site.itemsite_code).first()
    path = None
    if title and title.logo_pic:
        path = BASE_DIR + title.logo_pic.url
    print(path,"path")    
    taud_f = PosTaud.objects.filter(sa_transacno=sa_transacno,ItemSIte_Codeid__pk=site.pk).first()


    date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime("%d-%b-%Y")

    #treatopen_ids = Treatment.objects.filter(cust_code=hdr[0].sa_custno,
    #site_code=site.itemsite_code,status='Open').values('item_code','course').annotate(total=Count('item_code'))
    treatopen_ids = Treatment.objects.filter(cust_code=hdr[0].sa_custno,
    status='Open').values('item_code','course').annotate(total=Count('item_code'))
    
    set_obj = False
    # if site.inv_templatename:
    #     set_obj = TemplateSettings.objects.filter(site_code=site.itemsite_code,template_name=site.inv_templatename).order_by('pk').first()
    #     if not set_obj:
    #         raise Exception('Template Settings not found') 

    pre_acc_ids = PrepaidAccount.objects.filter(cust_code=hdr[0].sa_custno,outstanding__gt = 0,status=True
    ).order_by('-pk').aggregate(balance=Coalesce(Sum('remain'), 0))
    # print(pre_acc_ids)
    if pre_acc_ids['balance'] > 0.0:
        prepaid_amt = "{:.2f}".format(pre_acc_ids['balance'])
    else:
        prepaid_amt = 0.0   
    credit = CreditNote.objects.filter(cust_code=hdr[0].sa_custno, status='OPEN'
    ).only('cust_code','status').order_by('pk').aggregate(amount=Coalesce(Sum('balance'), 0))
    if credit['amount'] > 0.0:
        credit_amt = "{:.2f}".format(credit['amount'])
    else:
        credit_amt = "0.00"  
    # print(credit,"credit") 
    custsign_ids = Tempcustsign.objects.filter(transaction_no=sa_transacno).order_by("-pk").first()

    path_custsign = None
    if custsign_ids and custsign_ids.cust_sig:
        path_custsign = BASE_DIR + custsign_ids.cust_sig.url
    # print(path_custsign,"path_custsign")

    prepaid_lst = []
    pre_queryset = PrepaidAccount.objects.filter(cust_code=hdr[0].sa_custno,
    status=True,remain__gt=0).only('site_code','cust_code','sa_status').order_by('-pk')
    if pre_queryset:
        for i in pre_queryset:
            val = {'pp_desc':i.pp_desc,'remain':"{:.2f}".format(i.remain)}
            prepaid_lst.append(val)

    prepaidbal_setup = Systemsetup.objects.filter(title='InvoiceSetting',
    value_name='showprepaidbalance',isactive=True).first()

    if prepaidbal_setup and prepaidbal_setup.value_data == 'True':
        prepaidbal = True
    else:
        prepaidbal = False

    treatmentbal_setup = Systemsetup.objects.filter(title='InvoiceSetting',
    value_name='showtreatmentbalance',isactive=True).first()
    if treatmentbal_setup and treatmentbal_setup.value_data == 'True':
        treatmentbal = True
    else:
        treatmentbal = False

    postaud_ids = PosTaud.objects.filter(sa_transacno=sa_transacno,pay_group="PREPAID")
    if postaud_ids:
        showprepaid = True
    else:
        showprepaid = False
    
    if hdr[0].isvoid == True and hdr[0].sa_status == "VT":
        showvoidreason = True
    else:
        showvoidreason = False

    cretaud_ids = PosTaud.objects.filter(sa_transacno=sa_transacno,pay_group="Credit")
    if cretaud_ids:
        showcredit = True
    else:
        showcredit = False
    
    creditlst = []
    credit_ids = CreditNote.objects.filter(cust_code=hdr[0].sa_custno, status='OPEN').only('cust_code','status').order_by('-pk','-sa_date')
    if credit_ids:
        for ce in credit_ids:
            cval = {'creditnote_no':ce.credit_code,'balance':"{:.2f}".format(ce.balance) if ce.balance else "0.00"}
            creditlst.append(cval)


    # print(treatopen_ids,"treatopen_ids")
    data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
    'address': title.trans_h2 if title and title.trans_h2 else '', 
    'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
    'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
    'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
    'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
    'footer5':title.trans_footer5 if title and title.trans_footer5 else '',
    'footer6':title.trans_footer6 if title and title.trans_footer6 else '',
    'hdr': hdr[0], 'daud':daud,'taud_f':taud_f,'postaud':taud,'day':day,'fmspw':fmspw,
    'date':date,'time':time,'percent':int(gst.item_value) if gst and gst.item_value else "0" ,'path':path if path else '','title':title if title else None,
    'packages': str(packages),'site':site,'treatment': treatopen_ids,'settings': set_obj,
    'tot_price':tot_price,'prepaid_balance': prepaid_amt,
    'creditnote_balance': credit_amt,'total_netprice':str("{:.2f}".format((total_netprice))),
    'custsign_ids':path_custsign if path_custsign else '','prepaid_lst':prepaid_lst,
    'prepaidbal':prepaidbal,'treatmentbal':treatmentbal,'showprepaid': showprepaid,
    'showvoidreason':showvoidreason,'showcredit':showcredit,'creditlst': creditlst}
    data.update(sub_data)
    if site.inv_templatename:
        template = get_template(site.inv_templatename)
    else:
        template = get_template('customer_receipt.html')


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
    
    # existing = os.listdir(settings.PDF_ROOT)
    dst ="customer_receipt_" + str(str(hdr[0].sa_transacno_ref)) + ".pdf"

    # src = settings.PDF_ROOT + existing[0] 
    # dst = settings.PDF_ROOT + dst 
        
    # os.rename(src, dst) 
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

            ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/customer_receipt_"+str(hdr[0].sa_transacno_ref)+".pdf"
    return ip_link


def customeraccount(cust_obj, site):
    tr_outstanding = 0.0; pr_outstanding = 0.0; pe_outstanding = 0.0

    #treat_ids = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code, type='Deposit', 
    #outstanding__gt = 0).order_by('pk')
    treat_ids = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,type='Deposit', 
    outstanding__gt = 0).order_by('pk')

    for i in treat_ids:
        #acc_ids = TreatmentAccount.objects.filter(ref_transacno=i.sa_transacno,
        #treatment_parentcode=i.treatment_parentcode,site_code=i.site_code).order_by('id').last()
        acc_ids = TreatmentAccount.objects.filter(ref_transacno=i.sa_transacno,
        treatment_parentcode=i.treatment_parentcode).order_by('sa_date','sa_time','id').last()

        if acc_ids and acc_ids.outstanding:   
            tr_outstanding += acc_ids.outstanding

    #depo_ids = DepositAccount.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code, type='Deposit', 
    #outstanding__gt=0).order_by('pk')  
    depo_ids = DepositAccount.objects.filter(cust_code=cust_obj.cust_code,type='Deposit', 
    outstanding__gt=0).order_by('pk')  
            
    for j in depo_ids:
        #dacc_ids = DepositAccount.objects.filter(ref_transacno=j.sa_transacno,
        #ref_productcode=j.treat_code,site_code=j.site_code).order_by('id').last()
        dacc_ids = DepositAccount.objects.filter(ref_transacno=j.sa_transacno,
        ref_productcode=j.treat_code).order_by('sa_date','sa_time','id').last()
        if dacc_ids and dacc_ids.outstanding:
            pr_outstanding += dacc_ids.outstanding

    #pre_ids = PrepaidAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
    #sa_status__in=['DEPOSIT','SA'],outstanding__gt = 0).only('site_code','cust_code','sa_status').order_by('pk') 
    pre_ids = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,
    sa_status__in=['DEPOSIT'],outstanding__gt = 0).only('site_code','cust_code','sa_status').order_by('pk') 
    
    for k in pre_ids:
        #last_acc_ids = PrepaidAccount.objects.filter(pp_no=k.pp_no,
        #site_code=k.site_code,status=True,line_no=k.line_no).only('pp_no','site_code','status','line_no').last()
        last_acc_ids = PrepaidAccount.objects.filter(pp_no=k.pp_no,
        status=True,line_no=k.line_no).only('pp_no','site_code','status','line_no').last()
        
        if last_acc_ids and last_acc_ids.outstanding:
            pe_outstanding += last_acc_ids.outstanding

    value = tr_outstanding + pr_outstanding + pe_outstanding
    return "{:.2f}".format(value)        

