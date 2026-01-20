from django.http.request import split_domain_port

def tenant(request):
    domainFromRequest, port = split_domain_port(request.get_host())
    domain = request.tenant.domains.filter(domain=domainFromRequest).first()

    return {
        "tenant": getattr(request, "tenant", None),
        "domain": domain
    }