from django import template

register = template.Library()

@register.filter
def get_type(value):
    return type(value).__name__
