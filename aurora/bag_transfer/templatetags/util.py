from django import template
from django.contrib.auth.models import Group
from bag_transfer.models import Archives

register = template.Library()


@register.filter
def get_type(value):
    return type(value).__name__


@register.filter
def has_group(user, group_name):
    if not user:
        return False
    return user.groups.filter(name=group_name).exists()


@register.filter
def progress_class(status):
    label_class = 'green'
    if status in [10, 20]:
        label_class = 'yellow'
    elif status in [30, 60]:
        label_class = 'red'
    return label_class


@register.filter
def progress_percentage(status):
    return int(round(float(status)/Archives.ACCESSIONING_COMPLETE * 100))
