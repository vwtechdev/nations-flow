from django.conf import settings


def global_settings(request):
    return {
        'whatsapp_group_url': settings.WHATSAPP_GROUP_URL,
    }
