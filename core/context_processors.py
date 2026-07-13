from django.conf import settings


def environment(request):
    return {
        "registration_enabled": settings.SERVER_TYPE == settings.PRODUCTION,
    }
