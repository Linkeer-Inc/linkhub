from os import environ
from django.http.request import split_domain_port


def tenant(request):
    try:
        domainFromRequest, _ = split_domain_port(request.get_host())
        domain = request.tenant.domains.filter(domain=domainFromRequest).first()

        return {
            "tenant": getattr(request, "tenant", None),
            "domain": domain,
            "APP_NAME": "LinkHub"
        }
    except:
        return {
          "APP_URL": environ.get('BASE_URL', 'localhost:8000')
        }