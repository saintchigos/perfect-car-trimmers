from datetime import date
from xml.sax.saxutils import escape

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.urls import NoReverseMatch, reverse
from django.views.decorators.http import require_GET

SITEMAP_PAGES = (
    ('bookings:home', 'daily', '1.0'),
    ('bookings:book', 'monthly', '0.9'),
    ('bookings:gallery', 'weekly', '0.8'),
)


@require_GET
def robots_txt(request: HttpRequest) -> HttpResponse:
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Disallow: /{settings.ADMIN_URL}',
        'Disallow: /staff',
        '',
        f'Sitemap: {settings.SHOP_SITE_URL}/sitemap.xml',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


@require_GET
def sitemap_xml(request: HttpRequest) -> HttpResponse:
    urls = []
    for name, changefreq, priority in SITEMAP_PAGES:
        try:
            loc = settings.SHOP_SITE_URL + reverse(name)
        except NoReverseMatch:
            continue
        urls.append(
            f'  <url>\n'
            f'    <loc>{escape(loc)}</loc>\n'
            f'    <lastmod>{date.today().isoformat()}</lastmod>\n'
            f'    <changefreq>{changefreq}</changefreq>\n'
            f'    <priority>{priority}</priority>\n'
            f'  </url>'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(urls)
        + '\n</urlset>\n'
    )
    return HttpResponse(xml, content_type='application/xml; charset=utf-8')