from django import template
register = template.Library()

@register.simple_tag
def disc_percent_calc(dt_price, dt_discamt, *args, **kwargs):
    # you would need to do any localization of the result here
    res = "{:.2f}".format(float((100 / dt_price) * dt_discamt))
    return res