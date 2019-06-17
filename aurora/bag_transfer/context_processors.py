# bag_transfer/context_processors.py

from django.conf import settings

def gtm_id(request):
    return {'gtm_id': settings.GTM_ID}
