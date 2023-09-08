from django import template
register = template.Library()
from cl_table.models import Systemsetup,PackageDtl

@register.simple_tag
def disc_percent_calc(dt_price, dt_discamt, *args, **kwargs):
    # you would need to do any localization of the result here
    res = "{:.2f}".format(float((100 / dt_price) * dt_discamt))
    return res

@register.simple_tag
def get_desc(daud):
    res = daud.dt_itemdesc
    if daud.record_detail_type == "PRODUCT":
        data = daud.dt_itemdesc
        spl = data.split(',')
        # print(spl,"spl")

        pro_expdat_setup = Systemsetup.objects.filter(title='Invoice show PRODUCT Expiry Date',
        value_name='Invoice show PRODUCT Expiry Date',isactive=True).first()
        if pro_expdat_setup and pro_expdat_setup.value_data == 'True':
            res = daud.dt_itemdesc
        else:
            res = spl[0]
    # print(res,"res")
    return res    

@register.simple_tag
def get_packages(daud):
    package_desc = []; packages = ""
    if daud.record_detail_type == "PACKAGE":
        package_dtl = PackageDtl.objects.filter(package_code=daud.dt_combocode,isactive=True)
        for i in package_dtl:
            desc = i.description
            package_desc.append(desc)
        packages = tuple(package_desc)

    return packages        