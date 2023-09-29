# Create your import here .

def two_decimal_digit(amount):
    v = str(amount).split('.')
    c = float(v[0])
    if len(v) > 1:
        c = float(v[0]+"."+v[1][:2])
    return c