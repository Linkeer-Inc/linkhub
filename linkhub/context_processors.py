from tenants.models import TenantDomain

def tenant(request):
    return {
        "tenant": getattr(request, "tenant", None),
    }