from django import template

register = template.Library()

@register.filter(name='reparuj')
def reparuj(value, arg):
    return ("[[[ %s ]]]" % value) + str(arg)
