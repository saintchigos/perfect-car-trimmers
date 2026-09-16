from urllib.parse import quote

from django.conf import settings

from .models import SiteContent


def shop_info(request):
    general_message = f"Hi, I'd like to find out more about {settings.SHOP_NAME}."
    return {
        'shop_name': settings.SHOP_NAME,
        'shop_short_name': getattr(settings, 'SHOP_SHORT_NAME', settings.SHOP_NAME),
        'site_content': SiteContent.load(),
        'shop_location': settings.SHOP_LOCATION,
        'shop_address': settings.SHOP_ADDRESS,
        'shop_phone_display': settings.SHOP_PHONE_DISPLAY,
        'shop_facebook_url': settings.SHOP_FACEBOOK_URL,
        'shop_maps_url': settings.SHOP_MAPS_URL,
        'shop_maps_embed_url': settings.SHOP_MAPS_EMBED_URL,
        'shop_whatsapp_general_url': (
            f"https://wa.me/{settings.SHOP_WHATSAPP_NUMBER}?text={quote(general_message)}"
        ),
        'shop_site_url': settings.SHOP_SITE_URL,
    }
