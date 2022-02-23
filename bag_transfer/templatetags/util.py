from django import template

from bag_transfer.lib.view_helpers import label_class
from bag_transfer.models import Transfer

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
    return label_class(status)


@register.filter
def progress_percentage(status):
    return int(round(float(status) / Transfer.ACCESSIONING_COMPLETE * 100))
