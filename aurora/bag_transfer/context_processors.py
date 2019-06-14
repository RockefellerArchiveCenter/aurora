# bag_transfer/context_processors.py

from django.conf import settings

def ga_tracking_id(request):
    return {'ga_tracking_id': settings.GA_TRACKING_ID}
