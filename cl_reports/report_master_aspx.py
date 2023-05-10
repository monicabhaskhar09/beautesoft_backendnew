#Collection By Outlet

#Paytable Api
GET http://sequoiasg.ddns.net:7022/WebReportAPI_Train/api/PaymentGroup?siteCode=NIL
output
{
    "status": 200,
    "message": "Listed Succesfully",
    "error": false,
    "data": [
        {
            "code": "ALIPAY",
            "name": "ALIPAY"
        },

    ]
}

# SQL 
select Distinct pay_code [Code],pay_description [Name]  from PAYTABLE where pay_isactive=1 Order By pay_description

#SiteListing  Api based on login employee
GET http://sequoiasg.ddns.net:7022/WebReportAPI_Train/api/siteListing?empCode=100001
output
{
    "status": 200,
    "message": "Listed Succesfully",
    "error": false,
    "data": [
        {
            "itemcode": "JY01",
            "itemdesc": "BSB"
        },
        {
            "itemcode": "JYHQ",
            "itemdesc": "HQ"
        },
        {
            "itemcode": "JY02",
            "itemdesc": "JPB"
        }
    ]
}

# SQL
select TOP(100) itemSite_Code as itemCode, itemSite_desc as itemDesc from item_SiteList where ItemSite_isactive = 1 and itemsite_code in (select Site_Code from emp_SiteList where emp_code='" + empCode + "' and isactive=1) order by itemDesc

# Report Title api
POST http://sequoiasg.ddns.net:7022/WebReportAPI_Train/api/webBI_ReportTittle
payload
{
	"fromDate":"01/03/2023",
	"toDate":"30/03/2023",
	"ReportTitle":"Collection By Outlet",
	"userCode":"",  
    "siteText":"",  
	"siteCode2":"JY01"
}
output

{
    "success": "1",
    "error": "No Error Found",
    "result": [
        {
            "fromDate": "01/03/2023",
            "toDate": "30/03/2023",
            "reportTitle": "Collection By Outlet",
            "fromsite": null,
            "tosite": null,
            "ShowZeroQty": null,
            "companytitle": "Welcome to Jean Yip",
            "companyHeader1": "Jean Yip",
            "companyHeader2": "Bishan",
            "companyHeader3": "Singapore",
            "companyHeader4": "Tel: 6",
            "companyFooter1": "",
            "companyFooter2": "THANK YOU!",
            "companyFooter3": "",
            "companyFooter4": "",
            "ReportUrl": null,
            "binaryValue": null,
            "binaryValueByte": 0,
            "binaryValueInt": 0,
            "userCode": "",
            "siteText": "",
            "returnText": null
        }
    ]
}
# SQL
select TOP 1 product_license,ID,Title,Comp_Title1,Comp_Title2,Comp_Title3,Comp_Title4,Footer_1,Footer_2,Footer_3,Footer_4 from Title 
where 
--product_license=@siteCode
product_license in (Select Item From dbo.LISTTABLE(@siteCode,','))
order by ID

# LISTTABLE
CREATE FUNCTION [dbo].LISTTABLE ( @StringInput VARCHAR(8000), @Delimiter nvarchar(1))
RETURNS @OutputTable TABLE ( Item VARCHAR(100) )
AS
BEGIN

    DECLARE @String    VARCHAR(100)

    WHILE LEN(@StringInput) > 0
    BEGIN
        SET @String      = LEFT(@StringInput, 
                                ISNULL(NULLIF(CHARINDEX(@Delimiter, @StringInput) - 1, -1),
                                LEN(@StringInput)))
        SET @StringInput = SUBSTRING(@StringInput,
                                     ISNULL(NULLIF(CHARINDEX(@Delimiter, @StringInput), 0),
                                     LEN(@StringInput)) + 1, LEN(@StringInput))

        INSERT INTO @OutputTable ( Item )
        VALUES ( @String )
    END

    RETURN
END

ItemSite_ID least need to pass select api

# webBI_SaleCollection collecttion by outlet main api table data

POST http://sequoiasg.ddns.net:7022/WebReportAPI_Train/api/webBI_SaleCollection
payload
{
	"fromDate":"01/03/2023",
	"toDate":"30/03/2023",
	"siteCode":"JY01,JY02,JYHQ",
	"payCode":"",  
    "ReportUrl":"",  
	"reportType":"Detail"
}

output
{
    "success": "1",
    "result": [
        {
            "staffCode": null,
            "staffname": null,
            "payDate": "27/03/2023",
            "customer": "alex",
            "invoiceRef": "INVJY01100888",
            "Date": null,
            "SalesCmtn": 0.0,
            "ServiceCmtn": 0.0,
            "SalesGroup": "Sales",
            "payTypes": "CASH",
            "payTypes1": null,
            "siteCode": "JY01",
            "siteName": "BSB",
            "amt": 372.0,
            "payContra": 0.0,
            "payCN": 0.0,
            "grossAmt": 372.0,
            "taxes": 0.0,
            "gstRate": 0.0,
            "netAmt": 372.0,
            "comm": 0.0,
            "total": 372.0,
            "payRef": "Dhanasekhar",
            "CustRef": "",
            "BankCharges": 0.0,
            "ReportUrl": "",
            "RatioCheck": null,
            "Ratio": 0.0,
            "sharedStaff": null,
            "receivedBy": null,
            "servedBy": null,
            "tpCount": 0.0,
            "tpAmount": 0.0,
            "ProductAmnt": 0.0,
            "TdAmnt": 0.0,
            "PackageAmnt": 0.0,
            "CreditAmnt": 0.0,
            "depositAmnt": 0.0,
            "Outstanding": 0.0,
            "Marketing": null,
            "remark": null,
            "GroupOrder": "Group1",
            "excelSeq": 0.0,
            "Dept": null,
            "Types": null,
            "count": 0
        },
        ],
    "error": "No Error Found"
}

# SQL
# subquery
SELECT   
--pos_haud.sa_date [payDate],    
--CAST (pos_haud.sa_date AS DATE) [payDate],   
convert (varchar,pos_haud.sa_date,103)[payDate],   
Customer.Cust_name [customer],    
pos_haud.SA_TransacNo_Ref [invoiceRef],   
pos_haud.isVoid,  
--pos_haud.sa_transacno [payRef],  
pos_haud.sa_staffname [payRef],  
isnull(Customer.Cust_Refer,'') [CustRef],  
pos_taud.pay_Desc [payTypes],   
pos_taud.pay_actamt  [amt] ,   
0 [payContra],  
paytable.GT_Group [Group],  
Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],  
--pos_taud.PAY_GST [taxes],  
--Below line commanded as per discussion with yoonus on 7.9.2022 for JY
--(case when paytable.GT_Group='GT1' and pos_taud.PAY_GST<>0 then (pos_taud.pay_actamt * 7 / 100) else 0 end ) as [taxes],  
(case when paytable.GT_Group='GT1' and pos_taud.PAY_GST<>0 then round((pos_taud.pay_actamt /107)*7,2) else 0 end ) as [taxes],  
Convert(Decimal(19,0),CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.PAY_GST/(pos_taud.pay_actamt-pos_taud.PAY_GST))*100 End) [gstRate],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST [netAmt],  
0 [comm],  
--isnull(bank_charges,0) [BankCharges],  
round((isnull(bank_charges,0) * ( pos_taud.pay_actamt - pos_taud.PAY_GST) )/100 ,2) as [BankCharges],  
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - isnull(bank_charges,0)+0 [total],  
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - round((isnull(bank_charges,0) * ( pos_taud.pay_actamt - pos_taud.PAY_GST) )/100 ,2) +0 [total],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )- (case when paytable.GT_Group='GT1' and pos_taud.PAY_GST<>0 then round((pos_taud.pay_actamt /107)*7,2) else 0 end ) - round((isnull(bank_charges,0) * ( pos_taud.pay_actamt - pos_taud.PAY_GST)

 )/100 ,2) +0 [total],  
pos_haud.ItemSite_Code,Item_SiteList.ItemSite_Desc  ,isnull(paytable.Excel_Col_Seq,0) as Excel_Col_Seq
FROM pos_haud   
INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno     
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code   
INNER JOIN Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code   
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE and paytable.Pay_isactive=1 
--INNER JOIN pay_group ON pay_group.PAY_GROUP_CODE=paytable.pay_group
--Where pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate --And pos_haud.ItemSite_Code=@Site  
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate --And pos_haud.ItemSite_Code=@Site  
--and pos_haud.SA_TransacNo_Type='Receipt'  
and paytable.pay_code in (select pay_code from paytable where GT_Group='GT1' )  and pos_haud.isVoid!=1  
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
And ((@PayMode='') OR ((@PayMode<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayMode,',')))) --pay


# Mainquery
Select X.payDate,X.customer,X.invoiceRef,[payRef],[CustRef],  
  
--STRING_SPLIT (X.payTypes,',') [payTypes],  
--dbo.SplitStringWithDelim (X.payTypes,',') [payTypes],  
X.payTypes [payTypes],  
(case when X.[isVoid]=1 then 'Voided Sales'  when X.[Group]='GT1' and X.[isVoid]=0 and isnull(SUM(X.total),0)<>0 then 'Sales' when ((X.[Group]='GT2' and X.[isVoid]=0) or (isnull(SUM(X.total),0)=0)) then 'Non-Sales' else '' end) as SalesGroup,  
'Group1' as GroupOrder,X.Excel_Col_Seq [Excel_Col_Seq],
X.ItemSite_Code [siteCode],  
X.ItemSite_Desc [siteName],  
isnull(SUM(X.amt),0) [amt],  
isnull(SUM(X.payCN),0) [payCN],  
isnull(SUM(X.payContra),0) [payContra],  
isnull(SUM(X.grossAmt),0) [grossAmt],  
isnull(MAX(X.taxes),0) [taxes],  
isnull(SUM(X.gstRate),0) [gstRate],  
isnull(SUM(X.netAmt),0) [netAmt],  
isnull(SUM(X.BankCharges),0) [BankCharges],  
isnull(SUM(X.comm),0) [comm],  
isnull(SUM(X.total),0) total    
from (  
SELECT   
--pos_haud.sa_date [payDate],    
--CAST (pos_haud.sa_date AS DATE) [payDate],   
convert (varchar,pos_haud.sa_date,103)[payDate],   
Customer.Cust_name [customer],    
pos_haud.SA_TransacNo_Ref [invoiceRef],   
pos_haud.isVoid,  
--pos_haud.sa_transacno [payRef],  
pos_haud.sa_staffname [payRef],  
isnull(Customer.Cust_Refer,'') [CustRef],  
pos_taud.pay_Desc [payTypes],   
pos_taud.pay_actamt  [amt] ,   
0 [payContra],  
paytable.GT_Group [Group],  
Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],  
--pos_taud.PAY_GST [taxes],  
--Below line commanded as per discussion with yoonus on 7.9.2022 for JY
--(case when paytable.GT_Group='GT1' and pos_taud.PAY_GST<>0 then (pos_taud.pay_actamt * 7 / 100) else 0 end ) as [taxes],  
(case when paytable.GT_Group='GT1' and pos_taud.PAY_GST<>0 then round((pos_taud.pay_actamt /107)*7,2) else 0 end ) as [taxes],  
Convert(Decimal(19,0),CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.PAY_GST/(pos_taud.pay_actamt-pos_taud.PAY_GST))*100 End) [gstRate],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST [netAmt],  
0 [comm],  
--isnull(bank_charges,0) [BankCharges],  
round((isnull(bank_charges,0) * ( pos_taud.pay_actamt - pos_taud.PAY_GST) )/100 ,2) as [BankCharges],  
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - isnull(bank_charges,0)+0 [total],  
--pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST - round((isnull(bank_charges,0) * ( pos_taud.pay_actamt - pos_taud.PAY_GST) )/100 ,2) +0 [total],  
pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )- (case when paytable.GT_Group='GT1' and pos_taud.PAY_GST<>0 then round((pos_taud.pay_actamt /107)*7,2) else 0 end ) - round((isnull(bank_charges,0) * ( pos_taud.pay_actamt - pos_taud.PAY_GST)

 )/100 ,2) +0 [total],  
pos_haud.ItemSite_Code,Item_SiteList.ItemSite_Desc  ,isnull(paytable.Excel_Col_Seq,0) as Excel_Col_Seq
FROM pos_haud   
INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno     
INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code   
INNER JOIN Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code   
INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE and paytable.Pay_isactive=1 
--INNER JOIN pay_group ON pay_group.PAY_GROUP_CODE=paytable.pay_group
--Where pos_haud.sa_date>=@FDate And pos_haud.sa_date<=@TDate --And pos_haud.ItemSite_Code=@Site  
Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=@FDate And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=@TDate --And pos_haud.ItemSite_Code=@Site  
--and pos_haud.SA_TransacNo_Type='Receipt'  
and paytable.pay_code in (select pay_code from paytable where GT_Group='GT1' )  and pos_haud.isVoid!=1  
And ((@Site='') OR ((@Site<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE(@Site,',')))) --Site  
And ((@PayMode='') OR ((@PayMode<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE(@PayMode,',')))) --pay  
)X  
Group By X.payDate,X.customer,X.invoiceRef,X.payTypes,X.ItemSite_Code,X.ItemSite_Desc,[payRef],[CustRef],X.[Group],X.isVoid ,X.Excel_Col_Seq

# api key outputs
# payDate = row["payDate"].ToString();
# customer = row["customer"].ToString();
# invoiceRef = row["invoiceRef"].ToString();
# payTypes = row["payTypes"].ToString();
# SalesGroup = row["SalesGroup"].ToString();
# loginResult.siteCode = row["siteCode"].ToString();
# loginResult.siteName = row["siteName"].ToString();
# loginResult.amt = Convert.ToDecimal(row["amt"].ToString());
# loginResult.payContra = Convert.ToDecimal(row["payContra"].ToString());
# loginResult.payCN = Convert.ToDecimal(row["payCN"].ToString());
# loginResult.grossAmt = Convert.ToDecimal(row["grossAmt"].ToString());                         
# loginResult.taxes = Convert.ToDecimal(row["taxes"].ToString());
# loginResult.gstRate = Convert.ToDecimal(row["gstRate"].ToString());
# loginResult.netAmt = Convert.ToDecimal(row["netAmt"].ToString());
# loginResult.comm = Convert.ToDecimal(row["comm"].ToString());
# loginResult.total = Convert.ToDecimal(row["total"].ToString());
# loginResult.payRef = row["payRef"].ToString();
# loginResult.CustRef = row["CustRef"].ToString();
# loginResult.BankCharges = Convert.ToDecimal(row["BankCharges"].ToString());
# loginResult.ReportUrl = loginInputOut.ReportUrl;
# loginResult.GroupOrder = row["GroupOrder"].ToString();
# loginResult.excelSeq = Convert.ToDouble(row["Excel_Col_Seq"].ToString());

# subquery
# raw_q = "SELECT convert (varchar,pos_haud.sa_date,103)[payDate],   " \
#         "Customer.Cust_name [customer],    " \
#         "pos_haud.SA_TransacNo_Ref [invoiceRef],   " \
#         "pos_haud.isVoid,  " \
#         "pos_haud.sa_staffname [payRef],  " \
#         "isnull(Customer.Cust_Refer,'') [CustRef],  " \
#         "pos_taud.pay_Desc [payTypes],   " \
#         "pos_taud.pay_actamt  [amt] ,   " \
#         "0 [payContra],  " \
#         "paytable.GT_Group [Group],  " \
#         "Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],  " \
#         "pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],  " \
#         "(case when paytable.GT_Group='GT1' and pos_taud.PAY_GST<>0 then round((pos_taud.pay_actamt /107)*7,2) else 0 end ) as [taxes],  "  \
#         "Convert(Decimal(19,0),CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.PAY_GST/(pos_taud.pay_actamt-pos_taud.PAY_GST))*100 End) [gstRate],  " \
#         "pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-pos_taud.PAY_GST [netAmt],  " \
#         "0 [comm],  " \
#         "round((isnull(bank_charges,0) * ( pos_taud.pay_actamt - pos_taud.PAY_GST) )/100 ,2) as [BankCharges],  " \
#         "pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )- (case when paytable.GT_Group='GT1' and pos_taud.PAY_GST<>0 then round((pos_taud.pay_actamt /107)*7,2) else 0 end ) - round((isnull(bank_charges,0) * ( pos_taud.pay_actamt - pos_taud.PAY_GST))/100 ,2) +0 [total], pos_haud.ItemSite_Code,Item_SiteList.ItemSite_Desc  ,isnull(paytable.Excel_Col_Seq,0) as Excel_Col_Seq FROM pos_haud   " \
#         "INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno     " \
#         "INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code   " \
#         "INNER JOIN Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code   " \
#         "INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE and paytable.Pay_isactive=1" \
#         "Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103)>=Convert(Datetime,'01/05/2023',103)" \
#         "And convert(datetime,convert(varchar,pos_haud.sa_date,103),103)<=Convert(Datetime,'04/05/2023',103)" \
#         "and paytable.pay_code in (select pay_code from paytable where GT_Group='GT1' )  and pos_haud.isVoid!=1 And (('JY01,JY02'='') OR (('JY01,JY02'<>'') And pos_haud.ItemSite_Code In (Select Item From dbo.LISTTABLE('JY01,JY02',',')))) --Site " \
#         "And (('CS,'='') OR (('CS,'<>'') And pos_taud.pay_Type In (Select Item From dbo.LISTTABLE('CS,',',')))) --pay" 

 # {'payDate': '05/05/2023', 'customer': 'Yuzuha', 'invoiceRef': 'INVJY01101507',
                #  'payRef': 'Santhosh', 'CustRef': '', 'payTypes': 'CASH', 'SalesGroup': 'Sales',
                #   'GroupOrder': 'Group1', 'Excel_Col_Seq': 0, 'siteCode': 'JY01', 'siteName': 'BSB', 
                #   'amt': 682.0, 'payCN': 0.0, 'payContra': 0, 'grossAmt': 682.0, 'taxes': 0.0,
                #    'gstRate': Decimal('0'), 'netAmt': 682.0, 'BankCharges': 0.0, 'comm': 0, 
                #    'total': 682.0}