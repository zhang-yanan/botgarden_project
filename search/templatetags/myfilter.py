from django import template

register = template.Library()

@register.filter(is_safe=True, name='mysplit')

def mysplit(str, myfilter):
    return str.split(myfilter)