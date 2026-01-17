from django.http import Http404
from django_tenants.middleware import TenantMainMiddleware

class TenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, domain_model, hostname):
        tenant = super().get_tenant(domain_model, hostname)

        if not tenant.is_active:
            raise Http404('tenant not active')
        
        return tenant