from os import environ
from django.http.request import split_domain_port

def tenant(request):
    try:
        domainFromRequest, _ = split_domain_port(request.get_host())
        domain = request.tenant.domains.filter(domain=domainFromRequest).first()
        links = domain.links.filter(emphasis=False)
        links_with_emphasis = domain.links.filter(emphasis=True)
        branding_icon = request.tenant.branding_icon.url

        return {
            "tenant": getattr(request, "tenant", None),
            "domain": domain,
            "links": links,
            "links_with_emphasis": links_with_emphasis,
            "branding_icon": branding_icon,
            "APP_NAME": "YourLinks",
            "APP_URL": environ.get('BASE_URL', 'localhost:8000')
        }
    except Exception as e:
        print(f"Error in tenant context processor: {e}")
        return {
          "APP_NAME": "YourLinks",
          "APP_URL": environ.get('BASE_URL', 'localhost:8000'),
          "VIEW_DEMONSTRATION_URL": environ.get('VIEW_DEMONSTRATION_URL', 'localhost:8000')
        }
