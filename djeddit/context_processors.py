from django.conf import settings


def djeddit_settings(request):
    return dict(BASE_TEMPLATE=settings.DJEDDIT_BASE_TEMPLATE if hasattr(settings, 'DJEDDIT_BASE_TEMPLATE') else 'djeddit/base.html')
