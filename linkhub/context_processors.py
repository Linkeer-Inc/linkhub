from os import environ
from django.http.request import split_domain_port

def tenant(request):
    try:
        domainFromRequest, _ = split_domain_port(request.get_host())
        domain = request.tenant.domains.filter(domain=domainFromRequest).first()
        links = domain.links.filter(emphasis=False)
        links_with_emphasis = domain.links.filter(emphasis=True)

        return {
            "tenant": getattr(request, "tenant", None),
            "domain": domain,
            "links": links,
            "links_with_emphasis": links_with_emphasis,
            "APP_NAME": "YourLink"
        }
    except:
        return {
          "APP_URL": environ.get('BASE_URL', 'localhost:8000')
        }