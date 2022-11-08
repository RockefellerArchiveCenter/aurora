from django.conf import settings


def mtm_id(request):
    """Adds Matomo Tag Manager ID to requests."""
    return {"mtm_id": settings.MTM_ID}
