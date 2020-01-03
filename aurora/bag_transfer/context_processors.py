from django.conf import settings


def gtm_id(request):
    """Adds Google Tag Manager ID to requests."""
    return {"gtm_id": settings.GTM_ID}
