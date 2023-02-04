from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from custom.models import ItemCart, RoundSales, VoucherRecord, PosPackagedeposit
from .serializers import PosdaudSerializer
from .models import (Employee,  Fmspw, Customer, Treatment, Stock, Appointment,ItemDept, ControlNo, 
Treatment_Master,ItemClass,Paytable,PosTaud,PayGroup,PosDaud,PosHaud,GstSetting,PayGroup,TreatmentAccount, 
ItemStatus,Source,ApptType, ItemHelper, Multistaff, DepositType, TmpItemHelper, PosDisc, FocReason, Holditemdetail,
DepositAccount,PrepaidAccount,PrepaidAccountCondition,VoucherCondition,ItemUom,Title,PackageHdr,PackageDtl,
ItemBatch,Stktrn,ItemUomprice,Tmptreatment,ExchangeDtl,Systemsetup,PackageAuditingLog,
TreatmentPackage,StudioWork,AppointmentLog,ItemBatchSno,Treatmentids)
from datetime import date, timedelta, datetime
import datetime
from django.utils import timezone
from custom.views import get_in_val
from cl_app.utils import general_error_response
from dateutil.relativedelta import relativedelta
from cl_app.models import ItemSitelist,Usagelevel,TreatmentUsage,TmpTreatmentSession
from django.db.models.functions import Coalesce,Concat
from django.db.models import Sum
import time
from django.db.models import Q


def customeraccount(cust_obj, site):
   
    tr_outstanding = 0.0; pr_outstanding = 0.0; pe_outstanding = 0.0

    #treat_ids = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code, type='Deposit', 
    #outstanding__gt = 0).order_by('pk')
    treat_ids = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,type='Deposit', 
    outstanding__gt = 0).order_by('pk')
    #acc_ids = TreatmentAccount.objects.filter(ref_transacno=treat_ids.sa_transacno,
    #treatment_parentcode=treat_ids.treatment_parentcode).order_by('sa_date','sa_time','id').last()
	
    for i in treat_ids:
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
        ref_productcode=j.treat_code).order_by('id').order_by('sa_date','sa_time','id').last()
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



def invoice_deposit(self, request, depo_ids, sa_transacno, cust_obj, outstanding, pay_date, pay_time):
    # try:
    if self:
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        empl = fmspw.Emp_Codeid
        id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0
        outstanding_new = 0.0
        gst = GstSetting.objects.filter(isactive=True,activefromdate__date__lte=pay_date,
        activetodate__date__gte=pay_date).first()
        
        is_autoappt = False
        for idx, c in enumerate(depo_ids, start=1):

            studio_setupids = Systemsetup.objects.filter(title='studioAbooking',
            value_name='studioAbooking',isactive=True).first()

            stk_setupids = Systemsetup.objects.filter(title='Stock Setting',value_name='Free Text',isactive=True).first()
            
            if is_autoappt == False and studio_setupids and studio_setupids.value_data == 'True' and int(c.itemcodeid.item_div) == 3 and c.itemcodeid.autoappointment == True:
                studio_ids = StudioWork.objects.filter(isactive=True).order_by('dateplus')
                if studio_ids:
                    if stk_setupids and stk_setupids.value_data:
                        isstockobj = Stock.objects.filter(pk=stk_setupids.value_data).order_by('item_seq').first()
                        if isstockobj:
                            for s in studio_ids:
                                aptctrl_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                if aptctrl_obj:
                                    staff = s.emp_id
                                    
                                    if staff:
                                        appt_code = str(aptctrl_obj.Site_Codeid.itemsite_code)+str(aptctrl_obj.control_prefix)+str(aptctrl_obj.control_no)
                                        linkcode =  appt_code
                                        
                                        invdate = datetime.datetime.strptime(str(pay_date), "%Y-%m-%d")
                                        apptdate = invdate + timedelta(days = s.dateplus)                       
                                        channel = ApptType.objects.filter(appt_type_code="10003",appt_type_isactive=True).first()

                                        appt_n = Appointment(cust_noid=cust_obj,cust_no=cust_obj.cust_code,appt_date=apptdate,
                                        appt_fr_time="10:00",Appt_typeid=channel if channel else None,appt_type=channel.appt_type_code if channel and channel.appt_type_code else None,
                                        appt_phone=cust_obj.cust_phone2,appt_remark=s.work,
                                        emp_noid=staff,emp_no=staff.emp_code if staff and staff.emp_code else None,emp_name=staff.display_name if staff and staff.display_name else None,
                                        cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
                                        appt_to_time="11:00",sa_transacno=sa_transacno,Appt_Created_Byid=fmspw,
                                        appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                                        Room_Codeid=None,room_code=None,
                                        Source_Codeid=None,source_code=None,
                                        cust_refer=cust_obj.cust_refer,requesttherapist=False,new_remark=None,
                                        item_code=isstockobj.item_code,
                                        linkcode=linkcode,add_duration="01:00",
                                        Item_Codeid=isstockobj,checktype="freetext",dt_lineno=c.lineno,
                                        sec_status=None,bookedby="Auto")
                                        
                                        appt_n.save()
                                        

                                        if appt_n.pk:
                                            aptctrl_obj.control_no = int(aptctrl_obj.control_no) + 1
                                            aptctrl_obj.save()
                                            is_autoappt = True

                                            apptlog = AppointmentLog(appt_id=appt_n,userid=empl,
                                            username=empl.display_name,appt_date=apptdate,
                                            appt_fr_time="10:00",appt_to_time="11:00",emp_code=staff.emp_code,newempcode=None,
                                            appt_status="Booking",sec_status=None,appt_remark=s.work,
                                            item_code=isstockobj.item_code,requesttherapist=False,add_duration="01:00",
                                            new_remark=None).save()

                                            


            if idx == 1:
                alsales_staff = c.sales_staff.all().first()

            # print(c,"cc")
            outstanding_acc =  float(c.trans_amt) - float(c.deposit)

           
            sales_staff = c.sales_staff.all().first()
            salesstaff = c.sales_staff.all()

            # total = c.price * c.quantity
            totQty += c.quantity
            # discount_amt += float(c.discount_amt)
            # additional_discountamt += float(c.additional_discountamt)
            total_disc += c.discount_amt + c.additional_discountamt
            totaldisc = c.discount_amt + c.additional_discountamt
            # dt_discPercent = (float(total_disc) * 100) / float(value['subtotal'])
            dt_discPercent = c.discount + c.additional_discount

            if c.is_foc == True:
                isfoc = True
                item_remarks = c.focreason.foc_reason_ldesc if c.focreason and c.focreason.foc_reason_ldesc else None 
                # dt_itemdesc = c.itemdesc +" "+"(FOC)"
                dt_itemdesc = c.itemdesc
            else:
                isfoc = False  
                item_remarks = None 
                dt_itemdesc = c.itemdesc
  
            dt_uom = None; dt_discuser = None ; lpackage = False; package_code = None; dt_combocode = None;record_detail_type = None
            
            if c.itemcodeid.Item_Divid.itm_code == '3':
                if c.itemcodeid.item_type == 'PACKAGE':
                    record_detail_type = "PACKAGE"
                    dt_combocode = c.itemcodeid.item_code
                else:    
                    record_detail_type = "SERVICE"
                # elif c.itemcodeid.item_type == 'COURSE':  
                #     record_detail_type = "PACKAGE"
                #     lpackage = True
                #     packobj = PackageDtl.objects.filter(code=str(c.itemcodeid.item_code)+"0000",isactive=True)
                #     if packobj:
                #         package_code = packobj[0].package_code

                dt_discuser = fmspw.pw_userlogin
            elif c.itemcodeid.Item_Divid.itm_code == '1':
                dt_uom = c.item_uom.uom_code if c.item_uom else None
                record_detail_type = "PRODUCT"
                dt_discuser = fmspw.pw_userlogin
            elif c.itemcodeid.Item_Divid.itm_code == '5':
                record_detail_type = "PREPAID" 
                dt_discuser = None   
            elif c.itemcodeid.Item_Divid.itm_code == '4':
                record_detail_type = "VOUCHER" 
                dt_discuser = None      

            calcgst = 0
            if gst:
                calcgst = gst.item_value if gst and gst.item_value else 0.0
            if calcgst > 0:
                sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
                if sitegst:
                    if sitegst.site_is_gst == False:
                        calcgst = 0
            # print(calcgst,"0 calcgst")
            # Yoonus Tax Chcking
            gst_amt_collect = 0
            if calcgst > 0:
                if site and site.is_exclusive == True:
                    gst_amt_collect = c.deposit * (calcgst/ 100)
                    # tax_amt = deposit_amt * (gst.item_value / 100)
                    # billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
                else:
                    gst_amt_collect = c.deposit * calcgst / (100+calcgst)
                    # billable_amount = "{:.2f}".format(deposit_amt)
                    # tax_amt = deposit_amt * gst.item_value / (100+gst.item_value)
                    # Yoonus
            # gst_amt_collect = c.deposit * (gst.item_value / 100)
                        
            sales = "";service = ""
            if c.sales_staff.all():
                for i in c.sales_staff.all():
                    if sales == "":
                        sales = sales + i.display_name
                    elif not sales == "":
                        sales = sales +","+ i.display_name
            if c.service_staff.all(): 
                for s in c.service_staff.all():
                    if service == "":
                        service = service + s.display_name
                    elif not service == "":
                        service = service +","+ s.display_name 


            dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
            dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=dt_itemdesc,dt_price=c.price,
            dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
            dt_discamt="{:.2f}".format(float(totaldisc)),
            dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            dt_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
            dt_discuser=dt_discuser,dt_combocode=dt_combocode,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
            dt_transacamt="{:.2f}".format(float(c.trans_amt)),dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,itemcart=c,
            st_ref_treatmentcode=None,record_detail_type=record_detail_type,gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
            topup_outstanding=outstanding_acc if outstanding_acc is not None and outstanding_acc > 0 else 0,dt_remark=c.remark if c.remark else None,isfoc=isfoc,item_remarks=item_remarks,
            dt_uom=dt_uom,first_trmt_done=False,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
            staffs=sales +" "+"/"+" "+ service)
            #appt_time=app_obj.appt_fr_time,                
            #st_ref_treatmentcode=treatment_parentcode,
            dtl.save()
            dtl.sa_date = pay_date
            dtl.sa_time = pay_time
            # print(dtl.sa_date,"dtl")
            dtl.save()
              
            if dtl.pk not in id_lst:
                id_lst.append(c.pk)

            
            

            #multi staff table creation
            ratio = 0.0
            if c.sales_staff.all().count() > 0:
                count = c.sales_staff.all().count()
                ratio = float(c.ratio) / float(count)

            # for sale in c.sales_staff.all():
            #     multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
            #     emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
            #     dt_lineno=c.lineno)
            #     multi.save()
                # print(multi.id,"multi")

            for sale in c.multistaff_ids.all():
                multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
                emp_code=sale.emp_code,ratio=sale.ratio,salesamt="{:.2f}".format(float(sale.salesamt)),type=None,isdelete=False,role=1,
                dt_lineno=c.lineno,salescommpoints=sale.salescommpoints)
                multi.save()  
                sale.sa_transacno = sa_transacno 
                sale.save()

            if int(c.itemcodeid.item_div) == 3 and c.itemcodeid.item_type == 'PACKAGE':
                packhdr_ids = PackageHdr.objects.filter(code=c.itemcodeid.item_code).first()
                if packhdr_ids:
                    packdtl_ids = PackageDtl.objects.filter(package_code=packhdr_ids.code,isactive=True)
                    if packdtl_ids:
                        for pa in packdtl_ids:
                            packdtl_code = str(pa.code)
                            itm_code = packdtl_code[:-4]
                            # print(itm_code,"itm_code")
                            # itmstock = Stock.objects.filter(item_code=itm_code,item_isactive=True).first()
                            itmstock = Stock.objects.filter(item_code=itm_code).first()
                            if itmstock:
                                pos_ids = PosPackagedeposit.objects.filter(itemcart=c,code=pa.code)
                                if pos_ids:
                                    p = pos_ids.first()
                                    pa_trasac = p.price * p.qty
                                    pa_deposit = p.deposit_amt
                                    #outstanding_acc =  float(c.trans_amt) - float(c.deposit)

                                    pa_outstanding_acc = float(pa_trasac) - float(pa_deposit)


                                    if int(itmstock.Item_Divid.itm_code) == 3 and itmstock.Item_Divid.itm_desc == 'SERVICES' and itmstock.Item_Divid.itm_isactive == True:
                                        pscontrolobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                        # if not pscontrolobj:
                                        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
                                        #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                        
                                        patreatment_parentcode = "TRM"+str(pscontrolobj.control_prefix)+str(pscontrolobj.Site_Codeid.itemsite_code)+str(pscontrolobj.control_no)
                                        pscontrolobj.control_no = int(pscontrolobj.control_no) + 1
                                        pscontrolobj.save()
                                        desc = "Total Service Amount : "+str("{:.2f}".format(float(pa_trasac)))
                                        
                                        # amount="{:.2f}".format(float(c.deposit)),
                                        # balance="{:.2f}".format(float(c.deposit)),deposit="{:.2f}".format(float(c.deposit))

                                        #treatment Account creation
                                        patreatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                                        description=desc,type="Deposit",amount="{:.2f}".format(float(pa_deposit)),
                                        balance="{:.2f}".format(float(pa_deposit)),User_Nameid=fmspw,
                                        user_name=fmspw.pw_userlogin,ref_transacno=sa_transacno,sa_transacno=sa_transacno,
                                        qty=p.qty,outstanding="{:.2f}".format(float(pa_outstanding_acc)) if pa_outstanding_acc is not None and pa_outstanding_acc > 0 else 0,deposit="{:.2f}".format(float(pa_deposit)),
                                        treatment_parentcode=patreatment_parentcode,sa_status="SA",
                                        cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                        sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),dt_lineno=c.lineno,
                                        package_code=packhdr_ids.code,
                                        Site_Codeid=site,site_code=site.itemsite_code,itemcart=c)
                                        patreatacc.save()
                                        patreatacc.sa_date = pay_date
                                        patreatacc.sa_time = pay_time
                                        patreatacc.save()

                                        # print(treatacc.id,"treatacc")
                                        if c.is_foc == True:
                                            courseval = itmstock.item_name +" "+"(FOC)"
                                            trisfoc_val = True
                                        else:
                                            courseval = itmstock.item_name 
                                            trisfoc_val = False
                                        
                                        expiry = None
                                        if itmstock and itmstock.service_expire_active == True:
                                            month = itmstock.service_expire_month
                                            if month:
                                                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                                                expiry = current_date + relativedelta(months=month)

                                        paqty = p.qty;dtl_st_ref_treatmentcode = "";dtl_first_trmt_done = False

                                        for i in range(1,int(paqty)+1):
                                            # treat = c
                                            # Price = c.trans_amt
                                            Price = pa_trasac
                                            # Unit_Amount = Price / c.quantity
                                            Unit_Amount = Price / paqty
                                            times = str(i).zfill(2)
                                            treatment_no = str(paqty).zfill(2)

                                        
                                            patreatmentid = Treatment(treatment_code=str(patreatment_parentcode)+"-"+str(times),
                                            treatment_parentcode=patreatment_parentcode,course=courseval,times=times,
                                            treatment_no=treatment_no,price="{:.2f}".format(float(Price)),unit_amount="{:.2f}".format(float(Unit_Amount)),Cust_Codeid=cust_obj,
                                            cust_code=cust_obj.cust_code,cust_name=cust_obj.cust_name,
                                            status="Open",item_code=str(itmstock.item_code)+"0000",Item_Codeid=itmstock,
                                            sa_transacno=sa_transacno,sa_status="SA",type="N",trmt_is_auto_proportion=False,
                                            dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,isfoc=trisfoc_val,
                                            treatment_account=patreatacc,service_itembarcode=str(itmstock.item_code)+"0000",
                                            package_code=packhdr_ids.code,expiry=expiry)
                                            patreatmentid.save()
                                            patreatmentid.treatment_date = pay_date
                                            patreatmentid.save()

                                            if patreatmentid: 
                                                stids = Treatmentids.objects.filter(treatment_int=patreatmentid.pk)
                                                if not stids: 
                                                    t_id =  Treatmentids(treatment_parentcode=patreatment_parentcode,
                                                    treatment_int=patreatmentid.pk).save()
                                                
                                            # apt_lst = []

                                            if c.helper_ids.exists():
    
                                                plink_flag = False
                                                if len(c.helper_ids.all().filter(times=times,pospackage=p)) > 1:
                                                    plink_flag = True

                                                for h in c.helper_ids.all().filter(times=times,pospackage=p):
                                                
                                                    # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                                                        
                                                    patreatmentid.status = "Done"
                                                    patreatmentid.trmt_room_code = h.Room_Codeid.room_code if h.Room_Codeid else None
                                                    # treatmentid.treatment_date = timezone.now()
                                                    patreatmentid.treatment_date = pay_date
                                                    patreatmentid.save()

                                                    # wp1 = h.workcommpoints / float(c.helper_ids.all().filter(times=times).count())
                                                    wp1 = h.wp1
                                                    pashare_amt = float(patreatmentid.unit_amount) / float(c.helper_ids.all().filter(times=times,pospackage=p).count())
                                                    if h.work_amt and h.work_amt > 0:
                                                        pashare_amt = h.work_amt
                                                    

                                                    TmpItemHelper.objects.filter(id=h.id).update(item_code=patreatment_parentcode+"-"+str(times),
                                                    item_name=itmstock.item_name,line_no=dtl.dt_lineno,sa_transacno=sa_transacno,
                                                    amount=patreatmentid.unit_amount,sa_date=pay_date,site_code=site.itemsite_code,
                                                    wp1=wp1,wp2=0.0,wp3=0.0)

                                                    # Item helper create
                                                    helper = ItemHelper(item_code=patreatment_parentcode+"-"+str(times),item_name=itmstock.item_desc,
                                                    line_no=dtl.dt_lineno,sa_transacno=sa_transacno,amount="{:.2f}".format(float(patreatmentid.unit_amount)),
                                                    helper_name=h.helper_name if h.helper_name else None,helper_code=h.helper_code if h.helper_code else None,
                                                    site_code=site.itemsite_code,share_amt="{:.2f}".format(float(pashare_amt)),helper_transacno=sa_transacno,
                                                    wp1=wp1,wp2=0.0,wp3=0.0,percent=h.percent,work_amt="{:.2f}".format(float(h.work_amt)) if h.work_amt else h.work_amt,session=h.session,
                                                    times=h.times,treatment_no=h.treatment_no)
                                                    helper.save()
                                                    ItemHelper.objects.filter(id=helper.id).update(sa_date=pay_date)
                                                    
                                                    # print(helper.sa_date,"helper")

                                                    #appointment treatment creation
                                                    # if h.appt_fr_time and h.appt_to_time != False and h.add_duration != False:

                                                    #     custprevappts = Appointment.objects.filter(appt_date=date.today(),
                                                    #     cust_no=cust_obj.cust_code).order_by('-pk').exclude(itemsite_code=site.itemsite_code)
                                                            
                                                    #     custprevtimeappts = Appointment.objects.filter(appt_date=date.today(),
                                                    #     cust_no=cust_obj.cust_code).filter(Q(appt_to_time__gte=h.appt_fr_time) & Q(appt_fr_time__lte=h.appt_to_time)).order_by('-pk')
                                                    

                                                    #     #staff having shift/appointment on other branch for the same time
                                                    
                                                    #     checkids = Appointment.objects.filter(appt_date=date.today(),emp_no=h.helper_id.emp_code,
                                                    #     ).filter(Q(appt_to_time__gt=h.appt_fr_time) & Q(appt_fr_time__lt=h.appt_to_time))
                                                    #     # print(check_ids,"check_ids")

                                                    #     if not custprevappts and not custprevtimeappts and not checkids:
                                                    #         stock_obj = itmstock

                                                    #         stk_duration = 60
                                                    #         if stock_obj.srv_duration:
                                                    #             if stock_obj.srv_duration is None or float(stock_obj.srv_duration) == 0.0:
                                                    #                 stk_duration = 60
                                                    #             else:
                                                    #                 stk_duration = int(stock_obj.srv_duration)

                                                    #         stkduration = int(stk_duration) + 30
                                                    #         # print(stkduration,"stkduration")

                                                    #         hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                                                    #         start_time =  get_in_val(self, h.appt_fr_time)
                                                    #         starttime = datetime.datetime.strptime(start_time, "%H:%M")

                                                    #         end_time = starttime + datetime.timedelta(minutes = stkduration)
                                                    #         endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                                                    #         duration = hrs

                                                    #         treat_all = Treatment.objects.filter(sa_transacno=sa_transacno,treatment_parentcode=patreatment_parentcode,site_code=site.itemsite_code)
                                                    #         length = [t.status for t in treat_all if t.status == 'Done']
                                                    #         if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
                                                    #             master_status = "Done"
                                                    #         else:
                                                    #             master_status = "Open"

                                                    #         master = Treatment_Master(treatment_code=str(patreatment_parentcode)+"-"+str(times),
                                                    #         treatment_parentcode=patreatment_parentcode,sa_transacno=sa_transacno,
                                                    #         course=stock_obj.item_desc,times=times,treatment_no=treatment_no,
                                                    #         price=stock_obj.item_price,cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,
                                                    #         cust_name=cust_obj.cust_name,status=master_status,unit_amount=stock_obj.item_price,
                                                    #         Item_Codeid=stock_obj,item_code=stock_obj.item_code,
                                                    #         sa_status="SA",dt_lineno=dtl.dt_lineno,type="N",duration=stkduration,
                                                    #         Site_Codeid=site,site_code=site.itemsite_code,
                                                    #         trmt_room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,Trmt_Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,
                                                    #         Item_Class=stock_obj.Item_Classid if stock_obj.Item_Classid else None,PIC=stock_obj.Stock_PIC if stock_obj.Stock_PIC else None,
                                                    #         start_time=h.appt_fr_time if h.appt_fr_time else None,end_time=h.appt_to_time if h.appt_to_time else None,add_duration=h.add_duration if h.add_duration else None,
                                                    #         appt_remark=stock_obj.item_desc if stock_obj.item_desc else None,requesttherapist=False)
                                                    #         master.save()
                                                    #         master.treatment_date = pay_date
                                                    #         master.save()
                                                    #         master.emp_no.add(h.helper_id.pk)
                                                    #         # print(master.id,"master")

                                                    #         ctrl_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                                    #         # if not ctrl_obj:
                                                    #         #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
                                                    #         #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                                            
                                                    #         appt_code = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                                                            
                                                    #         if apt_lst == []:
                                                    #             linkcode = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                                                    #         else:
                                                    #             app_obj = Appointment.objects.filter(pk=apt_lst[0]).order_by('pk').first()
                                                    #             linkcode = app_obj.linkcode

                                                    #         channel = ApptType.objects.filter(appt_type_code="10003",appt_type_isactive=True).first()
                                                    #         # if not channel:
                                                    #         #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
                                                    #         #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                                    #         # no need to add checktype & treat_parentcode for TD / service done appts

                                                    #         appt = Appointment(cust_noid=cust_obj,cust_no=cust_obj.cust_code,appt_date=pay_date,
                                                    #         appt_fr_time=h.appt_fr_time if h.appt_fr_time else None,Appt_typeid=channel if channel else None,appt_type=channel.appt_type_desc if channel.appt_type_desc else None,
                                                    #         appt_phone=cust_obj.cust_phone2,appt_remark=stock_obj.item_desc,
                                                    #         emp_noid=h.helper_id if h.helper_id else None,emp_no=h.helper_id.emp_code if h.helper_id.emp_code else None,emp_name=h.helper_id.display_name if h.helper_id.display_name else None,
                                                    #         cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
                                                    #         appt_to_time=h.appt_to_time if h.appt_to_time else None,Appt_Created_Byid=fmspw,
                                                    #         appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                                                    #         Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,
                                                    #         Source_Codeid=h.Source_Codeid if h.Source_Codeid else None,source_code=h.Source_Codeid.source_code if h.Source_Codeid else None,
                                                    #         cust_refer=cust_obj.cust_refer,requesttherapist=False,new_remark=h.new_remark,
                                                    #         item_code=stock_obj.item_code,sa_transacno=sa_transacno,treatmentcode=str(patreatment_parentcode)+"-"+str(times),
                                                    #         linkcode=linkcode,link_flag=plink_flag,add_duration=h.add_duration if h.add_duration else None,
                                                    #         Item_Codeid=stock_obj)
                                                            
                                                    #         appt.save()
                                                            

                                                    #         if appt.pk:
                                                    #             apt_lst.append(appt.pk)
                                                    #             master.Appointment = appt
                                                    #             master.appt_time = timezone.now()
                                                    #             master.save()
                                                    #             ctrl_obj.control_no = int(ctrl_obj.control_no) + 1
                                                    #             ctrl_obj.save()
                                                        
                                                #treatment Account creation for done treatment 01
                                                if c.helper_ids.all().filter(times=times,pospackage=p).first():
                                                    stock_obj = itmstock
                                                    #acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,
                                                    #treatment_parentcode=treatment_parentcode,Site_Codeid=site).order_by('id').last()
                                                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,
                                                    treatment_parentcode=patreatment_parentcode).order_by('sa_date','sa_time','id').last()

                                                    td_desc = str(times)+"/"+str(paqty)+" "+str(stock_obj.item_name)
                                                    balance = acc_ids.balance - float(patreatmentid.unit_amount) if acc_ids.balance else float(patreatmentid.unit_amount)

                                                    treatacc_td = TreatmentAccount(Cust_Codeid=cust_obj,
                                                    cust_code=cust_obj.cust_code,ref_no=patreatmentid.treatment_code,
                                                    description=td_desc,type='Sales',amount=-float("{:.2f}".format(float(patreatmentid.unit_amount))) if patreatmentid.unit_amount else 0.0,
                                                    balance="{:.2f}".format(float(balance)) if balance else 0.0,User_Nameid=fmspw,user_name=fmspw.pw_userlogin,
                                                    ref_transacno=patreatmentid.sa_transacno,
                                                    sa_transacno=sa_transacno,qty=1,outstanding="{:.2f}".format(float(acc_ids.outstanding)) if acc_ids and acc_ids.outstanding is not None and acc_ids.outstanding > 0 else 0,
                                                    deposit=None,treatment_parentcode=patreatmentid.treatment_parentcode,
                                                    sa_status="SA",cas_name=fmspw.pw_userlogin,
                                                    sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                                    sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                                                    dt_lineno=c.lineno,Site_Codeid=site,site_code=site.itemsite_code,
                                                    itemcart=c)
                                                    treatacc_td.save()
                                                    treatacc_td.sa_date = pay_date
                                                    treatacc_td.sa_time = pay_time
                                                    treatacc_td.save()
                                                    # print(treatacc_td.id,"treatacc_td")
                                                    dtl_first_trmt_done = True
                                                    if dtl_st_ref_treatmentcode == "":
                                                        dtl_st_ref_treatmentcode = str(patreatment_parentcode)+"-"+str(times)
                                                    elif not dtl_st_ref_treatmentcode == "":
                                                        dtl_st_ref_treatmentcode = str(dtl_st_ref_treatmentcode) +"-"+str(times)

                                                    #auto Treatment Usage transactions
                                                    now = datetime.datetime.now()
                                                    s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))
                                                    usagelevel_ids = Usagelevel.objects.filter(service_code=str(itmstock.item_code)+"0000",
                                                    isactive=True).order_by('-pk') 
                                                    valuedata = 'TRUE'

                                                    sys_ids = Systemsetup.objects.filter(title='Stock Available',value_name='Stock Available').first() 
                                                    if sys_ids:
                                                        valuedata = sys_ids.value_data

                                                    currenttime = timezone.now()
                                                    currentdate = timezone.now().date()
                                                        
                                                    for i in usagelevel_ids: 
                                                        TreatmentUsage(treatment_code=patreatmentid.treatment_code,item_code=i.item_code,
                                                        item_desc=i.item_desc,qty=i.qty,uom=i.uom,site_code=site.itemsite_code,usage_status="Usage",
                                                        line_no=1,usage_update=s1,sa_transacno=sa_transacno).save()
                                                        if int(i.qty) > 0:
                                                            qtytodeduct = int(i.qty)

                                                            batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=i.item_code[:-4],
                                                            uom=i.uom).order_by('pk').last() 
                                                            obatchids = ItemBatch.objects.none()

                                                            uom_ids = ItemUomprice.objects.filter(item_code=i.item_code[:-4],item_uom2=i.uom
                                                            ,uom_unit__gt=0,isactive=True).first()
                                                            if uom_ids:
                                                                obatchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(i.item_code[:-4]),
                                                                uom=uom_ids.item_uom).order_by('pk').last() 


                                                            stockreduce = False
                                                            if valuedata == 'TRUE':
                                                                if (batchids and int(batchids.qty) >= int(i.qty)) or (obatchids and int(obatchids.qty) >= int(qtytodeduct)):
                                                                    stockreduce = True
                                                            else:
                                                                stockreduce = True     

                                                            if stockreduce == True:
                                                                #ItemBatch
                                                                if batchids and int(batchids.qty) >= int(qtytodeduct):
                                                                    deduct = batchids.qty - qtytodeduct
                                                                    batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())

                                                                    
                                                                    post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                                                    stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                                                    item_uom=i.uom).order_by('pk').last() 


                                                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=patreatmentid.treatment_code,trn_date=currentdate,
                                                                    trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                                                    trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                                                    trn_amt=None,trn_post=currentdate,
                                                                    trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                                                    hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                                                    line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                                    stock_in=None,trans_package_line_no=None)
                                                                    stktrn_id.save()
                                                                    Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                                                                
                                                                else:
                                                                    flag = False

                                                                    adcontrolobj = ControlNo.objects.filter(control_description__iexact="ADJS",
                                                                    site_code=fmspw.loginsite.itemsite_code).first()

                                                                    adjno = False
                                                                    if adcontrolobj:
                                                                        adjno = "W"+str(adcontrolobj.control_prefix)+str(adcontrolobj.site_code)+str(adcontrolobj.control_no)


                                                                    if batchids and obatchids and int(obatchids.qty) >= int(qtytodeduct):

                                                                        post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                                                        stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                                                        item_uom=uom_ids.item_uom).order_by('pk').last() 


                                                                        stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno if adjno else patreatmentid.treatment_code,trn_date=currentdate,
                                                                        trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=-1,trn_balqty=obatchids.qty-1,
                                                                        trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                                                        trn_amt=None,trn_post=currentdate,
                                                                        trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                                                        hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                                                        line_no=c.lineno,item_uom=uom_ids.item_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                                        stock_in=None,trans_package_line_no=None)
                                                                        stktrn_id.save()
                                                                        Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                                                                        

                                                                        stktrnids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                                                        item_uom=i.uom).order_by('pk').last() 


                                                                        stktrnid = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno,trn_date=currentdate,
                                                                        trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=uom_ids.uom_unit,trn_balqty=uom_ids.uom_unit,
                                                                        trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                                                        trn_amt=None,trn_post=currentdate,
                                                                        trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                                                        hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                                                        line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                                        stock_in=None,trans_package_line_no=None)
                                                                        stktrnid.save()
                                                                        Stktrn.objects.filter(pk=stktrnid.pk).update(trn_post=pay_date,trn_date=pay_date)
                                                                    

                                                                        fbatch_qty = (batchids.qty + uom_ids.uom_unit) - qtytodeduct

                                                                        vstk = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=patreatmentid.treatment_code,trn_date=currentdate,
                                                                        trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=fbatch_qty,
                                                                        trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                                                        trn_amt=None,trn_post=currentdate,
                                                                        trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                                                        hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                                                        line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                                        stock_in=None,trans_package_line_no=None)
                                                                        vstk.save()
                                                                        Stktrn.objects.filter(pk=vstk.pk).update(trn_post=pay_date,trn_date=pay_date)
                                                                    


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
                                                                            batch_id = ItemBatch(item_code=i.item_code[:-4],site_code=site.itemsite_code,
                                                                            batch_no="",uom=i.uom,qty=-qtytodeduct,exp_date=None,batch_cost=None).save()
                                                                            deduct = -qtytodeduct

                                                                        #Stktrn
                                                                        currenttime = timezone.now()
                                                                        currentdate = timezone.now().date()
                                                                
                                                                        post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                                                        stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                                                        item_uom=i.uom).order_by('pk').last() 

                                                                        stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=patreatmentid.treatment_code,trn_date=currentdate,
                                                                        trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                                                        trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                                                        trn_amt=None,trn_post=currentdate,
                                                                        trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                                                        hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                                                        line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                                        stock_in=None,trans_package_line_no=None)
                                                                        stktrn_id.save()
                                                                        Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                                        

                                            
                                            patreatmentid.save()
                                            # appt_time=treat.appt_time,Trmt_Room_Codeid=treat.Trmt_Room_Codeid,trmt_room_code=treat.trmt_room_code,
                                            # print(treatmentid.id,"treatment_id")

                                        # if treatacc and treatmentid:
                                        #     controlobj.control_no = int(controlobj.control_no) + 1
                                        #     controlobj.save()

                                        # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
                                        dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
                                        dtl.first_trmt_done = dtl_first_trmt_done
                                        # dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
                                        # dtl.first_trmt_done_staff_name = ','.join([v.helper_id.display_name for v in c.helper_ids.all() if v.helper_id.display_name])
                                        dtl.first_trmt_done_staff_code = ','.join([v.emp_code for v in c.service_staff.all() if v.emp_code])
                                        dtl.first_trmt_done_staff_name = ','.join([v.display_name for v in c.service_staff.all() if v.display_name])
                                    
                                        dtl.save()


                                        if patreatacc:
                                           
                                            p.sa_transacno = sa_transacno
                                            p.status = "COMPLETED"
                                            p.save()

                                        if patreatment_parentcode:
                                            search_ids = TreatmentPackage.objects.filter(treatment_parentcode=patreatment_parentcode)
                                            if not search_ids:
                                                tpdone_ids = Treatment.objects.filter(treatment_parentcode=patreatment_parentcode,status="Done").order_by('pk').count()
                                                tpcancel_ids = Treatment.objects.filter(treatment_parentcode=patreatment_parentcode,status="Cancel").order_by('pk').count()
                                                tpopen_ids = Treatment.objects.filter(treatment_parentcode=patreatment_parentcode,status="Open").order_by('pk').count()
                                                

                                                trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=patreatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                                                
                                              

                                                tr = TreatmentPackage(treatment_parentcode=patreatment_parentcode,
                                                item_code=str(patreatmentid.Item_Codeid.item_code)+"0000",course=patreatmentid.course,
                                                treatment_no=patreatmentid.treatment_no,open_session=tpopen_ids,done_session=tpdone_ids,
                                                cancel_session=tpcancel_ids,expiry_date=patreatmentid.expiry,unit_amount=patreatmentid.unit_amount,
                                                customerid=cust_obj,cust_name=patreatmentid.cust_name,cust_code=patreatmentid.cust_code,
                                                treatment_accountid=patreatmentid.treatment_account,totalprice=patreatmentid.price,
                                                type=patreatmentid.type,
                                                Item_Codeid=patreatmentid.Item_Codeid,treatment_limit_times=patreatmentid.treatment_limit_times,
                                                Site_Codeid=patreatmentid.Site_Codeid,site_code=patreatmentid.site_code,
                                                sa_transacno=sa_transacno,lastsession_unit_amount=patreatmentid.unit_amount,
                                                balance="{:.2f}".format(float(trmtAccObj.balance)),outstanding="{:.2f}".format(float(trmtAccObj.outstanding)),
                                                )
                                                tr.save()
                                                datetimed = datetime.datetime.strptime(str(pay_date)+" "+str(time.strftime("%H:%M:%S")), "%Y-%m-%d %H:%M:%S")
                                                tr.treatment_date = datetimed
                                                tr.save()

                                                treatmids = list(set(Treatment.objects.filter(
                                                treatment_parentcode=patreatment_parentcode).filter(~Q(status="Open")).only('pk').order_by('pk').values_list('pk', flat=True).distinct()))

                                                Treatmentids.objects.filter(treatment_parentcode=patreatment_parentcode,
                                                treatment_int__in=treatmids).delete()
                                                
                                                p_ids = list(set(Treatmentids.objects.filter(treatment_parentcode=patreatment_parentcode).values_list('treatment_int', flat=True).distinct()))
                                                op_ids = list(Treatment.objects.filter(
                                                treatment_parentcode=patreatment_parentcode).filter(Q(status="Open"),~Q(pk__in=p_ids)).only('pk').order_by('pk').values_list('pk', flat=True).distinct())
                                                if op_ids:
                                                    for j in op_ids:
                                                        stf_ids = Treatmentids.objects.filter(treatment_int=j)
                                                        if not stf_ids: 
                                                            Treatmentids(treatment_parentcode=patreatment_parentcode,
                                                                        treatment_int=j).save()
                           
                





                                    elif int(itmstock.Item_Divid.itm_code) == 1 and itmstock.Item_Divid.itm_desc == 'RETAIL PRODUCT' and itmstock.Item_Divid.itm_isactive == True:
                                        desc = "Total Product Amount : "+str("{:.2f}".format(float(pa_trasac)))
                                        #Deposit Account creation
                                        
                                        padecontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                        # if not padecontrolobj:
                                        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                                        #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                        patreat_code = str(padecontrolobj.Site_Codeid.itemsite_code)+str(padecontrolobj.control_no)
                                        
                                        if c.is_foc == True:
                                            item_descriptionval = itmstock.item_name+" "+"(FOC)"
                                        else:
                                            item_descriptionval = itmstock.item_name
                                        
                                        # amount="{:.2f}".format(float(c.deposit)),
                                        # balance="{:.2f}".format(float(c.deposit)),deposit="{:.2f}".format(float(c.deposit))

                                        padepoacc = DepositAccount(cust_code=cust_obj.cust_code,type="Deposit",amount="{:.2f}".format(float(pa_deposit)),
                                        balance="{:.2f}".format(float(pa_deposit)),user_name=fmspw.pw_userlogin,qty=p.qty,outstanding="{:.2f}".format(float(pa_outstanding_acc)) if pa_outstanding_acc is not None and pa_outstanding_acc > 0 else 0,
                                        deposit="{:.2f}".format(float(pa_deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                        sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                                        deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
                                        sa_status="SA",item_barcode=packdtl_code,item_description=item_descriptionval,
                                        treat_code=patreat_code,void_link=None,lpackage=True,package_code=packhdr_ids.code,
                                        dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
                                        ref_transacno=sa_transacno,ref_productcode=patreat_code,Item_Codeid=itmstock,
                                        item_code=itmstock.item_code)
                                        padepoacc.save()
                                        padepoacc.sa_date = pay_date
                                        padepoacc.sa_time = pay_time
                                        padepoacc.save()
                                        # print(depoacc.pk,"depoacc")
                                        if padepoacc.pk:
                                            padecontrolobj.control_no = int(padecontrolobj.control_no) + 1
                                            padecontrolobj.save()
                                            p.sa_transacno = sa_transacno
                                            p.status = "COMPLETED"
                                            p.save()

                                        if p.hold_qty and int(p.hold_qty) > 0:
                                            p_con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                            # if not p_con_obj:
                                            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
                                            #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                            product_issues_no = str(p_con_obj.control_prefix)+str(p_con_obj.Site_Codeid.itemsite_code)+str(p_con_obj.control_no)
                                            
                                            hold = Holditemdetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
                                            transacamt=pa_trasac,itemno=itmstock.item_code+"0000",
                                            hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                            hi_itemdesc=itmstock.item_desc,hi_price=p.unit_price,hi_amt=pa_trasac,hi_qty=p.qty,
                                            hi_discamt=p.discount,hi_discpercent=p.discount,hi_discdesc=None,
                                            hi_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                                            hi_lineno=c.lineno,hi_uom=pa.uom if pa.uom else None,hold_item=True,hi_deposit=pa_deposit,
                                            holditemqty=p.hold_qty if p.hold_qty else None,status="OPEN",sa_custno=cust_obj.cust_code,
                                            sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
                                            product_issues_no=product_issues_no)
                                            hold.save()
                                            hold.sa_date = pay_date
                                            hold.sa_time = pay_time
                                            hold.save()
                                            # print(hold.pk,"hold")
                                            if hold.pk:
                                                p_con_obj.control_no = int(p_con_obj.control_no) + 1
                                                p_con_obj.save()
                                                dtl.holditemqty = int(p.hold_qty)
                                                dtl.save() 

                                        # Inventory Control
                                        qtytodeduct = p.qty
                                        if p.hold_qty and int(p.hold_qty) > 0:
                                            qtytodeduct = p.qty - int(p.hold_qty)

                                        if qtytodeduct > 0:
                                            batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(itmstock.item_code),
                                            uom=pa.uom).order_by('pk').last() 
                                            #ItemBatch
                                            if batchids:
                                                deduct = batchids.qty - qtytodeduct
                                                batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                                            else:
                                                batch_id = ItemBatch(item_code=itmstock.item_code,site_code=site.itemsite_code,
                                                batch_no="",uom=pa.uom,qty=-qtytodeduct,exp_date=None,batch_cost=itmstock.lstpo_ucst).save()
                                                deduct = -qtytodeduct

                                            #Stktrn
                                            currenttime = timezone.now()
                                            currentdate = timezone.now().date()
                                    
                                            post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                            stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(itmstock.item_code)+"0000",
                                            item_uom=pa.uom).order_by('pk').last() 

                                            stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(itmstock.item_code)+"0000",
                                            store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,trn_date=currentdate,
                                            trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                            trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                            trn_amt="{:.2f}".format(float(pa_deposit)),trn_post=currentdate,
                                            trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                            hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                            line_no=c.lineno,item_uom=pa.uom if pa.uom else None,item_batch=None,mov_type=None,item_batch_cost=None,
                                            stock_in=None,trans_package_line_no=None)
                                            stktrn_id.save()
                                            Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                                           
                            

                                    elif int(itmstock.Item_Divid.itm_code) == 5 and itmstock.Item_Divid.itm_desc == 'PREPAID' and itmstock.Item_Divid.itm_isactive == True:
                                        #Prepaid Account creation
                                        #exp_date need to map
                                        pprepaid_valid_period = None
                                        if itmstock and itmstock.prepaid_valid_period:
                                            pprepaid_valid_period = date.today() + timedelta(int(itmstock.prepaid_valid_period))
                                        ppbonus = itmstock.prepaid_value - itmstock.prepaid_sell_amt

                                        if c.is_foc == True:
                                            ppdescval = itmstock.item_name+" "+"(FOC)"
                                        else:
                                            ppdescval = itmstock.item_name

                                        if pa_outstanding_acc == 0:
                                            pre_remain = itmstock.prepaid_value
                                        else:
                                            pre_remain = pa_deposit    
                                        
                                        #remain=c.deposit
                                        paprepacc = PrepaidAccount(pp_no=sa_transacno,pp_type=itmstock.item_range if itmstock.item_range else None,
                                        pp_desc=ppdescval,exp_date=pprepaid_valid_period,cust_code=cust_obj.cust_code,
                                        cust_name=cust_obj.cust_name,pp_amt=itmstock.prepaid_sell_amt,pp_total=itmstock.prepaid_value,
                                        pp_bonus=ppbonus,transac_no="",item_no="",use_amt=0,remain=pre_remain,ref1="",
                                        ref2="",status=True,site_code=site.itemsite_code,sa_status="DEPOSIT",exp_status=True,
                                        voucher_no='',isvoucher=False,has_deposit=True,topup_amt=pa_deposit,
                                        outstanding=pa_outstanding_acc if pa_outstanding_acc is not None and pa_outstanding_acc > 0 else 0,active_deposit_bonus=True,topup_no="",topup_date=None,
                                        line_no=c.lineno,staff_name=','.join([v.display_name for v in salesstaff if v.display_name]),
                                        staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                        pp_type2=None,condition_type1=None,pos_daud_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,
                                        Item_Codeid=itmstock,item_code=itmstock.item_code,lpackage=True,package_code=packhdr_ids.code,
                                        package_code_lineno=p.deposit_lineno)
                                        paprepacc.save()
                                        paprepacc.sa_date = pay_date 
                                        paprepacc.start_date = pay_date
                                        paprepacc.save()
                                        # print(paprepacc.pk,"paprepacc")

                                        vo_obj = VoucherCondition.objects.filter(item_code=itmstock.item_code)
                                        # print(vo_obj,"vo_obj")
                                        #PrepaidAccountCondition Creation
                                        if vo_obj:  
                                            ppacc = PrepaidAccountCondition(pp_no=sa_transacno,pp_type=itmstock.item_range if itmstock.item_range else None,
                                            pp_desc=ppdescval,p_itemtype=','.join([v.p_itemtype for v in vo_obj if v.p_itemtype]),
                                            item_code=itmstock.item_code,conditiontype1=','.join([v.conditiontype1 for v in vo_obj if v.conditiontype1]),
                                            conditiontype2=','.join([v.conditiontype2 for v in vo_obj if v.conditiontype2]),
                                            amount=vo_obj.first().amount,rate=vo_obj.first().rate,use_amt=0,remain=pre_remain,
                                            pos_daud_lineno=c.lineno,lpackage=True,package_code=packhdr_ids.code,package_code_lineno=p.deposit_lineno)
                                            ppacc.save()
                                            # print(ppacc.pk,"ppacc")
                                            PrepaidAccount.objects.filter(pk=paprepacc.pk).update(pp_type2=ppacc.pp_type,
                                            condition_type1=ppacc.conditiontype1)


                                        p.sa_transacno = sa_transacno
                                        p.status = "COMPLETED"
                                        p.save()
    
                                    elif int(itmstock.Item_Divid.itm_code) == 4 and itmstock.Item_Divid.itm_desc == 'VOUCHER' and itmstock.Item_Divid.itm_isactive == True:
                                        pavorecontrolobj = ControlNo.objects.filter(control_description__iexact="Public Voucher",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                        # if not pavorecontrolobj:
                                        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher Record Control No does not exist!!",'error': True} 
                                        #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                        vouchercode = str(pavorecontrolobj.control_prefix)+str(pavorecontrolobj.Site_Codeid.itemsite_code)+str(pavorecontrolobj.control_no)
                                        vopercent = None
                                        if itmstock.voucher_value_is_amount == True:
                                            vopercent = 0
                                        else:
                                            if itmstock.voucher_value_is_amount == False:
                                                vopercent = itmstock.voucher_value
                                        
                                        end_date = None
                                        if itmstock.voucher_valid_period:
                                            date_1 = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                                            # print(date_1,"date_1")
                                            end_date = date_1 + datetime.timedelta(days=int(itmstock.voucher_valid_period))
                                            # print(end_date,"end_date")
                                            # tod_now = datetime.now(pytz.timezone(TIME_ZONE))
                                            # print(tod_now,"tod_now")
                                            # voexpiry = tod_now + datetime.timedelta(days=c.itemcodeid.voucher_valid_period)
                                            # print(voexpiry,"voexpiry")
                                            # expiry = datetime.datetime.combine(end_date, datetime.datetime.min.time())

                                            # expiry = end_date.strftime("%d-%m-%Y")
                                            # print(expiry,"expiry") 

                                        if c.is_foc == True:
                                            vouchernameval = itmstock.item_name+" "+"(FOC)"
                                        else:
                                            vouchernameval = itmstock.item_name    
                                        
                                        #value=c.price
                                        vorec = VoucherRecord(sa_transacno=sa_transacno,voucher_name=vouchernameval,
                                        voucher_no=vouchercode,value=p.ttl_uprice,cust_codeid=cust_obj,cust_code=cust_obj.cust_code,
                                        cust_name=cust_obj.cust_name,percent=vopercent,site_codeid=site,site_code=site.itemsite_code,
                                        issued_expiry_date=end_date if end_date else None,issued_staff=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                        onhold=0,paymenttype=None,remark=None,type_code=pavorecontrolobj.control_prefix,used=0,
                                        ref_fullvoucherno=None,ref_rangefrom=None,ref_rangeto=None,site_allocate=None,dt_lineno=c.lineno)
                                        vorec.save()
                                        vorec.sa_date = pay_date
                                        vorec.save()
                                        if vorec.pk:
                                            pavorecontrolobj.control_no = int(pavorecontrolobj.control_no) + 1
                                            pavorecontrolobj.save()
                                            p.sa_transacno = sa_transacno
                                            p.status = "COMPLETED"
                                            p.save()
                        
            else:
                if int(c.itemcodeid.Item_Divid.itm_code) == 3 and c.itemcodeid.Item_Divid.itm_desc == 'SERVICES' and c.itemcodeid.Item_Divid.itm_isactive == True:
                    controlobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    # if not controlobj:
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
                    #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                    treatment_parentcode = "TRM"+str(controlobj.control_prefix)+str(controlobj.Site_Codeid.itemsite_code)+str(controlobj.control_no)
                    controlobj.control_no = int(controlobj.control_no) + 1
                    controlobj.save()
                    
                    desc = "Total Service Amount : "+str("{:.2f}".format(float(c.trans_amt)))

                    #treatment Account creation
                    treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                    description=desc,type="Deposit",amount="{:.2f}".format(float(c.deposit)),
                    balance="{:.2f}".format(float(c.deposit)),User_Nameid=fmspw,
                    user_name=fmspw.pw_userlogin,ref_transacno=sa_transacno,sa_transacno=sa_transacno,
                    qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)) if outstanding_acc is not None and outstanding_acc > 0 else 0,deposit="{:.2f}".format(float(c.deposit)),
                    treatment_parentcode=treatment_parentcode,sa_status="SA",
                    cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                    sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),dt_lineno=c.lineno,
                    Site_Codeid=site,site_code=site.itemsite_code,itemcart=c,
                    package_code=package_code)
                    treatacc.save()
                    treatacc.sa_date = pay_date
                    treatacc.sa_time = pay_time
                    treatacc.save()
                    
                        

                    # print(treatacc.id,"treatacc")
                elif int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
                    desc = "Total Product Amount : "+str("{:.2f}".format(float(c.trans_amt)))
                    #Deposit Account creation
                    
                    decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    # if not decontrolobj:
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                    #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)
                    
                    if c.is_foc == True:
                        item_descriptionval = c.itemcodeid.item_name+" "+"(FOC)"
                    else:
                        item_descriptionval = c.itemcodeid.item_name
                    

                    depoacc = DepositAccount(cust_code=cust_obj.cust_code,type="Deposit",amount="{:.2f}".format(float(c.deposit)),
                    balance="{:.2f}".format(float(c.deposit)),user_name=fmspw.pw_userlogin,qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)) if outstanding_acc is not None and outstanding_acc > 0 else 0,
                    deposit="{:.2f}".format(float(c.deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                    sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                    deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
                    sa_status="SA",item_barcode=str(c.itemcodeid.item_code)+"0000",item_description=item_descriptionval,
                    treat_code=treat_code,void_link=None,lpackage=None,package_code=None,
                    dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
                    ref_transacno=sa_transacno,ref_productcode=treat_code,Item_Codeid=c.itemcodeid,
                    item_code=c.itemcodeid.item_code)
                    depoacc.save()
                    depoacc.sa_date = pay_date
                    depoacc.sa_time = pay_time

                    depoacc.save()
                    # print(depoacc.pk,"depoacc")
                    if depoacc.pk:
                        decontrolobj.control_no = int(decontrolobj.control_no) + 1
                        decontrolobj.save()

                    if c.batch_sno:
                        dtl.dt_itemdesc = dtl.dt_itemdesc+" "+"SN-"+str(c.batch_sno)
                        batchso_ids = ItemBatchSno.objects.filter(batch_sno__icontains=c.batch_sno,
                        availability=True).first()
                        if batchso_ids and batchso_ids.exp_date:
                            dx_split = str(batchso_ids.exp_date).split(" ")
                            exp_rdate = datetime.datetime.strptime(str(dx_split[0]), '%Y-%m-%d').strftime("%d/%m/%Y")
                            dtl.dt_itemdesc = dtl.dt_itemdesc+" "+", Expiry Date : "+str(exp_rdate)
                        
                        if batchso_ids:
                            batchso_ids.availability = False
                            batchso_ids.save()

                        dtl.save()    
                    
                    currenttime = timezone.now()
                    currentdate = timezone.now().date()
                    
                    # Inventory Control
                    qtytodeduct = c.quantity
                    if c.holditemqty and int(c.holditemqty) > 0:
                        qtytodeduct = c.quantity - int(c.holditemqty)

                    if qtytodeduct > 0:
                        batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(c.itemcodeid.item_code),
                        uom=c.item_uom.uom_code).order_by('pk').last() 
                        #ItemBatch
                        if batchids and batchids.qty >= qtytodeduct:
                            deduct = batchids.qty - qtytodeduct
                            batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())

                            
                            post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                            stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(c.itemcodeid.item_code)+"0000",
                            item_uom=c.item_uom.uom_code).order_by('pk').last() 

                            stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(c.itemcodeid.item_code)+"0000",
                            store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,trn_date=currentdate,
                            trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                            trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                            trn_amt="{:.2f}".format(float(c.deposit)),trn_post=currentdate,
                            trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                            hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                            line_no=c.lineno,item_uom=c.item_uom.uom_code,item_batch=None,mov_type=None,item_batch_cost=None,
                            stock_in=None,trans_package_line_no=None)
                            stktrn_id.save()
                            Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                           
                        else:
                            flag = False

                            adcontrolobj = ControlNo.objects.filter(control_description__iexact="ADJS",
                            site_code=fmspw.loginsite.itemsite_code).first()

                            adjno = False
                            if adcontrolobj:
                                adjno = "W"+str(adcontrolobj.control_prefix)+str(adcontrolobj.site_code)+str(adcontrolobj.control_no)


                            uom_ids = ItemUomprice.objects.filter(item_code=c.itemcodeid.item_code,item_uom2=c.item_uom.uom_code
                            ,uom_unit__gt=0,isactive=True).first()
                            if uom_ids:
                                obatchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(c.itemcodeid.item_code),
                                uom=uom_ids.item_uom).order_by('pk').last() 
                                if batchids and obatchids and obatchids.qty > 0:

                                    post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                    stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(c.itemcodeid.item_code)+"0000",
                                    item_uom=uom_ids.item_uom).order_by('pk').last() 


                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(c.itemcodeid.item_code)+"0000",
                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno if adjno else sa_transacno,trn_date=currentdate,
                                    trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=-1,trn_balqty=obatchids.qty-1,
                                    trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                    trn_amt="{:.2f}".format(float(c.deposit)),trn_post=currentdate,
                                    trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                    hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                    line_no=c.lineno,item_uom=uom_ids.item_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                    stock_in=None,trans_package_line_no=None)
                                    stktrn_id.save()
                                    Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                                    

                                    stktrnids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(c.itemcodeid.item_code)+"0000",
                                    item_uom=c.item_uom.uom_code).order_by('pk').last() 


                                    stktrnid = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(c.itemcodeid.item_code)+"0000",
                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno,trn_date=currentdate,
                                    trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=uom_ids.uom_unit,trn_balqty=uom_ids.uom_unit,
                                    trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                    trn_amt="{:.2f}".format(float(c.deposit)),trn_post=currentdate,
                                    trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                    hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                    line_no=c.lineno,item_uom=c.item_uom.uom_code,item_batch=None,mov_type=None,item_batch_cost=None,
                                    stock_in=None,trans_package_line_no=None)
                                    stktrnid.save()
                                    Stktrn.objects.filter(pk=stktrnid.pk).update(trn_post=pay_date,trn_date=pay_date)
                                   

                                    fbatch_qty = (batchids.qty + uom_ids.uom_unit) - qtytodeduct

                                    vstk = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(c.itemcodeid.item_code)+"0000",
                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,trn_date=currentdate,
                                    trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=fbatch_qty,
                                    trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                    trn_amt="{:.2f}".format(float(c.deposit)),trn_post=currentdate,
                                    trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                    hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                    line_no=c.lineno,item_uom=c.item_uom.uom_code,item_batch=None,mov_type=None,item_batch_cost=None,
                                    stock_in=None,trans_package_line_no=None)
                                    vstk.save()
                                    Stktrn.objects.filter(pk=vstk.pk).update(trn_post=pay_date,trn_date=pay_date)
                                   


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
                                    batch_id = ItemBatch(item_code=c.itemcodeid.item_code,site_code=site.itemsite_code,
                                    batch_no="",uom=c.item_uom.uom_code,qty=-qtytodeduct,exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                                    deduct = -qtytodeduct

                                #Stktrn
                                currenttime = timezone.now()
                                currentdate = timezone.now().date()
                        
                                post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(c.itemcodeid.item_code)+"0000",
                                item_uom=c.item_uom.uom_code).order_by('pk').last() 

                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(c.itemcodeid.item_code)+"0000",
                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,trn_date=currentdate,
                                trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                trn_amt="{:.2f}".format(float(c.deposit)),trn_post=currentdate,
                                trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                line_no=c.lineno,item_uom=c.item_uom.uom_code,item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None)
                                stktrn_id.save()
                                Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                              


                       
                elif int(c.itemcodeid.Item_Divid.itm_code) == 5 and c.itemcodeid.Item_Divid.itm_desc == 'PREPAID' and c.itemcodeid.Item_Divid.itm_isactive == True:
                    #Prepaid Account creation
                    #exp_date need to map
                    prepaid_valid_period = None
                    if c.itemcodeid and c.itemcodeid.prepaid_valid_period:
                        prepaid_valid_period = date.today() + timedelta(int(c.itemcodeid.prepaid_valid_period))
                    vo_obj = VoucherCondition.objects.filter(item_code=c.itemcodeid.item_code)

                    if c.isopen_prepaid == True:
                        pp_amt = c.price
                        pp_total = c.prepaid_value
                        pp_bonus = c.prepaid_value - float(c.price)
                        v_amount = c.prepaid_value
                        v_remain = c.prepaid_value
                        if outstanding_acc == 0:
                            remain = c.prepaid_value
                        else:
                            remain = c.deposit
                        
                    else:
                        pp_amt = c.itemcodeid.prepaid_sell_amt
                        pp_total = c.itemcodeid.prepaid_value
                        pp_bonus = c.itemcodeid.prepaid_value - c.itemcodeid.prepaid_sell_amt
                        v_amount = vo_obj.first().amount if vo_obj else 0
                        v_remain = c.trans_amt
                        if outstanding_acc == 0:
                            remain = c.itemcodeid.prepaid_value
                        else:
                            remain = c.deposit


                    if c.is_foc == True:
                        pp_descval = c.itemcodeid.item_name+" "+"(FOC)"
                    else:
                        pp_descval = c.itemcodeid.item_name

                    prepacc = PrepaidAccount(pp_no=sa_transacno,pp_type=c.itemcodeid.item_range if c.itemcodeid.item_range else None, 
                    pp_desc=pp_descval,exp_date=prepaid_valid_period,cust_code=cust_obj.cust_code,
                    cust_name=cust_obj.cust_name,pp_amt=pp_amt,pp_total=pp_total,
                    pp_bonus=pp_bonus,transac_no="",item_no="",use_amt=0,remain=remain,ref1="",
                    ref2="",status=True,site_code=site.itemsite_code,sa_status="DEPOSIT",exp_status=True,
                    voucher_no='',isvoucher=False,has_deposit=True,topup_amt=c.deposit,
                    outstanding=outstanding_acc if outstanding_acc is not None and outstanding_acc > 0 else 0,active_deposit_bonus=True,topup_no="",topup_date=None,
                    line_no=c.lineno,staff_name=','.join([v.display_name for v in salesstaff if v.display_name]),
                    staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                    pp_type2=None,condition_type1=None,pos_daud_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,
                    Item_Codeid=c.itemcodeid,item_code=c.itemcodeid.item_code)
                    prepacc.save()
                    prepacc.sa_date = pay_date 
                    prepacc.start_date = pay_date
                    prepacc.save()
                    # print(prepacc.pk,"prepacc")

                    #PrepaidAccountCondition Creation

                    pp_acc = PrepaidAccountCondition(pp_no=sa_transacno,pp_type=c.itemcodeid.item_range if c.itemcodeid.item_range else None,
                    pp_desc=pp_descval,p_itemtype=','.join([v.p_itemtype for v in vo_obj if v.p_itemtype]),
                    item_code=c.itemcodeid.item_code,conditiontype1=','.join([v.conditiontype1 for v in vo_obj if v.conditiontype1]),
                    conditiontype2=','.join([v.conditiontype2 for v in vo_obj if v.conditiontype2]),
                    amount=v_amount,rate=vo_obj.first().rate if vo_obj else 0,use_amt=0,remain=remain,
                    pos_daud_lineno=c.lineno)
                    pp_acc.save()
                    # print(pp_acc.pk,"pp_acc")
                    PrepaidAccount.objects.filter(pk=prepacc.pk).update(pp_type2=pp_acc.pp_type,
                    condition_type1=pp_acc.conditiontype1)

                elif int(c.itemcodeid.Item_Divid.itm_code) == 4 and c.itemcodeid.Item_Divid.itm_desc == 'VOUCHER' and c.itemcodeid.Item_Divid.itm_isactive == True:
                    vorecontrolobj = ControlNo.objects.filter(control_description__iexact="Public Voucher",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    # if not vorecontrolobj:
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher Record Control No does not exist!!",'error': True} 
                    #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    voucher_code = str(vorecontrolobj.control_prefix)+str(vorecontrolobj.Site_Codeid.itemsite_code)+str(vorecontrolobj.control_no)
                    vo_percent = None
                    if c.itemcodeid.voucher_value_is_amount == True:
                        vo_percent = 0
                    else:
                        if c.itemcodeid.voucher_value_is_amount == False:
                            vo_percent = c.itemcodeid.voucher_value
                    
                    end_date = None
                    if c.itemcodeid.voucher_valid_period:
                        date_1 = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                        # print(date_1,"date_1")
                        end_date = date_1 + datetime.timedelta(days=int(c.itemcodeid.voucher_valid_period))
                        # print(end_date,"end_date")
                        # tod_now = datetime.now(pytz.timezone(TIME_ZONE))
                        # print(tod_now,"tod_now")
                        # voexpiry = tod_now + datetime.timedelta(days=c.itemcodeid.voucher_valid_period)
                        # print(voexpiry,"voexpiry")
                        # expiry = datetime.datetime.combine(end_date, datetime.datetime.min.time())

                        # expiry = end_date.strftime("%d-%m-%Y")
                        # print(expiry,"expiry") 

                    if c.is_foc == True:
                        voucher_nameval = c.itemcodeid.item_name+" "+"(FOC)"
                    else:
                        voucher_nameval = c.itemcodeid.item_name    

                    vo_rec = VoucherRecord(sa_transacno=sa_transacno,voucher_name=voucher_nameval,
                    voucher_no=voucher_code,value=c.price,cust_codeid=cust_obj,cust_code=cust_obj.cust_code,
                    cust_name=cust_obj.cust_name,percent=vo_percent,site_codeid=site,site_code=site.itemsite_code,
                    issued_expiry_date=end_date if end_date else None,issued_staff=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                    onhold=0,paymenttype=None,remark=None,type_code=vorecontrolobj.control_prefix,used=0,
                    ref_fullvoucherno=None,ref_rangefrom=None,ref_rangeto=None,site_allocate=None,dt_lineno=c.lineno,)
                    vo_rec.save()
                    vo_rec.sa_date = pay_date
                    vo_rec.save()
                    if vo_rec.pk:
                        vorecontrolobj.control_no = int(vorecontrolobj.control_no) + 1
                        vorecontrolobj.save()

                totaldisc = c.discount_amt + c.additional_discountamt
                totalpercent = c.discount + c.additional_discount

                # if c.discount_amt != 0.0 and c.additional_discountamt != 0.0:
                #     totaldisc = c.discount_amt + c.additional_discountamt
                #     totalpercent = c.discount + c.additional_discount
                #     istransdisc = True
                # elif c.discount_amt != 0.0:
                #     totaldisc = c.discount_amt
                #     totalpercent = c.discount
                #     istransdisc = False
                # elif c.additional_discountamt != 0.0:
                #     totaldisc = c.additional_discountamt
                #     totalpercent = c.additional_discount
                #     istransdisc = True    
                # else:
                #     totaldisc = 0.0
                #     totalpercent = 0.0
                #     istransdisc = False

                #PosDisc Creation for each cart line with or without line disc (disc per/amt = line disc + trasac disc)
                # if transc disc for whole cart is applied that time need to create one record in PosDisc (disc per/amt = trasac disc).
                discreason = None

                if c.pos_disc.all().exists():
                    for po in c.pos_disc.all():
                        po.sa_transacno = sa_transacno
                        po.dt_status = "SA"
                        po.dt_price = c.price
                        po.dt_date = pay_date
                        po.save()

                if int(c.itemcodeid.item_div) in [1,3] and c.itemcodeid.item_type == 'SINGLE':
                    if not c.pos_disc.all().exists():
                        if totaldisc == 0.0 or totalpercent == 0.0 and len(c.pos_disc.all()) == 0:
                            posdisc = PosDisc(sa_transacno=sa_transacno,dt_itemno=c.itemcodeid.item_code+"0000",disc_amt=totaldisc,
                            disc_percent=totalpercent,dt_lineno=c.lineno,remark=discreason,site_code=site.itemsite_code,
                            dt_status="SA",dt_auto=0,line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=c.price,istransdisc=False)
                            posdisc.save()
                            posdisc.dt_date = pay_date
                            posdisc.save()
                            # print(posdisc.pk,"posdisc")

                
                    
                #HoldItemDetail creation for retail products
                if int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
                    if c.holditemqty and int(c.holditemqty) > 0:
                        con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
                        # if not con_obj:
                        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
                        #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                        
                        hold = Holditemdetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
                        transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
                        hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                        hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=c.trans_amt,hi_qty=c.quantity,
                        hi_discamt=totaldisc,hi_discpercent=totalpercent,hi_discdesc=None,
                        hi_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                        hi_lineno=c.lineno,hi_uom=c.item_uom.uom_code,hold_item=True,hi_deposit=c.deposit,
                        holditemqty=c.holditemqty,status="OPEN",sa_custno=cust_obj.cust_code,
                        sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
                        product_issues_no=product_issues_no)
                        hold.save()
                        # print(hold.pk,"hold")
                        if hold.pk:
                            hold.sa_date = pay_date
                            hold.sa_time = pay_time
                            hold.save()
                            con_obj.control_no = int(con_obj.control_no) + 1
                            con_obj.save()
                            dtl.holditemqty = int(c.holditemqty)
                            dtl.save()

                if '0' in str(c.quantity):
                    no = str(c.quantity).split('0')
                    if no[0] == '':
                        number = no[1]
                    else:
                        number = c.quantity
                else:
                    number = c.quantity

                dtl_st_ref_treatmentcode = "";dtl_first_trmt_done = False
                if c.itemcodeid.Item_Divid.itm_code == '3':
                    if c.is_foc == True:
                        course_val = c.itemdesc
                        isfoc_val = True
                    else:
                        course_val = c.itemdesc 
                        isfoc_val = False
                    
                    expiry = None
                    if c.itemcodeid.service_expire_active == True:
                        month = c.itemcodeid.service_expire_month
                        if month:
                            current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                            expiry = current_date + relativedelta(months=month)
                    
                    treat_type = "N"
                    treatment_limit_times = None
                    flexipoints = None

                    if c.itemcodeid.limitservice_flexionly == True:
                        treat_type = "FFi"
                        treatment_limit_times = 0
                        if c.itemcodeid.treatment_limit_active == True:
                            treatment_limit_times = c.itemcodeid.treatment_limit_count
                    
                   
                    if c.is_flexi == True:
                        expiry = c.treat_expiry
                        treat_type = c.treat_type
                        treatment_limit_times = c.treatment_limit_times
                        flexipoints = c.itemcodeid.flexipoints if c.itemcodeid.flexipoints else None
                    
                    for i in range(1,int(number)+1):
                        treat = c
                        Price = c.trans_amt
                        Unit_Amount = Price / c.quantity
                        
                        times = str(i).zfill(2)
                        treatment_no = str(c.quantity).zfill(2)
                        
                        if i == int(c.quantity):
                            lval = float(Price) - (float("{:.2f}".format(Unit_Amount)) * (c.quantity -1))
                            Unit_Amount = lval
                            
                        tmptrd_ids = Tmptreatment.objects.filter(itemcart=c,times=times).order_by('pk').first()

                        if tmptrd_ids:
                            treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
                            treatment_parentcode=treatment_parentcode,course=tmptrd_ids.course,times=times,
                            treatment_no=treatment_no,price="{:.2f}".format(float(tmptrd_ids.price)),unit_amount="{:.2f}".format(float(tmptrd_ids.unit_amount)),Cust_Codeid=treat.cust_noid,
                            cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
                            status="Open",item_code=str(treat.itemcodeid.item_code)+"0000",Item_Codeid=treat.itemcodeid,
                            sa_transacno=sa_transacno,sa_status="SA",type=treat_type,trmt_is_auto_proportion=False,
                            dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,isfoc=tmptrd_ids.isfoc,
                            treatment_account=treatacc,service_itembarcode=str(treat.itemcodeid.item_code)+"0000",
                            expiry=expiry,treatment_limit_times=treatment_limit_times,
                            flexipoints=flexipoints)
                        else:
                            treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
                            treatment_parentcode=treatment_parentcode,course=course_val,times=times,
                            treatment_no=treatment_no,price="{:.2f}".format(float(Price)),unit_amount="{:.2f}".format(float(Unit_Amount)),Cust_Codeid=treat.cust_noid,
                            cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
                            status="Open",item_code=str(treat.itemcodeid.item_code)+"0000",Item_Codeid=treat.itemcodeid,
                            sa_transacno=sa_transacno,sa_status="SA",type=treat_type,trmt_is_auto_proportion=False,
                            dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,isfoc=isfoc_val,
                            treatment_account=treatacc,service_itembarcode=str(treat.itemcodeid.item_code)+"0000",
                            expiry=expiry,treatment_limit_times=treatment_limit_times,
                            flexipoints=flexipoints)

                        treatmentid.save() 
                        treatmentid.treatment_date = pay_date
                        if treatmentid:
                            stdids = Treatmentids.objects.filter(treatment_int=treatmentid.pk)
                            if not stdids: 
                                tid =  Treatmentids(treatment_parentcode=treatment_parentcode,
                                treatment_int=treatmentid.pk).save()
                                                
                        #and str(treatmentid.treatment_code) == str(treatment_parentcode)+"-"+"01"
                        # apt_lst = []

                        if c.helper_ids.exists():

                            link_flag = False
                            if len(c.helper_ids.all()) > 1:
                                link_flag = True

                            for h in c.helper_ids.all().filter(times=times):
                            
                                # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                                    
                                treatmentid.status = "Done"
                                treatmentid.trmt_room_code = h.Room_Codeid.room_code if h.Room_Codeid else None
                                # treatmentid.treatment_date = timezone.now()
                                treatmentid.treatment_date = pay_date
                                treatmentid.save()

                                # wp1 = h.workcommpoints / float(c.helper_ids.all().filter(times=times).count())
                                wp1 = h.wp1
                                share_amt = float(treatmentid.unit_amount) / float(c.helper_ids.all().filter(times=times).count())
                                if h.work_amt and h.work_amt > 0:
                                    share_amt = h.work_amt
                                

                                TmpItemHelper.objects.filter(id=h.id).update(item_code=treatment_parentcode+"-"+str(times),
                                item_name=c.itemcodeid.item_name,line_no=dtl.dt_lineno,sa_transacno=sa_transacno,
                                amount=treatmentid.unit_amount,sa_date=pay_date,site_code=site.itemsite_code,
                                wp1=wp1,wp2=0.0,wp3=0.0)

                                # Item helper create
                                helper = ItemHelper(item_code=treatment_parentcode+"-"+str(times),item_name=c.itemdesc,
                                line_no=dtl.dt_lineno,sa_transacno=sa_transacno,amount="{:.2f}".format(float(treatmentid.unit_amount)),
                                helper_name=h.helper_name if h.helper_name else None,helper_code=h.helper_code if h.helper_code else None,
                                site_code=site.itemsite_code,share_amt="{:.2f}".format(float(share_amt)),helper_transacno=sa_transacno,
                                wp1=wp1,wp2=0.0,wp3=0.0,percent=h.percent,work_amt="{:.2f}".format(float(h.work_amt)) if h.work_amt else h.work_amt,session=h.session,
                                times=h.times,treatment_no=h.treatment_no)
                                helper.save()
                                ItemHelper.objects.filter(id=helper.id).update(sa_date=pay_date)
                                
                                # print(helper.sa_date,"helper")

                                #appointment treatment creation
                                # if h.appt_fr_time and h.appt_to_time != False and h.add_duration != False:

                                #     custprev_appts = Appointment.objects.filter(appt_date=date.today(),
                                #     cust_no=cust_obj.cust_code).order_by('-pk').exclude(itemsite_code=site.itemsite_code)
                                        
                                #     custprevtime_appts = Appointment.objects.filter(appt_date=date.today(),
                                #     cust_no=cust_obj.cust_code).filter(Q(appt_to_time__gte=h.appt_fr_time) & Q(appt_fr_time__lte=h.appt_to_time)).order_by('-pk')
                                   

                                #     #staff having shift/appointment on other branch for the same time
                                   
                                #     check_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=h.helper_id.emp_code,
                                #     ).filter(Q(appt_to_time__gt=h.appt_fr_time) & Q(appt_fr_time__lt=h.appt_to_time))
                                #     # print(check_ids,"check_ids")

                                #     if not custprev_appts and not custprevtime_appts and not check_ids:
                                #         stock_obj = c.itemcodeid

                                #         stk_duration = 60
                                #         if stock_obj.srv_duration:
                                #             if stock_obj.srv_duration is None or float(stock_obj.srv_duration) == 0.0:
                                #                 stk_duration = 60
                                #             else:
                                #                 stk_duration = int(stock_obj.srv_duration)

                                #         stkduration = int(stk_duration) + 30
                                #         # print(stkduration,"stkduration")

                                #         hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                                #         start_time =  get_in_val(self, h.appt_fr_time)
                                #         starttime = datetime.datetime.strptime(start_time, "%H:%M")

                                #         end_time = starttime + datetime.timedelta(minutes = stkduration)
                                #         endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                                #         duration = hrs

                                #         treat_all = Treatment.objects.filter(sa_transacno=sa_transacno,treatment_parentcode=treatment_parentcode,site_code=site.itemsite_code)
                                #         length = [t.status for t in treat_all if t.status == 'Done']
                                #         if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
                                #             master_status = "Done"
                                #         else:
                                #             master_status = "Open"

                                #         master = Treatment_Master(treatment_code=str(treatment_parentcode)+"-"+str(times),
                                #         treatment_parentcode=treatment_parentcode,sa_transacno=sa_transacno,
                                #         course=stock_obj.item_desc,times=times,treatment_no=treatment_no,
                                #         price=stock_obj.item_price,cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,
                                #         cust_name=cust_obj.cust_name,status=master_status,unit_amount=stock_obj.item_price,
                                #         Item_Codeid=stock_obj,item_code=stock_obj.item_code,
                                #         sa_status="SA",dt_lineno=dtl.dt_lineno,type="N",duration=stkduration,
                                #         Site_Codeid=site,site_code=site.itemsite_code,
                                #         trmt_room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,Trmt_Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,
                                #         Item_Class=stock_obj.Item_Classid if stock_obj.Item_Classid else None,PIC=stock_obj.Stock_PIC if stock_obj.Stock_PIC else None,
                                #         start_time=h.appt_fr_time if h.appt_fr_time else None,end_time=h.appt_to_time if h.appt_to_time else None,add_duration=h.add_duration if h.add_duration else None,
                                #         appt_remark=stock_obj.item_desc if stock_obj.item_desc else None,requesttherapist=False)
                                #         master.save()
                                #         master.treatment_date = pay_date
                                #         master.save()
                                #         master.emp_no.add(h.helper_id.pk)
                                #         # print(master.id,"master")

                                #         ctrl_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                #         # if not ctrl_obj:
                                #         #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
                                #         #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                        
                                #         appt_code = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                                        
                                #         if apt_lst == []:
                                #             linkcode = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                                #         else:
                                #             app_obj = Appointment.objects.filter(pk=apt_lst[0]).order_by('pk').first()
                                #             linkcode = app_obj.linkcode

                                #         channel = ApptType.objects.filter(appt_type_code="10003",appt_type_isactive=True).first()
                                #         # if not channel:
                                #         #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
                                #         #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                #         # no need to add checktype & treat_parentcode for TD / service done appts

                                #         appt = Appointment(cust_noid=cust_obj,cust_no=cust_obj.cust_code,appt_date=pay_date,
                                #         appt_fr_time=h.appt_fr_time if h.appt_fr_time else None,Appt_typeid=channel if channel else None,appt_type=channel.appt_type_desc if channel.appt_type_desc else None,
                                #         appt_phone=cust_obj.cust_phone2,appt_remark=stock_obj.item_desc,
                                #         emp_noid=h.helper_id if h.helper_id else None,emp_no=h.helper_id.emp_code if h.helper_id.emp_code else None,emp_name=h.helper_id.display_name if h.helper_id.display_name else None,
                                #         cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
                                #         appt_to_time=h.appt_to_time if h.appt_to_time else None,Appt_Created_Byid=fmspw,
                                #         appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                                #         Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,
                                #         Source_Codeid=h.Source_Codeid if h.Source_Codeid else None,source_code=h.Source_Codeid.source_code if h.Source_Codeid else None,
                                #         cust_refer=cust_obj.cust_refer,requesttherapist=False,new_remark=h.new_remark,
                                #         item_code=stock_obj.item_code,sa_transacno=sa_transacno,treatmentcode=str(treatment_parentcode)+"-"+str(times),
                                #         linkcode=linkcode,link_flag=link_flag,add_duration=h.add_duration if h.add_duration else None,
                                #         Item_Codeid=stock_obj)
                                        
                                #         appt.save()
                                        

                                #         if appt.pk:
                                #             apt_lst.append(appt.pk)
                                #             master.Appointment = appt
                                #             master.appt_time = timezone.now()
                                #             master.save()
                                #             ctrl_obj.control_no = int(ctrl_obj.control_no) + 1
                                #             ctrl_obj.save()
                                    
                            #treatment Account creation for done treatment 01
                            if c.helper_ids.all().filter(times=times).first():
                                stock_obj = c.itemcodeid
                                #acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,
                                #treatment_parentcode=treatment_parentcode,Site_Codeid=site).order_by('id').last()
                                acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,
                                treatment_parentcode=treatment_parentcode).order_by('sa_date','sa_time','id').last()
                                
                                tr_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode,times=times).first()

                                td_desc = str(times)+"/"+str(c.quantity)+" "+str(c.itemdesc)
                                balance = acc_ids.balance - float(tr_ids.unit_amount) if acc_ids.balance else 0.0

                                treatacc_td = TreatmentAccount(Cust_Codeid=cust_obj,
                                cust_code=cust_obj.cust_code,ref_no=treatmentid.treatment_code,
                                description=td_desc,type='Sales',amount=-float("{:.2f}".format(float(tr_ids.unit_amount))) if tr_ids.unit_amount else 0.0,
                                balance="{:.2f}".format(float(balance)) if balance else 0.0,User_Nameid=fmspw,user_name=fmspw.pw_userlogin,
                                ref_transacno=treatmentid.sa_transacno,
                                sa_transacno=sa_transacno,qty=1,outstanding="{:.2f}".format(float(acc_ids.outstanding)) if acc_ids and acc_ids.outstanding is not None and acc_ids.outstanding > 0 else 0,
                                deposit=None,treatment_parentcode=treatmentid.treatment_parentcode,
                                sa_status="SA",cas_name=fmspw.pw_userlogin,
                                sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                                dt_lineno=c.lineno,Site_Codeid=site,site_code=site.itemsite_code,
                                itemcart=c)
                                treatacc_td.save()
                                treatacc_td.sa_date = pay_date
                                treatacc_td.sa_time = pay_time
                                treatacc_td.save()
                                # print(treatacc_td.id,"treatacc_td")
                                dtl_first_trmt_done = True
                                if dtl_st_ref_treatmentcode == "":
                                    dtl_st_ref_treatmentcode = str(treatment_parentcode)+"-"+str(times)
                                elif not dtl_st_ref_treatmentcode == "":
                                    dtl_st_ref_treatmentcode = str(dtl_st_ref_treatmentcode) +"-"+str(times)

                                #auto Treatment Usage transactions
                                now = datetime.datetime.now()
                                s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))
                                usagelevel_ids = Usagelevel.objects.filter(service_code=str(treat.itemcodeid.item_code)+"0000",
                                isactive=True).order_by('-pk') 
                                valuedata = 'TRUE'

                                sys_ids = Systemsetup.objects.filter(title='Stock Available',value_name='Stock Available').first() 
                                if sys_ids:
                                    valuedata = sys_ids.value_data

                                currenttime = timezone.now()
                                currentdate = timezone.now().date()
                                    
                                for i in usagelevel_ids: 
                                    TreatmentUsage(treatment_code=treatmentid.treatment_code,item_code=i.item_code,
                                    item_desc=i.item_desc,qty=i.qty,uom=i.uom,site_code=site.itemsite_code,usage_status="Usage",
                                    line_no=1,usage_update=s1,sa_transacno=sa_transacno).save()
                                    if int(i.qty) > 0:
                                        qtytodeduct = int(i.qty)

                                        batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=i.item_code[:-4],
                                        uom=i.uom).order_by('pk').last() 
                                        obatchids = ItemBatch.objects.none()

                                        uom_ids = ItemUomprice.objects.filter(item_code=i.item_code[:-4],item_uom2=i.uom
                                        ,uom_unit__gt=0,isactive=True).first()
                                        if uom_ids:
                                            obatchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(i.item_code[:-4]),
                                            uom=uom_ids.item_uom).order_by('pk').last() 


                                        stockreduce = False
                                        if valuedata == 'TRUE':
                                            if (batchids and int(batchids.qty) >= int(i.qty)) or (obatchids and int(obatchids.qty) >= int(qtytodeduct)):
                                                stockreduce = True
                                        else:
                                            stockreduce = True     

                                        if stockreduce == True:
                                            #ItemBatch
                                            if batchids and int(batchids.qty) >= int(qtytodeduct):
                                                deduct = batchids.qty - qtytodeduct
                                                batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())

                                                
                                                post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                                item_uom=i.uom).order_by('pk').last() 


                                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=treatmentid.treatment_code,trn_date=currentdate,
                                                trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                                trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                                trn_amt=None,trn_post=currentdate,
                                                trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                                hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                                line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                stock_in=None,trans_package_line_no=None)
                                                stktrn_id.save()
                                                Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                                            
                                            else:
                                                flag = False

                                                adcontrolobj = ControlNo.objects.filter(control_description__iexact="ADJS",
                                                site_code=fmspw.loginsite.itemsite_code).first()

                                                adjno = False
                                                if adcontrolobj:
                                                    adjno = "W"+str(adcontrolobj.control_prefix)+str(adcontrolobj.site_code)+str(adcontrolobj.control_no)


                                                if batchids and obatchids and int(obatchids.qty) >= int(qtytodeduct):

                                                    post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                                    stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                                    item_uom=uom_ids.item_uom).order_by('pk').last() 


                                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno if adjno else treatmentid.treatment_code,trn_date=currentdate,
                                                    trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=-1,trn_balqty=obatchids.qty-1,
                                                    trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                                    trn_amt=None,trn_post=currentdate,
                                                    trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                                    hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                                    line_no=c.lineno,item_uom=uom_ids.item_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                    stock_in=None,trans_package_line_no=None)
                                                    stktrn_id.save()
                                                    Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                                                    

                                                    stktrnids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                                    item_uom=i.uom).order_by('pk').last() 


                                                    stktrnid = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno,trn_date=currentdate,
                                                    trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=uom_ids.uom_unit,trn_balqty=uom_ids.uom_unit,
                                                    trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                                    trn_amt=None,trn_post=currentdate,
                                                    trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                                    hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                                    line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                    stock_in=None,trans_package_line_no=None)
                                                    stktrnid.save()
                                                    Stktrn.objects.filter(pk=stktrnid.pk).update(trn_post=pay_date,trn_date=pay_date)
                                                

                                                    fbatch_qty = (batchids.qty + uom_ids.uom_unit) - qtytodeduct

                                                    vstk = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=treatmentid.treatment_code,trn_date=currentdate,
                                                    trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=fbatch_qty,
                                                    trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                                    trn_amt=None,trn_post=currentdate,
                                                    trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                                    hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                                    line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                    stock_in=None,trans_package_line_no=None)
                                                    vstk.save()
                                                    Stktrn.objects.filter(pk=vstk.pk).update(trn_post=pay_date,trn_date=pay_date)
                                                


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
                                                        batch_id = ItemBatch(item_code=i.item_code[:-4],site_code=site.itemsite_code,
                                                        batch_no="",uom=i.uom,qty=-qtytodeduct,exp_date=None,batch_cost=None).save()
                                                        deduct = -qtytodeduct

                                                    #Stktrn
                                                    currenttime = timezone.now()
                                                    currentdate = timezone.now().date()
                                            
                                                    post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                                    stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                                    item_uom=i.uom).order_by('pk').last() 

                                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=treatmentid.treatment_code,trn_date=currentdate,
                                                    trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                                    trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                                    trn_amt=None,trn_post=currentdate,
                                                    trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                                    hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                                    line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                                    stock_in=None,trans_package_line_no=None)
                                                    stktrn_id.save()
                                                    Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                    

                        
                        treatmentid.save()
                        # appt_time=treat.appt_time,Trmt_Room_Codeid=treat.Trmt_Room_Codeid,trmt_room_code=treat.trmt_room_code,
                        # print(treatmentid.id,"treatment_id")

                    # if treatacc and treatmentid:
                    #     controlobj.control_no = int(controlobj.control_no) + 1
                    #     controlobj.save()

                    # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
                    dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
                    dtl.first_trmt_done = dtl_first_trmt_done
                    # dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
                    # dtl.first_trmt_done_staff_name = ','.join([v.helper_id.display_name for v in c.helper_ids.all() if v.helper_id.display_name])
                    dtl.first_trmt_done_staff_code = ','.join([v.emp_code for v in c.service_staff.all() if v.emp_code])
                    dtl.first_trmt_done_staff_name = ','.join([v.display_name for v in c.service_staff.all() if v.display_name])
                    
                    if treatmentid.treatment_limit_times is not None:
                        if treatmentid.type in ['FFi','FFd'] and c.quantity == 1 and  int(treatmentid.treatment_limit_times) > 1:
                            for i in range(2,int(treatmentid.treatment_limit_times)+1):
                                times = str(i).zfill(2)
                                ctt = treatmentid
                                

                                e_treatids = Treatment(treatment_code=str(treatmentid.treatment_parentcode)+"-"+str(times),
                                course=ctt.course,times=times,
                                treatment_no=times,price=ctt.price,treatment_date=pay_date,
                                cust_name=ctt.cust_name,Cust_Codeid=ctt.Cust_Codeid,
                                cust_code=ctt.cust_code,status="Open",unit_amount=0,
                                Item_Codeid=ctt.Item_Codeid,item_code=ctt.item_code,
                                treatment_parentcode=ctt.treatment_parentcode,
                                sa_transacno=ctt.sa_transacno,
                                sa_status=ctt.sa_status,
                                remarks=ctt.remarks,
                                dt_lineno=ctt.dt_lineno,expiry=ctt.expiry,package_code=ctt.package_code,
                                Site_Codeid=ctt.Site_Codeid,site_code=ctt.site_code,type=ctt.type,treatment_limit_times=ctt.treatment_limit_times,
                                service_itembarcode=ctt.service_itembarcode,isfoc=ctt.isfoc,Trmt_Room_Codeid=ctt.Trmt_Room_Codeid,
                                trmt_room_code=ctt.trmt_room_code,trmt_is_auto_proportion=ctt.trmt_is_auto_proportion,
                                treatment_account=ctt.treatment_account)

                                
                                e_treatids.save() 
                                e_treatids.treatment_date = pay_date

                                if e_treatids: 
                                    stdsids = Treatmentids.objects.filter(treatment_int=e_treatids.pk)
                                    if not stdsids: 
                                        tid =  Treatmentids(treatment_parentcode=ctt.treatment_parentcode,
                                        treatment_int=e_treatids.pk).save()
                                                


                    if treatmentid.expiry:
                        dxsplit = str(treatmentid.expiry).split(" ")
                        expdate = datetime.datetime.strptime(str(dxsplit[0]), '%Y-%m-%d').strftime("%d/%m/%Y")
                        dtl.dt_itemdesc = dtl.dt_itemdesc+" "+"Expiry Date : "+str(expdate)

                    dtl.save()

                    if c.helper_ids.exists():
                        dohelperids = list(set(ItemHelper.objects.filter(sa_transacno=sa_transacno,
                        line_no=dtl.dt_lineno).values_list('times', flat=True).distinct()))
                        if dohelperids != []:
                            dtl.dt_itemdesc = dtl.dt_itemdesc+" "+"(TD - "+str(len(dohelperids))+")"
                            dtl.save()


                        treatk_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode).order_by('pk').first()
                        if treatk_ids and treatk_ids.type in ['FFi','FFd']:
                            ef_done_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode,status="Done").order_by('pk').count()
                            efd_treat_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode).order_by('-pk').first()
                            ef_open_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode,status="Open").order_by('pk')
                            if treatk_ids.expiry and treatk_ids.treatment_limit_times is not None:
                                splte_t = str(treatk_ids.expiry).split(' ')
                                expiry_t = splte_t[0]
                                if expiry_t >= str(date.today()):
                                    if int(treatk_ids.treatment_limit_times) == 0:
                                        if not ef_open_ids:
                                            # if treatk_ids.treatment_limit_times > ef_done_ids or treatk_ids.treatment_limit_times == 0:
                                            ct = treatk_ids
                                            times_ve = str(int(efd_treat_ids.times) + 1).zfill(2)
                                            treatment_coder = ct.treatment_parentcode+"-"+times_ve
                                            treatids = Treatment(treatment_code=treatment_coder,course=ct.course,times=times_ve,
                                            treatment_no=times_ve,price=ct.price,treatment_date=pay_date,
                                            cust_name=ct.cust_name,Cust_Codeid=ct.Cust_Codeid,
                                            cust_code=ct.cust_code,status="Open",unit_amount=0,
                                            Item_Codeid=ct.Item_Codeid,item_code=ct.item_code,treatment_parentcode=ct.treatment_parentcode,
                                            sa_transacno=ct.sa_transacno,
                                            sa_status=ct.sa_status,
                                            remarks=ct.remarks,
                                            dt_lineno=ct.dt_lineno,expiry=ct.expiry,package_code=ct.package_code,
                                            Site_Codeid=ct.Site_Codeid,site_code=ct.site_code,type=ct.type,treatment_limit_times=ct.treatment_limit_times,
                                            service_itembarcode=ct.service_itembarcode,isfoc=ct.isfoc,Trmt_Room_Codeid=ct.Trmt_Room_Codeid,
                                            trmt_room_code=ct.trmt_room_code,trmt_is_auto_proportion=ct.trmt_is_auto_proportion,
                                            treatment_account=ct.treatment_account)
                                            treatids.save()
                                            if treatids:
                                                stfdsids = Treatmentids.objects.filter(treatment_int=treatids.pk)
                                                if not stfdsids: 
                                                    Treatmentids(treatment_parentcode=ct.treatment_parentcode,
                                                    treatment_int=treatids.pk).save()
                            

                    if treatment_parentcode:
                        searchids = TreatmentPackage.objects.filter(treatment_parentcode=treatment_parentcode)
                        if not searchids:
                            o_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode).order_by('pk').count()
                            tptdone_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode,status="Done").order_by('pk').count()
                            tptcancel_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode,status="Cancel").order_by('pk').count()
                            tptopen_ids = Treatment.objects.filter(treatment_parentcode=treatment_parentcode,status="Open").order_by('pk').count()
                            fu_ids =  Treatment.objects.filter(treatment_parentcode=treatment_parentcode,times="01").first()
                            q = str(c.quantity).zfill(2)
                            ls_ids = Tmptreatment.objects.filter(itemcart=c,isfoc=False).order_by('-pk').first()

                            trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                            
                           
                            tr = TreatmentPackage(treatment_parentcode=treatment_parentcode,
                            item_code=str(treatmentid.Item_Codeid.item_code)+"0000",course=treatmentid.course,
                            treatment_no=str(o_ids).zfill(2),open_session=tptopen_ids,done_session=tptdone_ids,
                            cancel_session=tptcancel_ids,expiry_date=treatmentid.expiry,unit_amount=ls_ids.unit_amount if ls_ids else treatmentid.unit_amount,
                            customerid=cust_obj,cust_name=treatmentid.cust_name,cust_code=treatmentid.cust_code,
                            treatment_accountid=treatmentid.treatment_account,totalprice=treatmentid.price,
                            type=treatmentid.type,
                            Item_Codeid=treatmentid.Item_Codeid,treatment_limit_times=treatmentid.treatment_limit_times,
                            Site_Codeid=treatmentid.Site_Codeid,site_code=treatmentid.site_code,
                            sa_transacno=sa_transacno,lastsession_unit_amount=fu_ids.unit_amount,
                            balance="{:.2f}".format(float(trmtAccObj.balance)),outstanding="{:.2f}".format(float(trmtAccObj.outstanding)),
                            )
                            tr.save()   
                            datetimed = datetime.datetime.strptime(str(pay_date)+" "+str(time.strftime("%H:%M:%S")), "%Y-%m-%d %H:%M:%S")
                            tr.treatment_date = datetimed
                            tr.save()

                            treatmids = list(set(Treatment.objects.filter(
                            treatment_parentcode=treatment_parentcode).filter(~Q(status="Open")).only('pk').order_by('pk').values_list('pk', flat=True).distinct()))

                            Treatmentids.objects.filter(treatment_parentcode=treatment_parentcode,
                            treatment_int__in=treatmids).delete()
                            
                            p_ids = list(set(Treatmentids.objects.filter(treatment_parentcode=treatment_parentcode).values_list('treatment_int', flat=True).distinct()))
                            op_ids = list(Treatment.objects.filter(
                            treatment_parentcode=treatment_parentcode).filter(Q(status="Open"),~Q(pk__in=p_ids)).only('pk').order_by('pk').values_list('pk', flat=True).distinct())
                            if op_ids:
                                for j in op_ids:
                                    stf_ids = Treatmentids.objects.filter(treatment_int=j)
                                    if not stf_ids: 
                                        Treatmentids(treatment_parentcode=treatment_parentcode,
                                                    treatment_int=j).save()



            # tmptrd_ids = Tmptreatment.objects.filter(itemcart=c).order_by('pk').delete()

        return id_lst
    # except Exception as e:
    #     invalid_message = str(e)
    #     return general_error_response(invalid_message)
    
def invoice_topup(self, request, topup_ids,sa_transacno, cust_obj, outstanding, pay_date, pay_time):
    # try:
    if self:
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        empl = fmspw.Emp_Codeid
        id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0
        outstanding_new = 0.0
        gst = GstSetting.objects.filter(isactive=True,activefromdate__date__lte=pay_date,
        activetodate__date__gte=pay_date).first()

        for idx, c in enumerate(topup_ids, start=1):
            if idx == 1:
                alsales_staff = c.sales_staff.all().first()

            # print(c,"cc")
            # controlobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
            # if not controlobj:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
            #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            # treatment_parentcode = "TRM"+str(controlobj.control_prefix)+str(controlobj.Site_Codeid.itemsite_code)+str(controlobj.control_no)
            
            sales_staff = c.sales_staff.all().first()
            salesstaff = c.sales_staff.all()

            # total = c.price * c.quantity
            totQty += c.quantity
            # discount_amt += float(c.discount_amt)
            # additional_discountamt += float(c.additional_discountamt)
            total_disc += c.discount_amt + c.additional_discountamt
            totaldisc = c.discount_amt + c.additional_discountamt
            # dt_discPercent = (float(total_disc) * 100) / float(value['subtotal'])
            dt_discPercent = c.discount + c.additional_discount

            if c.is_foc == True:
                isfoc = True
                item_remarks = c.focreason.foc_reason_ldesc if c.focreason and c.focreason.foc_reason_ldesc else None 
            else:
                isfoc = False  
                item_remarks = None   
            
            
            stock = Stock.objects.filter(pk=c.itemcodeid.pk).first()
            multi_itemcode = None
            calcgst = 0
            if gst:
                calcgst = gst.item_value if gst and gst.item_value else 0.0
            if calcgst > 0:
                sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
                if sitegst:
                    if sitegst.site_is_gst == False:
                        calcgst = 0
            # print(calcgst,"0 calcgst")
            # Yoonus Tax Chcking
            gst_amt_collect = 0
            if calcgst > 0:
                if site and site.is_exclusive == True:
                    gst_amt_collect = c.deposit * (calcgst / 100)
                    # tax_amt = deposit_amt * (gst.item_value / 100)
                    # billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
                else:
                    gst_amt_collect = c.deposit * calcgst / (100+calcgst)
                    # billable_amount = "{:.2f}".format(deposit_amt)
                    # tax_amt = deposit_amt * gst.item_value / (100+gst.item_value)
                    # Yoonus
            # gst_amt_collect = c.deposit * (gst.item_value / 100)

            sales = "";service = ""
            if c.sales_staff.all():
                for i in c.sales_staff.all():
                    if sales == "":
                        sales = sales + i.display_name
                    elif not sales == "":
                        sales = sales +","+ i.display_name
            if c.service_staff.all(): 
                for s in c.service_staff.all():
                    if service == "":
                        service = service + s.display_name
                    elif not service == "":
                        service = service +","+ s.display_name 
            
            

            if c.treatment_account is not None:
                topup_code = c.treatment_account.treatment_parentcode
                multi_itemcode = c.treatment_account.treatment_parentcode

                #acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment_account.ref_transacno,
                #treatment_parentcode=c.treatment_account.treatment_parentcode,Site_Codeid=site,
                #cust_code=cust_obj.cust_code).order_by('id').last()
                acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment_account.ref_transacno,
                treatment_parentcode=c.treatment_account.treatment_parentcode,
                cust_code=cust_obj.cust_code).order_by('sa_date','sa_time','id').last()

                outstanding_acc =  float(acc_ids.outstanding) - float(c.deposit)
                # print(outstanding_acc,"outstanding_acc")
                
                dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
                dt_itemno=c.treatment_account.treatment_parentcode,dt_itemdesc=c.itemdesc,
                dt_price=c.price,dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
                dt_discamt="{:.2f}".format(float(totaldisc)),dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,
                dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                dt_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                dt_discuser=None,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                dt_transacamt=0,dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,
                itemcart=c,st_ref_treatmentcode=None,first_trmt_done=False,topup_outstanding=outstanding_acc if outstanding_acc is not None and outstanding_acc > 0 else 0,
                record_detail_type="TP SERVICE",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
                dt_remark=c.remark,isfoc=isfoc,item_remarks=item_remarks,topup_prepaid_trans_code="",
                topup_service_trmt_code=topup_code,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
                staffs = sales +" "+"/"+" "+ service)
                #appt_time=app_obj.appt_fr_time,
            
            elif c.deposit_account is not None:
                daud_ids = PosDaud.objects.filter(sa_transacno=c.deposit_account.ref_transacno,dt_itemnoid=c.itemcodeid,
                ItemSite_Codeid__pk=site.pk).order_by('pk').first()
                # decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                # if not decontrolobj:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                # treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)


                #acc_ids = DepositAccount.objects.filter(ref_transacno=c.deposit_account.sa_transacno,
                #ref_productcode=c.deposit_account.treat_code,Site_Codeid=site,type__in=('Deposit', 'Top Up'),
                #cust_code=cust_obj.cust_code).order_by('id').last()
                # acc_ids = DepositAccount.objects.filter(ref_transacno=c.deposit_account.sa_transacno,
                # ref_productcode=c.deposit_account.treat_code,
                # cust_code=cust_obj.cust_code).order_by('sa_date','sa_time','id').last()

                acc_ids = DepositAccount.objects.filter(sa_transacno=c.deposit_account.sa_transacno,
                treat_code=c.deposit_account.treat_code,
                cust_code=cust_obj.cust_code).order_by('sa_date','sa_time','id').last()


                treat_code = acc_ids.treat_code
                multi_itemcode = treat_code

                outstanding_acc =  float(acc_ids.outstanding) - float(c.deposit)
               
                
                dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
                dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=c.itemcodeid.item_name,
                dt_price="{:.2f}".format(float(c.price)),dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
                dt_discamt="{:.2f}".format(float(totaldisc)),dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,
                dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                dt_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                dt_discuser=None,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                dt_transacamt=0,dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,
                itemcart=c,st_ref_treatmentcode=None,first_trmt_done=False,topup_outstanding=outstanding_acc if outstanding_acc is not None and outstanding_acc > 0 else 0,
                record_detail_type="TP PRODUCT",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
                dt_remark=c.remark if c.remark else None,isfoc=isfoc,item_remarks=item_remarks,topup_product_treat_code = treat_code,
                topup_prepaid_trans_code="",dt_uom=daud_ids.dt_uom if daud_ids and daud_ids.dt_uom  else '',
                item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
                staffs = sales +" "+"/"+" "+ service)
                #appt_time=app_obj.appt_fr_time, 


            elif c.prepaid_account is not None:
                topup_code = c.prepaid_account.transac_no
                multi_itemcode = topup_code

                #acc_ids = PrepaidAccount.objects.filter(Site_Codeid=site,cust_code=cust_obj.cust_code,
                #pp_no=c.prepaid_account.pp_no,status=True,Item_Codeid=c.itemcodeid,
                #line_no=c.prepaid_account.line_no).order_by('id').first() #transac_no=
                acc_ids = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,
                pp_no=c.prepaid_account.pp_no,status=True,
                line_no=c.prepaid_account.line_no).order_by('sa_date','id').last()
        
                outstanding_acc =  float(acc_ids.outstanding) - float(c.deposit)

                dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
                dt_itemno=topup_code,dt_itemdesc=c.itemcodeid.item_name,
                dt_price=c.price,dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
                dt_discamt="{:.2f}".format(float(totaldisc)),dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,
                dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                dt_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                dt_discuser=None,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                dt_transacamt=0,dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,
                itemcart=c,st_ref_treatmentcode=None,first_trmt_done=False,topup_outstanding=outstanding_acc if outstanding_acc is not None and outstanding_acc > 0 else 0,
                record_detail_type="TP PREPAID",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
                dt_remark=c.remark,isfoc=isfoc,item_remarks=item_remarks,
                topup_prepaid_trans_code=c.prepaid_account.pp_no,topup_prepaid_type_code=c.prepaid_account.pp_type,
                topup_prepaid_pos_trans_lineno=c.lineno,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
                staffs = sales +" "+"/"+" "+ service)
                #appt_time=app_obj.appt_fr_time, 

            else:
                acc_ids = None                
            
            dtl.save()
            dtl.sa_date = pay_date
            dtl.sa_time = pay_time
            dtl.save()
            # print(dtl.id,"dtl")
            if dtl.pk not in id_lst:
                id_lst.append(c.pk)


            #multi staff table creation
            ratio = 0.0
            if c.sales_staff.all().count() > 0:
                count = c.sales_staff.all().count()
                ratio = float(c.ratio) / float(count)

            # for sale in c.sales_staff.all():
            #     multi = Multistaff(sa_transacno=sa_transacno,item_code=multi_itemcode,
            #     emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
            #     dt_lineno=c.lineno)
            #     multi.save()
                # print(multi.id,"multi")

            for sale in c.multistaff_ids.all():
                multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
                emp_code=sale.emp_code,ratio=sale.ratio,salesamt="{:.2f}".format(float(sale.salesamt)),type=None,isdelete=False,role=1,
                dt_lineno=c.lineno,salescommpoints=sale.salescommpoints)
                multi.save()
                sale.sa_transacno = sa_transacno 
                sale.save()    


            desc = "Top Up Amount: "+str("{:.2f}".format(float(c.deposit)))
            if c.treatment_account is not None:
                tp_balance = acc_ids.balance + c.deposit if acc_ids.balance else c.deposit
                
                #treatment Account creation
                treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                description=desc,type="Top Up",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(tp_balance)),
                User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=acc_ids.ref_transacno,sa_transacno=sa_transacno,
                qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)) if outstanding_acc is not None and outstanding_acc > 0 else 0,deposit="{:.2f}".format(float(c.deposit)),
                treatment_parentcode=c.treatment_account.treatment_parentcode,sa_status="SA",
                cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),dt_lineno=c.lineno,
                Site_Codeid=site,site_code=site.itemsite_code,itemcart=c,
                ref_no=sa_transacno)
                treatacc.save()
                treatacc.sa_date = pay_date
                treatacc.sa_time = pay_time
                treatacc.save()

                searcids = TreatmentPackage.objects.filter(treatment_parentcode=c.treatment_account.treatment_parentcode).first()
                if searcids:
                    trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=c.treatment_account.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                    searcids.balance = "{:.2f}".format(float(trmtAccObj.balance)) 
                    searcids.outstanding = "{:.2f}".format(float(trmtAccObj.outstanding))
                    searcids.save()


            # print(treatacc.id,"treatacc")
            elif c.deposit_account is not None:
                tp_balance = acc_ids.balance + c.deposit if acc_ids.balance else c.deposit
    
                #deposit Account creation
                depositacc = DepositAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                description=desc,type="Top Up",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(tp_balance)),
                user_name=fmspw.pw_userlogin,sa_transacno=c.deposit_account.sa_transacno,qty=c.quantity,
                outstanding="{:.2f}".format(float(outstanding_acc)) if outstanding_acc is not None and outstanding_acc > 0 else 0,deposit="{:.2f}".format(float(c.deposit)),treat_code=treat_code,sa_status="SA",
                cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),dt_lineno=c.lineno,
                Site_Codeid=site,site_code=site.itemsite_code,Item_Codeid=c.itemcodeid,
                item_code=c.itemcodeid.item_code,ref_transacno=c.deposit_account.ref_transacno,
                ref_productcode=c.deposit_account.ref_productcode,ref_code=sa_transacno,
                deposit_type="PRODUCT",item_barcode=str(c.itemcodeid.item_code)+"0000",
                item_description=c.itemcodeid.item_name,void_link=None,lpackage=False,package_code=None)
                depositacc.save()
                depositacc.sa_date = pay_date
                depositacc.sa_time = pay_time
                depositacc.save()
                
                
                # if depositacc.pk:
                #     decontrolobj.control_no = int(decontrolobj.control_no) + 1
                #     decontrolobj.save()

            elif c.prepaid_account is not None:
                #prepaid Account creation

                prepaid_valid_period = None
                if c.itemcodeid and c.itemcodeid.prepaid_valid_period:
                    prepaid_valid_period = timezone.now() + timedelta(int(c.itemcodeid.prepaid_valid_period))
                pp_bonus = c.itemcodeid.prepaid_value - c.itemcodeid.prepaid_sell_amt
                
                c.prepaid_account.status = False
                c.prepaid_account.save()
                outstanding = float(c.prepaid_account.outstanding) - float(c.deposit)

                if outstanding == 0:
                    remain = c.prepaid_account.remain + c.deposit + c.prepaid_account.pp_bonus
                else:
                    remain = c.prepaid_account.remain + c.deposit


                prepaidacc = PrepaidAccount(pp_no=c.prepaid_account.pp_no,pp_type=c.itemcodeid.item_range if c.itemcodeid.item_range else None,
                pp_desc=c.itemcodeid.item_name,exp_date=prepaid_valid_period,Cust_Codeid=cust_obj,
                cust_code=cust_obj.cust_code,cust_name=cust_obj.cust_name,pp_amt= c.prepaid_account.pp_amt,
                pp_total=c.prepaid_account.pp_total, pp_bonus=c.prepaid_account.pp_bonus,transac_no="",item_no="",
                use_amt=0,remain=remain,ref1="",ref2="",status=True,site_code=site.itemsite_code,
                sa_status="TOPUP",exp_status=True,voucher_no="",isvoucher=False,has_deposit=True,
                topup_amt=c.deposit,outstanding=outstanding if outstanding is not None and outstanding > 0 else 0,active_deposit_bonus=False,topup_no=sa_transacno,
                topup_date=timezone.now(),line_no=c.prepaid_account.line_no,
                staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                staff_name=','.join([v.display_name for v in salesstaff if v.display_name]), 
                pp_type2=c.prepaid_account.pp_type2,condition_type1=c.prepaid_account.condition_type1,
                pos_daud_lineno=c.prepaid_account.pos_daud_lineno,Site_Codeid=site,
                Item_Codeid=c.itemcodeid,item_code=c.itemcodeid.item_code)
                prepaidacc.save()
                prepaidacc.sa_date = pay_date
                prepaidacc.start_date = pay_date
                prepaidacc.save()

            totaldisc = c.discount_amt + c.additional_discountamt
            totalpercent = c.discount + c.additional_discount


            #PosDisc Creation for each cart line with or without line disc (disc per/amt = line disc + trasac disc)
            # if transc disc for whole cart is applied that time need to create one record in PosDisc (disc per/amt = trasac disc).
            # discreason = None
            # if c.pos_disc.all().exists():
            #     # for d in c.disc_reason.all():
            #     #     if d.r_code == '100006' and d.r_desc == 'Others':
            #     #         discreason = c.discreason_txt
            #     #     elif d.r_desc:
            #     #         discreason = d.r_desc  
                        
            #     for po in c.pos_disc.all():
            #         po.sa_transacno = sa_transacno
            #         po.dt_status = "SA"
            #         po.dt_price = c.price
            #         po.save()
            # else:
            #     if totaldisc == 0.0 or totalpercent == 0.0 and len(c.pos_disc.all()) == 0:
            #         posdisc = PosDisc(sa_transacno=sa_transacno,dt_itemno=c.itemcodeid.item_code+"0000",disc_amt=totaldisc,
            #         disc_percent=totalpercent,dt_lineno=c.lineno,remark=discreason,site_code=site.itemsite_code,
            #         dt_status="SA",dt_auto=0,line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=c.price,istransdisc=False)
            #         posdisc.save()
                    # print(posdisc.pk,"posdisc")

                
            # #HoldItemDetail creation for retail products
            # if c.itemcodeid.Item_Divid.itm_code == 1 and c.itemcodeid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.itm_isactive == True:
            #     con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #     if not con_obj:
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
            #         return Response(result, status=status.HTTP_400_BAD_REQUEST) 


            #     product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                
            #     hold = HoldItemDetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
            #     transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
            #     hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #     hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=c.trans_amt,hi_qty=c.holditemqty,
            #     hi_discamt=totaldisc,hi_discpercent=totalpercent,hi_discdesc=None,
            #     hi_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
            #     hi_lineno=c.lineno,hi_uom=c.item_uom.uom_desc,hold_item=True,hi_deposit=c.deposit,
            #     holditemqty=c.holditemqty,status="OPEN",sa_custno=cust_obj.cust_code,
            #     sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
            #     product_issues_no=product_issues_no)
            #     hold.save()
            #     # print(hold.pk,"hold")
            #     if hold.pk:
            #         con_obj.control_no = int(con_obj.control_no) + 1
            #         con_obj.save()

            # if '0' in str(c.quantity):
            #     no = str(c.quantity).split('0')
            #     if no[0] == '':
            #         number = no[1]
            #     else:
            #         number = c.quantity
            # else:
            #     number = c.quantity

            # dtl_st_ref_treatmentcode = ""
            # for i in range(1,int(number)+1):
            #     treat = c
            #     Price = c.deposit
            #     Unit_Amount = Price / c.quantity
            #     times = str(i).zfill(2)
            #     treatment_no = str(c.quantity).zfill(2)
            #     treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
            #     treatment_parentcode=treatment_parentcode,course=treat.itemcodeid.item_desc,times=times,
            #     treatment_no=treatment_no,price=Price,unit_amount=Unit_Amount,Cust_Codeid=treat.cust_noid,
            #     cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
            #     status="Open",item_code=treat.itemcodeid.item_code,Item_Codeid=treat.itemcodeid,
            #     sa_transacno=sa_transacno,sa_status="SA",
            #     dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,
            #     treatment_account=treatacc)

            #     #and str(treatmentid.treatment_code) == str(treatment_parentcode)+"-"+"01"
            #     if c.helper_ids.exists():
            #         for h in c.helper_ids.all().filter(times=times):
                        
            #             # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                        
            #             treatmentid.status = "Done"
            #             wp1 = h.workcommpoints / float(c.helper_ids.all().filter(times=times).count())
            #             share_amt = treatmentid.unit_amount / float(c.helper_ids.all().filter(times=times).count())

            #             TmpItemHelper.objects.filter(id=h.id).update(item_code=treatment_parentcode+"-"+str(times),
            #             item_name=c.itemcodeid.item_desc,line_no=dtl.dt_lineno,sa_transacno=sa_transacno,
            #             amount=treatmentid.unit_amount,sa_date=dtl.sa_date,site_code=site.itemsite_code,
            #             wp1=wp1,wp2=0.0,wp3=0.0)

            #             # Item helper create
            #             helper = ItemHelper(item_code=treatment_parentcode+"-"+str(times),item_name=c.itemcodeid.item_desc,
            #             line_no=dtl.dt_lineno,sa_transacno=sa_transacno,amount=treatmentid.unit_amount,
            #             helper_name=h.helper_name,helper_code=h.helper_code,sa_date=dtl.sa_date,
            #             site_code=site.itemsite_code,share_amt=share_amt,helper_transacno=sa_transacno,
            #             wp1=wp1,wp2=0.0,wp3=0.0)
            #             helper.save()
            #             # print(helper.id,"helper")

            #             #appointment treatment creation
            #             if h.appt_fr_time and h.appt_to_time != False and h.add_duration != False:
            #                 stock_obj = c.itemcodeid

            #                 if stock_obj.srv_duration is None or float(stock_obj.srv_duration) == 0.0:
            #                     stk_duration = 60
            #                 else:
            #                     stk_duration = int(stock_obj.srv_duration)

            #                 stkduration = int(stk_duration) + 30
            #                 # print(stkduration,"stkduration")

            #                 hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
            #                 start_time =  get_in_val(self, h.appt_fr_time)
            #                 starttime = datetime.datetime.strptime(start_time, "%H:%M")

            #                 end_time = starttime + datetime.timedelta(minutes = stkduration)
            #                 endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            #                 duration = hrs

            #                 treat_all = Treatment.objects.filter(sa_transacno=sa_transacno,treatment_parentcode=treatment_parentcode)
            #                 length = [t.status for t in treat_all if t.status == 'Done']
            #                 if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
            #                     master_status = "Done"
            #                 else:
            #                     master_status = "Open"

            #                 master = Treatment_Master(treatment_code=str(treatment_parentcode)+"-"+str(times),
            #                 treatment_parentcode=treatment_parentcode,sa_transacno=sa_transacno,
            #                 course=stock_obj.item_desc,times=times,treatment_no=treatment_no,
            #                 price=stock_obj.item_price,cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,
            #                 cust_name=cust_obj.cust_name,status=master_status,unit_amount=stock_obj.item_price,
            #                 Item_Codeid=stock_obj,item_code=stock_obj.item_code,
            #                 sa_status="SA",dt_lineno=dtl.dt_lineno,type="N",duration=stkduration,
            #                 Site_Codeid=site,site_code=site.itemsite_code,
            #                 trmt_room_code=h.Room_Codeid.room_code,Trmt_Room_Codeid=h.Room_Codeid,
            #                 Item_Class=stock_obj.Item_Classid,PIC=stock_obj.Stock_PIC,
            #                 start_time=h.appt_fr_time,end_time=h.appt_to_time,add_duration=h.add_duration,
            #                 appt_remark=stock_obj.item_desc,requesttherapist=False)

            #                 master.save()
            #                 master.emp_no.add(h.helper_id.pk)
            #                 # print(master.id,"master")

            #                 ctrl_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #                 if not ctrl_obj:
            #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
            #                     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                            
            #                 appt_code = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                            
            #                 channel = ApptType.objects.filter(appt_type_code="10003",appt_type_isactive=True).first()
            #                 if not channel:
            #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
            #                     return Response(result, status=status.HTTP_400_BAD_REQUEST) 


            #                 appt = Appointment(cust_noid=cust_obj,cust_no=cust_obj.cust_code,appt_date=date.today(),
            #                 appt_fr_time=h.appt_fr_time,Appt_typeid=channel,appt_type=channel.appt_type_desc,
            #                 appt_phone=cust_obj.cust_phone2,appt_remark=stock_obj.item_desc,
            #                 emp_noid=h.helper_id,emp_no=h.helper_id.emp_code,emp_name=h.helper_id.display_name,
            #                 cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
            #                 appt_to_time=h.appt_to_time,Appt_Created_Byid=fmspw,
            #                 appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
            #                 Room_Codeid=h.Room_Codeid,room_code=h.Room_Codeid.room_code,
            #                 Source_Codeid=h.Source_Codeid,source_code=h.Source_Codeid.source_code,
            #                 cust_refer=cust_obj.cust_refer,requesttherapist=False,new_remark=h.new_remark,
            #                 item_code=stock_obj.item_code,sa_transacno=sa_transacno,treatmentcode=str(treatment_parentcode)+"-"+str(times))
            #                 appt.save()

            #                 if appt.pk:
            #                     master.Appointment = appt
            #                     master.appt_time = timezone.now()
            #                     master.save()
            #                     ctrl_obj.control_no = int(ctrl_obj.control_no) + 1
            #                     ctrl_obj.save()
                            
            #         #treatment Account creation for done treatment 01
            #         if c.helper_ids.all().filter(times=times).first():
            #             acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,treatment_parentcode=treatment_parentcode).order_by('id').last()
            #             td_desc = str(stock_obj.item_desc)
            #             balance = acc_ids.balance - treatmentid.unit_amount

            #             treatacc_td = TreatmentAccount(Cust_Codeid=cust_obj,
            #             cust_code=cust_obj.cust_code,ref_no=treatmentid.treatment_code,
            #             description=td_desc,type='Sales',amount=-treatmentid.unit_amount,balance=balance,
            #             User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=treatmentid.sa_transacno,
            #             sa_transacno=sa_transacno,qty=1,outstanding=treatacc.outstanding,deposit=0.0,
            #             treatment_parentcode=treatmentid.treatment_parentcode,treatment_code="",
            #             sa_status="SA",cas_name=fmspw.pw_userlogin,
            #             sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #             sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
            #             dt_lineno=c.lineno,Site_Codeid=site,site_code=site.itemsite_code,
            #             treat_code=treatmentid.treatment_parentcode,itemcart=c)
            #             treatacc_td.save()
            #             # print(treatacc_td.id,"treatacc_td")
                        
            #             if dtl_st_ref_treatmentcode == "":
            #                 dtl_st_ref_treatmentcode = str(treatment_parentcode)+"-"+str(times)
            #             elif not dtl_st_ref_treatmentcode == "":
            #                 dtl_st_ref_treatmentcode = str(dtl_st_ref_treatmentcode) +"-"+str(times)


            #     treatmentid.save()
            #     # appt_time=treat.appt_time,Trmt_Room_Codeid=treat.Trmt_Room_Codeid,trmt_room_code=treat.trmt_room_code,
            #     # print(treatmentid.id,"treatment_id")

            # if treatacc and treatmentid:
            #     controlobj.control_no = int(controlobj.control_no) + 1
            #     controlobj.save()

            # # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
            # dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
            # dtl.first_trmt_done = True
            # dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
            # dtl.first_trmt_done_staff_name = ','.join([v.helper_id.display_name for v in c.helper_ids.all() if v.helper_id.display_name])
            # dtl.save()

        return id_lst
    # except Exception as e:
    #     invalid_message = str(e)
    #     return general_error_response(invalid_message)
    

def invoice_sales(self, request, sales_ids,sa_transacno, cust_obj, outstanding, pay_date, pay_time):
    # try:
    if self:
        outstanding = 0.00
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        empl = fmspw.Emp_Codeid
        gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
        id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0
        outstanding_new = 0.0
        
        for idx, c in enumerate(sales_ids, start=1):
            if idx == 1:
                alservice_staff = c.service_staff.all().first()

            # if not c.treatment.helper_ids.all().exists():
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment done service staffs not mapped!!",'error': True} 
            #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 


            # print(c,"cc")
            # controlobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
            # if not controlobj:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
            #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            # treatment_parentcode = "TRM"+str(controlobj.control_prefix)+str(controlobj.Site_Codeid.itemsite_code)+str(controlobj.control_no)
            
            service_staff = c.service_staff.all().first()
            servicestaff = c.service_staff.all()

            # total = c.price * c.quantity
            totQty += c.quantity
            # discount_amt += float(c.discount_amt)
            # additional_discountamt += float(c.additional_discountamt)
            total_disc += c.discount_amt + c.additional_discountamt
            # dt_discPercent = (float(total_disc) * 100) / float(value['subtotal'])
            dt_discPercent = c.discount + c.additional_discount
            time = c.treatment.times 

            if c.is_foc == True:
                isfoc = True
                item_remarks = c.focreason.foc_reason_ldesc if c.focreason and c.focreason.foc_reason_ldesc else None 
                dt_itemdesc = str(time)+"/"+str(c.treatment.treatment_no)+" "+str(c.itemcodeid.item_name)+" "+"(FOC)" 

            else:
                isfoc = False  
                item_remarks = None 
                dt_itemdesc = str(time)+"/"+str(c.treatment.treatment_no)+" "+str(c.itemdesc)
            
            sales = "";service = ""
            if c.sales_staff.all():
                for i in c.sales_staff.all():
                    if sales == "":
                        sales = sales + i.display_name
                    elif not sales == "":
                        sales = sales +","+ i.display_name
            if c.service_staff.all(): 
                for s in c.service_staff.all():
                    if service == "":
                        service = service + s.display_name
                    elif not service == "":
                        service = service +","+ s.display_name 
            
            
            # dt_itemno=c.itemcodeid.item_code+"0000" if c.itemcodeid else None
            # ,topup_outstanding=
            dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid if c.itemcodeid else None,
            dt_itemno='',dt_itemdesc=dt_itemdesc if dt_itemdesc else None,dt_price=c.price if c.price else 0.0,
            dt_promoprice="{:.2f}".format(float(c.discount_price)) if c.discount_price else 0.0,dt_amt="{:.2f}".format(float(c.trans_amt)) if c.trans_amt else 0.0,dt_qty=c.quantity if c.quantity else 0.0,dt_discamt=0.0,
            dt_discpercent=0.0,dt_Staffnoid=service_staff if service_staff else None,dt_staffno=service_staff.emp_code if service_staff and service_staff.emp_code else None,
            dt_staffname=service_staff.display_name if service_staff and service_staff.display_name else None,dt_discuser=None,ItemSite_Codeid=site,
            itemsite_code=site.itemsite_code,dt_transacamt=0.0,dt_deposit=0.0,dt_lineno=c.lineno,
            itemcart=c,st_ref_treatmentcode=c.treatment.treatment_code if c.treatment.treatment_code else '',first_trmt_done=False,
            first_trmt_done_staff_code="",first_trmt_done_staff_name="",
            record_detail_type="TD",trmt_done_staff_code=','.join([v.emp_code for v in servicestaff if v.emp_code]),
            trmt_done_staff_name=','.join([v.display_name for v in servicestaff if v.display_name]),
            trmt_done_id=c.treatment.treatment_code if c.treatment.treatment_code else '',trmt_done_type="N",gst_amt_collect=0.0,
            dt_remark=c.remark if c.remark else '',isfoc=isfoc,item_remarks=item_remarks,
            item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
            staffs = "/"+" "+ service)
            #appt_time=app_obj.appt_fr_time,
            dtl.save()                
            dtl.sa_date = pay_date
            dtl.sa_time = pay_time
            dtl.save()
            # print(dtl.pk,"dtl")
            if dtl.pk not in id_lst:
                id_lst.append(c.pk)


            #multi staff table creation
            ratio = 0.0
            if c.sales_staff.all().count() > 0:
                count = c.sales_staff.all().count()
                ratio = float(c.ratio) / float(count)

            multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000" if c.itemcodeid else None,
            emp_code=service_staff.emp_code if service_staff.emp_code else None,ratio=c.ratio if c.ratio else None,salesamt="{:.2f}".format(float(c.deposit)) if c.deposit else 0.0,type=None,isdelete=False,role=1,
            dt_lineno=c.lineno if c.lineno else None)
            multi.save()
            # print(multi.id,"multi")

            

            # .exclude(type='Sales')
            # acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment.sa_transacno,
            # treatment_parentcode=c.treatment.treatment_parentcode,Site_Codeid=site).order_by('id').last()

            # acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment.sa_transacno,
            # treatment_parentcode=c.treatment.treatment_parentcode,site_code=site.itemsite_code).order_by('id').last()
            #acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment.sa_transacno,
            #treatment_parentcode=c.treatment.treatment_parentcode).order_by('id').last()
            acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment.sa_transacno,
            treatment_parentcode=c.treatment.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
            # print(acc_ids,acc_ids.pk,"kk")
            deduct_unitamt = c.multi_treat.filter().aggregate(amount=Coalesce(Sum('unit_amount'), 0)) 
            # print(deduct_unitamt,"deduct_unitamt") 
            dtl.dt_itemdesc = str(dtl.dt_itemdesc) +" "+"$"+str("{:.2f}".format(float(deduct_unitamt['amount'] )))
            dtl.save()
            Balance = 0
            if acc_ids:
                # Balance = acc_ids.balance - c.treatment.unit_amount if acc_ids.balance else c.treatment.unit_amount
                Balance = acc_ids.balance - (float(deduct_unitamt['amount'])) if acc_ids.balance else 0.0
                if acc_ids.outstanding:
                    outstanding += acc_ids.outstanding

            
            amount = -float("{:.2f}".format(float(deduct_unitamt['amount'] ))) if deduct_unitamt['amount'] else 0.0 
            
            # if ct.type in ['FFd','FFi']:
            #     if acc_ids and acc_ids.balance > 0:
            #         # print(acc_ids.balance,"hhh")
            #         frt_treatids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('pk').first()
            #         amount = -float("{:.2f}".format(float(frt_treatids.unit_amount * c.quantity ))) if frt_treatids and frt_treatids.unit_amount else 0.0 
            #         Balance = acc_ids.balance - (frt_treatids.unit_amount * c.quantity) if acc_ids.balance else c.treatment.unit_amount

            

            # if not c.multi_treat.all()[0].type == 'FFi':
            #treatment Account creation
            treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
            description=dt_itemdesc,ref_no=c.treatment.treatment_code if c.treatment.treatment_code else '',type="Sales",
            amount=amount,balance="{:.2f}".format(float(Balance)),User_Nameid=fmspw,
            user_name=fmspw.pw_userlogin,ref_transacno=c.treatment.sa_transacno if c.treatment.sa_transacno else None,sa_transacno=sa_transacno,
            qty=c.quantity if c.quantity else None,outstanding="{:.2f}".format(float(acc_ids.outstanding)) if acc_ids and acc_ids.outstanding is not None and acc_ids.outstanding > 0 else 0.0,deposit=0,
            treatment_parentcode=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else '',treatment_code="",sa_status="SA",
            cas_name=fmspw.pw_userlogin,sa_staffno=service_staff.emp_code if service_staff.emp_code else '',
            sa_staffname=service_staff.display_name if service_staff.display_name else '',dt_lineno=c.lineno,
            Site_Codeid=site,site_code=site.itemsite_code,itemcart=c)
            
            treatacc.save()
            treatacc.sa_date = pay_date
            treatacc.sa_time = pay_time
            treatacc.save()

            if not c.exchange_id: 
                PackageAuditingLog(treatment_parentcode=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else '',
                user_loginid=fmspw,package_type="Redeem",pa_qty=c.quantity if c.quantity else None).save()    
            
            course_ct = c.multi_treat.all()[0].course

            # print(treatacc.id,"treatacc")
            helper = c.treatment.helper_ids.all().first()
            # trmt_up = Treatment.objects.filter(pk=c.treatment.pk).update(status="Done",treatment_date=timezone.now(),
            # trmt_room_code=helper.Room_Codeid.room_code if helper.Room_Codeid else None,record_status='PENDING',
            # transaction_time=timezone.now(),treatment_count_done=1)
            for ct in c.multi_treat.all():
                # print(c.treatment.pk-iqty,"iqty")
                if ct.type != "FFi":
                    trmt_up = Treatment.objects.filter(pk=ct.pk).update(status="Done",treatment_date=pay_date,
                    trmt_room_code=helper.Room_Codeid.room_code if helper.Room_Codeid else None,record_status='PENDING',
                    transaction_time=timezone.now(),treatment_count_done=1)
                else:
                    if ct.type == "FFi":
                        tmp_treatment_ids = Tmptreatment.objects.filter(treatment_id__pk=ct.pk,status='Open').first()
                        if tmp_treatment_ids:
                            tm = tmp_treatment_ids

                            deductpoint = None
                            if ct and ct.flexipoints and tm.newservice_id.redeempoints:
                                if ct.flexipoints > tm.newservice_id.redeempoints:
                                    deductpoint = ct.flexipoints - tm.newservice_id.redeempoints

                            Treatment.objects.filter(pk=ct.pk).update(treatment_date=pay_date,
                            record_status='PENDING',status="Done",
                            transaction_time=timezone.now(),treatment_count_done=1,
                            course=tm.newservice_id.item_name,flexipoints=deductpoint,
                            redeempoints=tm.newservice_id.redeempoints if tm.newservice_id.redeempoints else None)
                            tm.status = "Done"
                            tm.save()
                        else:
                            trmt_up = Treatment.objects.filter(pk=ct.pk).update(status="Done",treatment_date=pay_date,
                            trmt_room_code=helper.Room_Codeid.room_code if helper.Room_Codeid else None,record_status='PENDING',
                            transaction_time=timezone.now(),treatment_count_done=1)

                        


            
            ct = c.multi_treat.all()[0]  
            frtstreat_ids = TreatmentPackage.objects.filter(treatment_parentcode=ct.treatment_parentcode).first()
            efdone_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('pk').count()
            efdtreat_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('-pk').first()
            efopen_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Open").order_by('pk')
            # print(efopen_ids,"efopen_ids")
            if ct.type in ['FFd','FFi']:
                if ct.expiry and ct.treatment_limit_times is not None:
                    splte = str(ct.expiry).split(' ')
                    expiry = splte[0]
                    if expiry >= str(date.today()):
                        if int(ct.treatment_limit_times) == 0:
                            if not efopen_ids:
                                # if ct.treatment_limit_times > efdone_ids:
                                times_v = str(int(efdtreat_ids.times) + 1).zfill(2)
                                treatment_code = ct.treatment_parentcode+"-"+times_v
                                treatids = Treatment(treatment_code=treatment_code,course=frtstreat_ids.course if frtstreat_ids else ct.course,times=times_v,
                                treatment_no=times_v,price=frtstreat_ids.totalprice if frtstreat_ids and frtstreat_ids.totalprice else ct.price,treatment_date=pay_date,
                                cust_name=ct.cust_name,Cust_Codeid=ct.Cust_Codeid,
                                cust_code=ct.cust_code,status="Open",unit_amount=0,
                                Item_Codeid=ct.Item_Codeid,item_code=ct.item_code,treatment_parentcode=ct.treatment_parentcode,
                                sa_transacno=ct.sa_transacno,
                                sa_status=ct.sa_status,
                                remarks=ct.remarks,
                                dt_lineno=ct.dt_lineno,expiry=ct.expiry,package_code=ct.package_code,
                                Site_Codeid=ct.Site_Codeid,site_code=ct.site_code,type=ct.type,treatment_limit_times=ct.treatment_limit_times,
                                service_itembarcode=ct.service_itembarcode,isfoc=ct.isfoc,Trmt_Room_Codeid=ct.Trmt_Room_Codeid,
                                trmt_room_code=ct.trmt_room_code,trmt_is_auto_proportion=ct.trmt_is_auto_proportion,
                                treatment_account=ct.treatment_account).save()
                                if treatids:
                                    stfd_ids = Treatmentids.objects.filter(treatment_int=treatids.pk)
                                    if not stfd_ids: 
                                        Treatmentids(treatment_parentcode=ct.treatment_parentcode,
                                                    treatment_int=treatids.pk).save()
                            
                
            if ct.type == "FFi":
                for ctr in c.multi_treat.all():
                    ctr.price = 0
                    ctr.save()

            
            
            # if c.is_flexinewservice == True and ct.type == "FFi":
                
            #     tmp_treatment_ids = Tmptreatment.objects.filter(treatment_id=ct,status='Open')
            #     # print(tmp_treatment_ids,"tmp_treatment_ids")
            #     if tmp_treatment_ids:
            #         # for tm in tmp_treatment_ids:
            #         for idx, tm in enumerate(tmp_treatment_ids, start=1):    
            #             etreat_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('-pk').first()
            #             # print(len(etreat_ids),"etreat_ids")
            #             # if not etreat_ids:
            #             #     times_t = "01" ; treatment_no_t = "01"
            #             # else:
            #             times_t = str(int(etreat_ids.times) + 1).zfill(2)
            #             # print(times_t,"times_t")
            #             treatment_no_t = str(int(etreat_ids.times) + 1).zfill(2)
                        
            #             # print(times_t,"times_t")
            #             # print(treatment_no_t,"treatment_no_t")
            #             f_treatment_code = ct.treatment_parentcode+"-"+times_t 
            #             # print(f_treatment_code,"f_treatment_code")  

            #             ftreat_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('-pk').first()
                        
            #             deductpoint = None
            #             if ftreat_ids and ftreat_ids.flexipoints and tm.newservice_id.redeempoints:
            #                 if ftreat_ids.flexipoints > tm.newservice_id.redeempoints:
            #                     deductpoint = ftreat_ids.flexipoints - tm.newservice_id.redeempoints

            #             if idx != 1:  
            #                 v = c.multi_treat.filter(~Q(pk=ct.pk)).filter(status='Open').first()
            #                 if v:
            #                     Treatment.objects.filter(pk=v.pk).update(treatment_date=pay_date,
            #                     record_status='PENDING',status="Done",price=0,
            #                     transaction_time=timezone.now(),treatment_count_done=1,
            #                     course=tm.newservice_id.item_name,flexipoints=deductpoint,
            #                     redeempoints=tm.newservice_id.redeempoints if tm.newservice_id.redeempoints else None)
        
            #                 # gtreatids = Treatment(treatment_code=f_treatment_code,course=tm.newservice_id.item_name,times=times_t,
            #                 # treatment_no=treatment_no_t,price=ct.price,treatment_date=pay_date,
            #                 # next_appt=ct.next_appt,cust_name=ct.cust_name,Cust_Codeid=ct.Cust_Codeid,
            #                 # cust_code=ct.cust_code,status="Done",unit_amount=0,
            #                 # Item_Codeid=tm.newservice_id,item_code=tm.newservice_id.item_code+"0000",treatment_parentcode=ct.treatment_parentcode,
            #                 # prescription=ct.prescription,allergy=ct.allergy,sa_transacno=ct.sa_transacno,
            #                 # sa_status=ct.sa_status,record_status=ct.record_status,appt_time=ct.appt_time,
            #                 # remarks=ct.remarks,duration=ct.duration,hold_item=ct.hold_item,transaction_time=ct.transaction_time,
            #                 # dt_lineno=ct.dt_lineno,expiry=ct.expiry,lpackage=ct.lpackage,package_code=ct.package_code,
            #                 # Site_Codeid=ct.Site_Codeid,site_code=ct.site_code,type=ct.type,treatment_limit_times=ct.treatment_limit_times,
            #                 # treatment_count_done=ct.treatment_count_done,treatment_history_last_modify=ct.treatment_history_last_modify,
            #                 # service_itembarcode=tm.newservice_id.item_code+"0000",isfoc=ct.isfoc,Trmt_Room_Codeid=ct.Trmt_Room_Codeid,
            #                 # trmt_room_code=ct.trmt_room_code,trmt_is_auto_proportion=ct.trmt_is_auto_proportion,
            #                 # smsout=ct.smsout,emailout=ct.emailout,treatment_account=ct.treatment_account,
            #                 # flexipoints=deductpoint,redeempoints=tm.newservice_id.redeempoints if tm.newservice_id.redeempoints else None)
            #                 # gtreatids.save()

            #                 # if ct.helper_ids.exists():

                               
            #                 #     for h in ct.helper_ids.all():
                                    
            #                 #         # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                                    
            #                 #         # treatmentid.status = "Done"
            #                 #         # wp1 = h.workcommpoints / float(c.treatment.helper_ids.all().count())
            #                 #         wp1 = h.wp1
            #                 #         share_amt = float(gtreatids.unit_amount) / float(c.treatment.helper_ids.all().count())
            #                 #         if h.work_amt and h.work_amt > 0:
            #                 #             share_amt =  h.work_amt


                                  
            #                 #         # Item helper create
            #                 #         helper = ItemHelper(item_code=f_treatment_code,item_name=tm.newservice_id.item_name,
            #                 #         line_no=dtl.dt_lineno,sa_transacno=c.treatment.sa_transacno,amount=gtreatids.unit_amount,
            #                 #         helper_name=h.helper_name,helper_code=h.helper_code,sa_date=dtl.sa_date,
            #                 #         site_code=site.itemsite_code,share_amt="{:.2f}".format(float(share_amt)),helper_transacno=sa_transacno,
            #                 #         wp1=wp1,wp2=0.0,wp3=0.0,percent=h.percent,work_amt="{:.2f}".format(float(h.work_amt)) if h.work_amt else h.work_amt,times=times_t,treatment_no=treatment_no_t)
            #                 #         helper.save()
            #                 #         ItemHelper.objects.filter(id=helper.id).update(sa_date=pay_date)
            #                 #         # print(helper.id,"helper")

            #             else:
            #                 if idx == 1:
            #                     ct.course = tm.newservice_id.item_name
            #                     ct.flexipoints = deductpoint
            #                     ct.redeempoints = tm.newservice_id.redeempoints if tm.newservice_id.redeempoints else None
            #                     ct.save()

                        
            #             tm.status = "Done"
            #             tm.save()
                        
            #             # if c.multi_treat.all()[0].type == 'FFi':
            #             #     facc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment.sa_transacno,
            #             #     treatment_parentcode=c.treatment.treatment_parentcode).order_by('sa_date','sa_time','id').last()

            #             #     if c.multi_treat.all()[0].type == 'FFi' and facc_ids.balance == 0:
            #             #         amount = 0
            #             #         Balance = 0

            #             #     dtitemdesc = str(times_t)+"/"+str(treatment_no_t)+" "+str(tm.newservice_id.item_name)

            #             #     if idx != 1:
            #             #         treatacc_id = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
            #             #         description=dtitemdesc,ref_no=f_treatment_code,type="Sales",
            #             #         amount=amount,balance="{:.2f}".format(float(Balance)),User_Nameid=fmspw,
            #             #         user_name=fmspw.pw_userlogin,ref_transacno=c.treatment.sa_transacno if c.treatment.sa_transacno else None,sa_transacno=sa_transacno,
            #             #         qty=c.quantity if c.quantity else None,outstanding="{:.2f}".format(float(acc_ids.outstanding)) if acc_ids and acc_ids.outstanding is not None and acc_ids.outstanding > 0 else 0.0,deposit=0,
            #             #         treatment_parentcode=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else '',treatment_code="",sa_status="SA",
            #             #         cas_name=fmspw.pw_userlogin,sa_staffno=service_staff.emp_code if service_staff.emp_code else '',
            #             #         sa_staffname=service_staff.display_name if service_staff.display_name else '',dt_lineno=c.lineno,
            #             #         Site_Codeid=site,site_code=site.itemsite_code,treat_code=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else None,itemcart=c,
            #             #         focreason=item_remarks)
            #             #         treatacc_id.save()
            #             #         treatacc_id.sa_date = pay_date
            #             #         treatacc_id.sa_time = pay_time
            #             #         treatacc_id.save()
                    
            #         ct.status="Done"
            #         ct.save() 

            #         done_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('pk').count()
            #         if ct.treatment_limit_times == 0:
            #             if ct.treatment_limit_times > done_ids or ct.treatment_limit_times == 0:
            #                 eetreat_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('-pk').first()
                            
            #                 timess_t = str(int(eetreat_ids.times) + 1).zfill(2)
            #                 treatment_no_tr = str(int(eetreat_ids.times) + 1).zfill(2)
                            
                        
            #                 ff_treatment_code = ct.treatment_parentcode+"-"+timess_t 

                            
            #                 goptreatids = Treatment(treatment_code=ff_treatment_code,course=frtstreat_ids.course,times=timess_t,
            #                 treatment_no=treatment_no_tr,price=ct.price,treatment_date=pay_date,
            #                 next_appt=ct.next_appt,cust_name=ct.cust_name,Cust_Codeid=ct.Cust_Codeid,
            #                 cust_code=ct.cust_code,status="Open",unit_amount=0,
            #                 Item_Codeid=frtstreat_ids.Item_Codeid,item_code=frtstreat_ids.Item_Codeid.item_code+"0000",treatment_parentcode=ct.treatment_parentcode,
            #                 prescription=ct.prescription,allergy=ct.allergy,sa_transacno=ct.sa_transacno,
            #                 sa_status=ct.sa_status,record_status=ct.record_status,appt_time=ct.appt_time,
            #                 remarks=ct.remarks,duration=ct.duration,hold_item=ct.hold_item,transaction_time=ct.transaction_time,
            #                 dt_lineno=ct.dt_lineno,expiry=ct.expiry,lpackage=ct.lpackage,package_code=ct.package_code,
            #                 Site_Codeid=ct.Site_Codeid,site_code=ct.site_code,type=ct.type,treatment_limit_times=ct.treatment_limit_times,
            #                 treatment_count_done=ct.treatment_count_done,treatment_history_last_modify=ct.treatment_history_last_modify,
            #                 service_itembarcode=frtstreat_ids.Item_Codeid.item_code+"0000",isfoc=ct.isfoc,Trmt_Room_Codeid=ct.Trmt_Room_Codeid,
            #                 trmt_room_code=ct.trmt_room_code,trmt_is_auto_proportion=ct.trmt_is_auto_proportion,
            #                 smsout=ct.smsout,emailout=ct.emailout,treatment_account=ct.treatment_account)
                            
            #                 goptreatids.save() 
                        
                    
                   
            #         ct.price = 0
            #         ct.save() 
            #         Treatment.objects.filter(pk=ct.pk).update(treatment_date=pay_date,
            #         record_status='PENDING',
            #         transaction_time=timezone.now(),treatment_count_done=1)
 
            # else:
            #     if ct.type == "FFi":
                    
            #         treat_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('-pk').first()
                    
            #         # if not treat_ids:
            #         #     timest = "01" ; treatment_not = "01"
            #         # else:
            #         timest = str(int(treat_ids.times) + 1).zfill(2)
            #         treatment_not = str(int(treat_ids.times) + 1).zfill(2)
                
            #         ftreatment_code = ct.treatment_parentcode+"-"+timest

            #         ct.status="Done"
            #         ct.save()
                    
            #         edone_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('pk').count()
            #         if ct.treatment_limit_times == 0:
            #             if ct.treatment_limit_times > edone_ids or ct.treatment_limit_times == 0:
            #                 ftreatids = Treatment(treatment_code=ftreatment_code,course=frtstreat_ids.course,times=timest,
            #                 treatment_no=treatment_not,price=ct.price,treatment_date=pay_date,
            #                 next_appt=ct.next_appt,cust_name=ct.cust_name,Cust_Codeid=ct.Cust_Codeid,
            #                 cust_code=ct.cust_code,status="Open",unit_amount=0,
            #                 Item_Codeid=ct.Item_Codeid,item_code=ct.item_code,treatment_parentcode=ct.treatment_parentcode,
            #                 prescription=ct.prescription,allergy=ct.allergy,sa_transacno=ct.sa_transacno,
            #                 sa_status=ct.sa_status,record_status=ct.record_status,appt_time=ct.appt_time,
            #                 remarks=ct.remarks,duration=ct.duration,hold_item=ct.hold_item,transaction_time=ct.transaction_time,
            #                 dt_lineno=ct.dt_lineno,expiry=ct.expiry,lpackage=ct.lpackage,package_code=ct.package_code,
            #                 Site_Codeid=ct.Site_Codeid,site_code=ct.site_code,type=ct.type,treatment_limit_times=ct.treatment_limit_times,
            #                 treatment_count_done=ct.treatment_count_done,treatment_history_last_modify=ct.treatment_history_last_modify,
            #                 service_itembarcode=ct.service_itembarcode,isfoc=ct.isfoc,Trmt_Room_Codeid=ct.Trmt_Room_Codeid,
            #                 trmt_room_code=ct.trmt_room_code,trmt_is_auto_proportion=ct.trmt_is_auto_proportion,
            #                 smsout=ct.smsout,emailout=ct.emailout,treatment_account=ct.treatment_account).save()

            #         # if c.multi_treat.all()[0].type == 'FFi' and acc_ids.balance == 0:
            #         #     amount = 0
            #         #     Balance = 0

            #         # dtitemdesc_n = str(timest)+"/"+str(treatment_not)+" "+str(c.itemcodeid.item_name)

            #         # treatacc_ids = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
            #         # description=dtitemdesc_n,ref_no=ftreatment_code,type="Sales",
            #         # amount=amount,balance="{:.2f}".format(float(Balance)),User_Nameid=fmspw,
            #         # user_name=fmspw.pw_userlogin,ref_transacno=c.treatment.sa_transacno if c.treatment.sa_transacno else None,sa_transacno=sa_transacno,
            #         # qty=c.quantity if c.quantity else None,outstanding="{:.2f}".format(float(acc_ids.outstanding)) if acc_ids and acc_ids.outstanding is not None and acc_ids.outstanding > 0 else 0.0,deposit=0,
            #         # treatment_parentcode=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else '',treatment_code="",sa_status="SA",
            #         # cas_name=fmspw.pw_userlogin,sa_staffno=service_staff.emp_code if service_staff.emp_code else '',
            #         # sa_staffname=service_staff.display_name if service_staff.display_name else '',dt_lineno=c.lineno,
            #         # Site_Codeid=site,site_code=site.itemsite_code,treat_code=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else None,itemcart=c,
            #         # focreason=item_remarks)
            #         # treatacc_ids.save() 

                    
            #         ct.price = 0
            #         ct.save() 
            #         for ct in c.multi_treat.all():
            #             Treatment.objects.filter(pk=ct.pk).update(treatment_date=pay_date,
            #             record_status='PENDING',price=0,status="Done",
            #             transaction_time=timezone.now(),treatment_count_done=1)

            totaldisc = c.discount_amt + c.additional_discountamt
            totalpercent = c.discount + c.additional_discount

            # if c.discount_amt != 0.0 and c.additional_discountamt != 0.0:
            #     totaldisc = c.discount_amt + c.additional_discountamt
            #     totalpercent = c.discount + c.additional_discount
            #     istransdisc = True
            # elif c.discount_amt != 0.0:
            #     totaldisc = c.discount_amt
            #     totalpercent = c.discount
            #     istransdisc = False
            # elif c.additional_discountamt != 0.0:
            #     totaldisc = c.additional_discountamt
            #     totalpercent = c.additional_discount
            #     istransdisc = True    
            # else:
            #     totaldisc = 0.0
            #     totalpercent = 0.0
            #     istransdisc = False

            #PosDisc Creation for each cart line with or without line disc (disc per/amt = line disc + trasac disc)
            # if transc disc for whole cart is applied that time need to create one record in PosDisc (disc per/amt = trasac disc).
            # discreason = None
            # if c.pos_disc.all().exists():
            #     # for d in c.disc_reason.all():
            #     #     if d.r_code == '100006' and d.r_desc == 'Others':
            #     #         discreason = c.discreason_txt
            #     #     elif d.r_desc:
            #     #         discreason = d.r_desc  
                        
            #     for po in c.pos_disc.all():
            #         po.sa_transacno = sa_transacno
            #         po.dt_status = "SA"
            #         po.dt_price = c.price
            #         po.save()
            # else:
            #     if totaldisc == 0.0 or totalpercent == 0.0 and len(c.pos_disc.all()) == 0:
            #         posdisc = PosDisc(sa_transacno=sa_transacno,dt_itemno=c.itemcodeid.item_code+"0000",disc_amt=totaldisc,
            #         disc_percent=totalpercent,dt_lineno=c.lineno,remark=discreason,site_code=site.itemsite_code,
            #         dt_status="SA",dt_auto=0,line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=c.price,istransdisc=False)
            #         posdisc.save()
            #         # print(posdisc.pk,"posdisc")

                
            #HoldItemDetail creation for retail products
            # if c.itemcodeid.Item_Divid.itm_code == 1 and c.itemcodeid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.itm_isactive == True:
            #     con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #     if not con_obj:
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
            #         return Response(result, status=status.HTTP_400_BAD_REQUEST) 


            #     product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                
            #     hold = HoldItemDetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
            #     transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
            #     hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #     hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=c.trans_amt,hi_qty=c.holditemqty,
            #     hi_discamt=totaldisc,hi_discpercent=totalpercent,hi_discdesc=None,
            #     hi_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
            #     hi_lineno=c.lineno,hi_uom=c.item_uom.uom_desc,hold_item=True,hi_deposit=c.deposit,
            #     holditemqty=c.holditemqty,status="OPEN",sa_custno=cust_obj.cust_code,
            #     sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
            #     product_issues_no=product_issues_no)
            #     hold.save()
            #     # print(hold.pk,"hold")
            #     if hold.pk:
            #         con_obj.control_no = int(con_obj.control_no) + 1
            #         con_obj.save()

            # if '0' in str(c.quantity):
            #     no = str(c.quantity).split('0')
            #     if no[0] == '':
            #         number = no[1]
            #     else:
            #         number = c.quantity
            # else:
            #     number = c.quantity

            # dtl_st_ref_treatmentcode = "";dtl_first_trmt_done = False
            # for i in range(1,int(number)+1):
            #     treat = c
            #     Price = c.trans_amt
            #     Unit_Amount = Price / c.quantity
            #     times = str(i).zfill(2)
            #     treatment_no = str(c.quantity).zfill(2)
            #     treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
            #     treatment_parentcode=treatment_parentcode,course=treat.itemcodeid.item_desc,times=times,
            #     treatment_no=treatment_no,price=Price,unit_amount=Unit_Amount,Cust_Codeid=treat.cust_noid,
            #     cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
            #     status="Open",item_code=treat.itemcodeid.item_code,Item_Codeid=treat.itemcodeid,
            #     sa_transacno=sa_transacno,sa_status="SA",type="N",
            #     dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,
            #     treatment_account=treatacc)

                #and str(treatmentid.treatment_code) == str(treatment_parentcode)+"-"+"01"

            # apt_lst = []   
            for cl in c.multi_treat.all():  
                if c.exchange_id:
                    if c.is_foc == True:
                        course_val = c.itemcodeid.item_name +" "+"(FOC)"
                    else:
                        course_val = c.itemcodeid.item_name 
                    cl.course = course_val
                    cl.save()

                if cl.helper_ids.exists():

                    link_flag = False
                    if len(cl.helper_ids.all()) > 1:
                        link_flag = True

                    for h in cl.helper_ids.all():
                        
                        # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                        
                        # treatmentid.status = "Done"
                        # wp1 = h.workcommpoints / float(c.treatment.helper_ids.all().count())
                        wp1 = h.wp1
                        share_amt = float(cl.unit_amount) / float(cl.helper_ids.all().count())
                        if h.work_amt and h.work_amt > 0:
                            share_amt =  h.work_amt


                        TmpItemHelper.objects.filter(id=h.id).update(item_code=cl.treatment_code,
                        item_name=cl.course,line_no=dtl.dt_lineno,sa_transacno=sa_transacno,
                        amount=cl.unit_amount,sa_date=pay_date,site_code=site.itemsite_code,
                        wp1=wp1,wp2=0.0,wp3=0.0)

                        # Item helper create
                        helper = ItemHelper(item_code=cl.treatment_code,item_name=cl.course,
                        line_no=dtl.dt_lineno,sa_transacno=c.treatment.sa_transacno,amount=cl.unit_amount,
                        helper_name=h.helper_name,helper_code=h.helper_code,sa_date=dtl.sa_date,
                        site_code=site.itemsite_code,share_amt="{:.2f}".format(float(share_amt)),helper_transacno=sa_transacno,
                        wp1=wp1,wp2=0.0,wp3=0.0,percent=h.percent,work_amt="{:.2f}".format(float(h.work_amt)) if h.work_amt else h.work_amt,times=h.times,treatment_no=h.treatment_no)
                        helper.save()
                        ItemHelper.objects.filter(id=helper.id).update(sa_date=pay_date)
                        # print(helper.id,"helper")

                        #appointment treatment creation
                        # if h.appt_fr_time and h.appt_to_time != False and h.add_duration != False:

                        #     custprev_appts = Appointment.objects.filter(appt_date=date.today(),
                        #     cust_no=cust_obj.cust_code).order_by('-pk').exclude(itemsite_code=site.itemsite_code)
                                
                        #     custprevtime_appts = Appointment.objects.filter(appt_date=date.today(),
                        #     cust_no=cust_obj.cust_code).filter(Q(appt_to_time__gte=h.appt_fr_time) & Q(appt_fr_time__lte=h.appt_to_time)).order_by('-pk')
                            

                        #     #staff having shift/appointment on other branch for the same time
                            
                        #     check_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=h.helper_id.emp_code,
                        #     ).filter(Q(appt_to_time__gt=h.appt_fr_time) & Q(appt_fr_time__lt=h.appt_to_time))
                        #     # print(check_ids,"check_ids")

                        #     if not custprev_appts and not custprevtime_appts and not check_ids:
                                        
                        #         stock_obj = c.itemcodeid
                        #         stk_duration = 60 
                        #         if stock_obj.srv_duration is None or float(stock_obj.srv_duration) == 0.0:
                        #             stk_duration = 60
                        #         else:
                        #             stk_duration = int(stock_obj.srv_duration)

                        #         stkduration = int(stk_duration) + 30
                        #         # print(stkduration,"stkduration")

                        #         hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                        #         start_time =  get_in_val(self, h.appt_fr_time)
                        #         starttime = datetime.datetime.strptime(start_time, "%H:%M")

                        #         end_time = starttime + datetime.timedelta(minutes = stkduration)
                        #         endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                        #         duration = hrs

                        #         # treat_all = Treatment.objects.filter(sa_transacno=c.treatment.sa_transacno,
                        #         # treatment_parentcode=c.treatment.treatment_parentcode,site_code=site.itemsite_code)
                        #         treat_all = Treatment.objects.filter(sa_transacno=c.treatment.sa_transacno,
                        #         treatment_parentcode=c.treatment.treatment_parentcode)
                        #         length = [t.status for t in treat_all if t.status == 'Done']
                        #         if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
                        #             master_status = "Done"
                        #         else:
                        #             master_status = "Open"

                        #         master = Treatment_Master(treatment_code=c.treatment.treatment_code,
                        #         treatment_parentcode=c.treatment.treatment_parentcode,sa_transacno=c.treatment.sa_transacno,
                        #         course=stock_obj.item_desc,times=h.times,treatment_no=h.treatment_no,
                        #         price="{:.2f}".format(float(c.treatment.unit_amount)) if c.treatment.unit_amount else 0.0,cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,
                        #         cust_name=cust_obj.cust_name,status=master_status,unit_amount="{:.2f}".format(float(c.treatment.unit_amount)) if c.treatment.unit_amount else 0.0,
                        #         Item_Codeid=stock_obj,item_code=stock_obj.item_code,
                        #         sa_status="SA",dt_lineno=dtl.dt_lineno,type="N",duration=stkduration,
                        #         Site_Codeid=site,site_code=site.itemsite_code,
                        #         trmt_room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,Trmt_Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,
                        #         Item_Class=stock_obj.Item_Classid if stock_obj.Item_Classid else None,PIC=stock_obj.Stock_PIC if stock_obj.Stock_PIC else None,
                        #         start_time=h.appt_fr_time if h.appt_fr_time else None,end_time=h.appt_to_time if h.appt_to_time else None,add_duration=h.add_duration if h.add_duration else None,
                        #         appt_remark=stock_obj.item_desc if stock_obj.item_desc else None,requesttherapist=False)
                        #         master.save()
                        #         master.treatment_date = pay_date
                        #         master.save()
                        #         master.emp_no.add(h.helper_id.pk)
                        #         # print(master.id,"master")

                        #         ctrl_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=fmspw.loginsite.pk).first()
                        #         # if not ctrl_obj:
                        #         #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
                        #         #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                
                        #         appt_code = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                                
                        #         if apt_lst == []:
                        #             linkcode = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                        #         else:
                        #             app_obj = Appointment.objects.filter(pk=apt_lst[0]).order_by('pk').first()
                        #             linkcode = app_obj.linkcode

                        #         channel = ApptType.objects.filter(appt_type_code="10003",appt_type_isactive=True).first()
                        #         # if not channel:
                        #         #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
                        #         #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                
                        #         #no need to add checktype & treat_parentcode for TD / service done appts   

                        #         appt = Appointment(cust_noid=cust_obj,cust_no=cust_obj.cust_code,appt_date=pay_date,
                        #         appt_fr_time=h.appt_fr_time if h.appt_fr_time else None,Appt_typeid=channel if channel else None,appt_type=channel.appt_type_desc if channel.appt_type_desc else None,
                        #         appt_phone=cust_obj.cust_phone2 if cust_obj.cust_phone2 else None,appt_remark=stock_obj.item_desc if stock_obj.item_desc else None,
                        #         emp_noid=h.helper_id if h.helper_id else None,emp_no=h.helper_id.emp_code if h.helper_id.emp_code else None,emp_name=h.helper_id.display_name if h.helper_id.display_name else None,
                        #         cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
                        #         appt_to_time=h.appt_to_time if h.appt_to_time else None,Appt_Created_Byid=fmspw,
                        #         appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                        #         Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,
                        #         Source_Codeid=h.Source_Codeid if h.Source_Codeid else None,source_code=h.Source_Codeid.source_code if h.Source_Codeid else None,
                        #         cust_refer=cust_obj.cust_refer if cust_obj.cust_refer else None,requesttherapist=False,new_remark=h.new_remark if h.new_remark else None,
                        #         item_code=stock_obj.item_code if stock_obj.item_code else None,sa_transacno=c.treatment.sa_transacno,treatmentcode=c.treatment.treatment_code,
                        #         linkcode=linkcode,link_flag=link_flag,add_duration=h.add_duration if h.add_duration else None,
                        #         Item_Codeid=stock_obj)
                        #         appt.save()
                        #         # print(appt,"appt")

                        #         if appt.pk:
                        #             apt_lst.append(appt.pk)
                        #             master.Appointment = appt
                        #             master.appt_time = timezone.now()
                        #             master.save()
                        #             ctrl_obj.control_no = int(ctrl_obj.control_no) + 1
                        #             ctrl_obj.save()
                                
                        #treatment Account creation for done treatment 01
                        # if c.helper_ids.all().filter(times=times).first():
                        #     acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,treatment_parentcode=treatment_parentcode).order_by('id').last()
                        #     td_desc = str(stock_obj.item_desc)
                        #     balance = acc_ids.balance - treatmentid.unit_amount if acc_ids.balance else treatmentid.unit_amount

                        #     treatacc_td = TreatmentAccount(Cust_Codeid=cust_obj,
                        #     cust_code=cust_obj.cust_code,ref_no=treatmentid.treatment_code,
                        #     description=td_desc,type='Sales',amount=-treatmentid.unit_amount,balance=balance,
                        #     User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=treatmentid.sa_transacno,
                        #     sa_transacno=sa_transacno,qty=1,outstanding=treatacc.outstanding,deposit=0.0,
                        #     treatment_parentcode=treatmentid.treatment_parentcode,treatment_code="",
                        #     sa_status="SA",cas_name=fmspw.pw_userlogin,
                        #     sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                        #     sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                        #     dt_lineno=c.lineno,Site_Codeid=site,site_code=site.itemsite_code,
                        #     treat_code=treatmentid.treatment_parentcode,itemcart=c)
                        #     treatacc_td.save()
                        #     # print(treatacc_td.id,"treatacc_td")
                        #     dtl_first_trmt_done = True
                        #     if dtl_st_ref_treatmentcode == "":
                        #         dtl_st_ref_treatmentcode = str(treatment_parentcode)+"-"+str(times)
                        #     elif not dtl_st_ref_treatmentcode == "":
                        #         dtl_st_ref_treatmentcode = str(dtl_st_ref_treatmentcode) +"-"+str(times)


                    # treatmentid.save()
                    # appt_time=treat.appt_time,Trmt_Room_Codeid=treat.Trmt_Room_Codeid,trmt_room_code=treat.trmt_room_code,
                    # print(treatmentid.id,"treatment_id")


                #auto Treatment Usage transactions
                now = datetime.datetime.now()
                s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))
                usagelevel_ids = Usagelevel.objects.filter(service_code=cl.service_itembarcode,
                isactive=True).order_by('-pk') 
                valuedata = 'TRUE'

                sys_ids = Systemsetup.objects.filter(title='Stock Available',value_name='Stock Available').first() 
                if sys_ids:
                    valuedata = sys_ids.value_data

                       

                currenttime = timezone.now()
                currentdate = timezone.now().date()
                     
                for i in usagelevel_ids: 
                    TreatmentUsage(treatment_code=cl.treatment_code,item_code=i.item_code,
                    item_desc=i.item_desc,qty=i.qty,uom=i.uom,site_code=site.itemsite_code,usage_status="Usage",
                    line_no=1,usage_update=s1,sa_transacno=sa_transacno).save()
                    if int(i.qty) > 0:
                        qtytodeduct = int(i.qty)
                        batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=i.item_code[:-4],
                        uom=i.uom).order_by('pk').last() 

                        obatchids = ItemBatch.objects.none()

                        uom_ids = ItemUomprice.objects.filter(item_code=i.item_code[:-4],item_uom2=i.uom
                        ,uom_unit__gt=0,isactive=True).first()
                        # print(uom_ids,"uom_ids")
                        if uom_ids:
                            obatchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(i.item_code[:-4]),
                            uom=uom_ids.item_uom).order_by('pk').last() 

                        stockreduce = False
                        if valuedata == 'TRUE':
                            if (batchids and int(batchids.qty) >= int(i.qty)) or (obatchids and int(obatchids.qty) >= int(qtytodeduct)):
                                stockreduce = True
                        else:
                            stockreduce = True

                        if stockreduce == True: 
                            #ItemBatch
                            if batchids and int(batchids.qty) >= int(qtytodeduct):
                                deduct = batchids.qty - qtytodeduct
                                batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())

                                
                                post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                item_uom=i.uom).order_by('pk').last() 


                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=cl.treatment_code,trn_date=currentdate,
                                trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                trn_amt=None,trn_post=currentdate,
                                trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None)
                                stktrn_id.save()
                                Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                            
                            else:
                                flag = False

                                adcontrolobj = ControlNo.objects.filter(control_description__iexact="ADJS",
                                site_code=fmspw.loginsite.itemsite_code).first()

                                adjno = False
                                if adcontrolobj:
                                    adjno = "W"+str(adcontrolobj.control_prefix)+str(adcontrolobj.site_code)+str(adcontrolobj.control_no)


                                if batchids and obatchids and int(obatchids.qty) >= int(qtytodeduct):

                                    post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                    stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                    item_uom=uom_ids.item_uom).order_by('pk').last() 


                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno if adjno else cl.treatment_code,trn_date=currentdate,
                                    trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=-1,trn_balqty=obatchids.qty-1,
                                    trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                    trn_amt=None,trn_post=currentdate,
                                    trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                    hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                    line_no=c.lineno,item_uom=uom_ids.item_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                    stock_in=None,trans_package_line_no=None)
                                    stktrn_id.save()
                                    Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                                    

                                    stktrnids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                    item_uom=i.uom).order_by('pk').last() 


                                    stktrnid = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=adjno,trn_date=currentdate,
                                    trn_type="ADJS",trn_db_qty=None,trn_cr_qty=None,trn_qty=uom_ids.uom_unit,trn_balqty=uom_ids.uom_unit,
                                    trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                    trn_amt=None,trn_post=currentdate,
                                    trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                    hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                    line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                    stock_in=None,trans_package_line_no=None)
                                    stktrnid.save()
                                    Stktrn.objects.filter(pk=stktrnid.pk).update(trn_post=pay_date,trn_date=pay_date)
                                

                                    fbatch_qty = (batchids.qty + uom_ids.uom_unit) - qtytodeduct

                                    vstk = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=cl.treatment_code,trn_date=currentdate,
                                    trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=fbatch_qty,
                                    trn_balcst=stktrnids.trn_balcst if stktrnids and stktrnids.trn_balcst else 0,
                                    trn_amt=None,trn_post=currentdate,
                                    trn_cost=stktrnids.trn_cost if stktrnids and stktrnids.trn_cost else 0,trn_ref=None,
                                    hq_update=stktrnids.hq_update if stktrnids and stktrnids.hq_update else 0,
                                    line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                    stock_in=None,trans_package_line_no=None)
                                    vstk.save()
                                    Stktrn.objects.filter(pk=vstk.pk).update(trn_post=pay_date,trn_date=pay_date)
                                


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
                                        batch_id = ItemBatch(item_code=i.item_code[:-4],site_code=site.itemsite_code,
                                        batch_no="",uom=i.uom,qty=-qtytodeduct,exp_date=None,batch_cost=None).save()
                                        deduct = -qtytodeduct

                                    #Stktrn
                                    currenttime = timezone.now()
                                    currentdate = timezone.now().date()
                            
                                    post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                    stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(i.item_code[:-4])+"0000",
                                    item_uom=i.uom).order_by('pk').last() 

                                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(i.item_code[:-4])+"0000",
                                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=cl.treatment_code,trn_date=currentdate,
                                    trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                    trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                    trn_amt=None,trn_post=currentdate,
                                    trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                    hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                    line_no=c.lineno,item_uom=i.uom,item_batch=None,mov_type=None,item_batch_cost=None,
                                    stock_in=None,trans_package_line_no=None)
                                    stktrn_id.save()
                                    Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                            
            if c.exchange_id:
                exc_ids = ExchangeDtl.objects.filter(exchange_no=c.exchange_id.exchange_no,
                status=False).update(status=True,fe_transacno=sa_transacno)

                # c.exchange_id.status = True
                # c.exchange_id.fe_transacno = sa_transacno
                # c.exchange_id.save()
                # ExchangeDtl.objects.filter(status=False).delete()
                PackageAuditingLog(treatment_parentcode=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else '',
                user_loginid=fmspw,package_type="Exchange",pa_qty=c.quantity if c.quantity else None).save()    

            for clp in c.multi_treat.all():
                if clp.type == "FFi":   
                    TmpItemHelper.objects.filter(treatment=clp).delete()
             
            # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
            # dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
            # dtl.first_trmt_done = dtl_first_trmt_done
            # dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
            # dtl.first_trmt_done_staff_name = ','.join([v.helper_id.display_name for v in c.helper_ids.all() if v.helper_id.display_name])
            # dtl.save()

            searcids = TreatmentPackage.objects.filter(treatment_parentcode=ct.treatment_parentcode).first()
            if searcids:
                stptdone_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Done").order_by('pk').count()
                stptcancel_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Cancel").order_by('pk').count()
                stptopen_ids = Treatment.objects.filter(treatment_parentcode=ct.treatment_parentcode,status="Open").order_by('pk').count()
                trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=ct.treatment_parentcode).order_by('-sa_date','-sa_time','-id').first()
                treatmids = list(set(Treatment.objects.filter(
                treatment_parentcode=ct.treatment_parentcode).filter(~Q(status="Open")).only('pk').order_by('pk').values_list('pk', flat=True).distinct()))

                Treatmentids.objects.filter(treatment_int__in=treatmids).delete()  
                
                searcids.open_session = stptopen_ids
                searcids.done_session = stptdone_ids
                searcids.cancel_session = stptcancel_ids
                
                searcids.balance = "{:.2f}".format(float(trmtAccObj.balance)) 
                searcids.outstanding = "{:.2f}".format(float(trmtAccObj.outstanding))
                # searcids.treatmentids = treatmids
                searcids.save()
                dtl.dt_itemdesc = dtl.dt_itemdesc+" "+"Bal : "+str(stptopen_ids)
                dtl.save()

                p_ids = list(set(Treatmentids.objects.filter(treatment_parentcode=ct.treatment_parentcode).values_list('treatment_int', flat=True).distinct()))
                op_ids = list(Treatment.objects.filter(
                treatment_parentcode=ct.treatment_parentcode).filter(Q(status="Open"),~Q(pk__in=p_ids)).only('pk').order_by('pk').values_list('pk', flat=True).distinct())
                if op_ids:
                    for j in op_ids:
                        stf_ids = Treatmentids.objects.filter(treatment_int=j)
                        if not stf_ids: 
                            Treatmentids(treatment_parentcode=ct.treatment_parentcode,
                                        treatment_int=j).save()

            
            searchhids = TmpTreatmentSession.objects.filter(treatment_parentcode=ct.treatment_parentcode,
            created_at=date.today()) 
            if searchhids:
                searchhids.delete()
           



        return id_lst    
    # except Exception as e:
    #     invalid_message = str(e)
    #     return general_error_response(invalid_message)
    

def invoice_exchange(self, request, exchange_ids, sa_transacno, cust_obj, outstanding, pay_date, pay_time):
    if self:
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        id_lst = [] 
        gst = GstSetting.objects.filter(isactive=True,activefromdate__date__lte=pay_date,
        activetodate__date__gte=pay_date).first()

        
        calcgst = 0
        if gst:
            calcgst = gst.item_value if gst and gst.item_value else 0.0
        if calcgst > 0:
            sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
            if sitegst:
                if sitegst.site_is_gst == False:
                    calcgst = 0
        # print(calcgst,"0 calcgst")
        # Yoonus Tax Chcking
      
        for idx, c in enumerate(exchange_ids, start=1):
            
            sales_staff = c.sales_staff.all().first()
            salesstaff = c.sales_staff.all()

            gst_amt_collect = 0
            if calcgst > 0:
                if site and site.is_exclusive == True:
                    gst_amt_collect = c.deposit * (calcgst/ 100)
                else:
                    gst_amt_collect = c.deposit * calcgst / (100+calcgst)
                
            
            sales = "";service = ""
            if c.sales_staff.all():
                for i in c.sales_staff.all():
                    if sales == "":
                        sales = sales + i.display_name
                    elif not sales == "":
                        sales = sales +","+ i.display_name
            if c.service_staff.all(): 
                for s in c.service_staff.all():
                    if service == "":
                        service = service + s.display_name
                    elif not service == "":
                        service = service +","+ s.display_name 


            dtl = PosDaud(sa_transacno=sa_transacno,dt_status="EX",dt_itemnoid=c.itemcodeid,
            dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=c.itemcodeid.item_name,dt_price=c.price,
            dt_promoprice="{:.2f}".format(float(c.discount_price)),
            dt_amt=-float("{:.2f}".format(float(c.trans_amt))),dt_qty=c.quantity,
            dt_discamt=0,dt_discpercent=0,dt_Staffnoid=sales_staff,dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            dt_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
            dt_discuser=None,dt_combocode=c.itemcodeid.item_code,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
            dt_transacamt="{:.2f}".format(float(c.trans_amt)),dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,itemcart=c,
            st_ref_treatmentcode=None,record_detail_type="PRODUCT",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
            topup_outstanding=0,dt_remark=sa_transacno,isfoc=0,item_remarks="",
            dt_uom=c.item_uom.uom_code if c.item_uom else None,first_trmt_done=False,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
            staffs=sales +" "+"/"+" "+ service)
            dtl.save()
            dtl.sa_date = pay_date 
            dtl.sa_time = pay_time
            dtl.save()
            # print(dtl.id,"dtl")

            if dtl.pk not in id_lst:
                id_lst.append(c.pk)

            #multi staff table creation
            ratio = 0.0
            if c.sales_staff.all().count() > 0:
                count = c.sales_staff.all().count()
                ratio = float(c.ratio) / float(count)

            # for sale in c.sales_staff.all():
            #     multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
            #     emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
            #     dt_lineno=c.lineno)
            #     multi.save()
                # print(multi.id,"multi")

            for sale in c.multistaff_ids.all():
                multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
                emp_code=sale.emp_code,ratio=sale.ratio,salesamt="{:.2f}".format(float(sale.salesamt)),type=None,isdelete=False,role=1,
                dt_lineno=c.lineno,salescommpoints=sale.salescommpoints)
                multi.save()  
                sale.sa_transacno = sa_transacno 
                sale.save()  

            if int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
                desc = "Total Product Amount : "+str("{:.2f}".format(float(c.trans_amt)))
                #Deposit Account creation
                
                decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                # if not decontrolobj:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)
                
                if c.is_foc == True:
                    item_descriptionval = c.itemcodeid.item_name+" "+"(FOC)"
                else:
                    item_descriptionval = c.itemcodeid.item_name
                

                depoacc = DepositAccount(cust_code=cust_obj.cust_code,type="Exchange",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(c.deposit)),user_name=fmspw.pw_userlogin,qty=c.quantity,outstanding=0,
                deposit="{:.2f}".format(float(c.deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.display_name for v in salesstaff if v.display_name]),
                deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
                sa_status="EX",item_barcode=str(c.itemcodeid.item_code)+"0000",item_description=item_descriptionval,
                treat_code=treat_code,void_link=None,lpackage=None,package_code=None,
                dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
                ref_transacno=sa_transacno,ref_productcode=treat_code,Item_Codeid=c.itemcodeid,
                item_code=c.itemcodeid.item_code)
                depoacc.save()
                depoacc.sa_date = pay_date
                depoacc.sa_time = pay_time
                depoacc.save()
                # print(depoacc.pk,"depoacc")
                if depoacc.pk:
                    decontrolobj.control_no = int(decontrolobj.control_no) + 1
                    decontrolobj.save()

                #ItemBatch
                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                item_code=c.itemcodeid.item_code,uom=c.item_uom.uom_code).order_by('pk').last()
                
                if batch_ids:
                    addamt = batch_ids.qty + abs(c.quantity)
                    batch_ids.qty = addamt
                    batch_ids.updated_at = timezone.now()
                    batch_ids.save() 
                else:
                    batch_id = ItemBatch(item_code=c.itemcodeid.item_code,site_code=site.itemsite_code,
                    batch_no="",uom=c.item_uom.uom_code,qty=abs(c.quantity),exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                    addamt = abs(c.quantity)                      

                #Stktrn
                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                itemcode=c.itemcodeid.item_code+"0000",item_uom=c.item_uom.uom_code).last() 
                # print(stktrn_ids,"stktrn_ids")

                currenttime = timezone.now()
                currentdate = timezone.now().date()

                post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                itemuom_ids = ItemUomprice.objects.filter(item_code=c.itemcodeid.item_code,item_uom=c.item_uom.uom_code,isactive=True).order_by('pk').first()

                if stktrn_ids:
                    amt_add = stktrn_ids.trn_balqty + abs(c.quantity)

                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                    itemcode=str(c.itemcodeid.item_code)+"0000",store_no=site.itemsite_code,
                    tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                    trn_type="EX",trn_db_qty=None,trn_cr_qty=None,
                    trn_qty=abs(c.quantity),trn_balqty=amt_add,trn_balcst=0,
                    trn_amt="{:.2f}".format(float(abs(c.deposit))),
                    trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                    hq_update=0,line_no=c.lineno,item_uom=c.item_uom.uom_code,
                    item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None,trn_post=currentdate,
                    trn_date=currentdate)
                    stktrn_id.save()
                    Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                   
                else:
                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                    itemcode=str(c.itemcodeid.item_code)+"0000",store_no=site.itemsite_code,
                    tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                    trn_type="EX",trn_db_qty=None,trn_cr_qty=None,
                    trn_qty=abs(c.quantity),trn_balqty=addamt,trn_balcst=0,
                    trn_amt="{:.2f}".format(float(abs(c.deposit))),
                    trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                    hq_update=0,line_no=c.lineno,item_uom=c.item_uom.uom_code,
                    item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None,trn_post=currentdate,
                    trn_date=currentdate)
                    stktrn_id.save()
                    Stktrn.objects.filter(pk=stktrn_id.pk).update(trn_post=pay_date,trn_date=pay_date)
                   
                
        return id_lst


        
