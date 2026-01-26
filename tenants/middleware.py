from django.http import Http404, HttpResponse
from django_tenants.middleware import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name

from django.shortcuts import render

class TenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, domain_model, hostname):
        tenant = super().get_tenant(domain_model, hostname)

        if tenant.schema_name == get_public_schema_name():
            return tenant

        if not tenant.is_active:
            raise Http404('tenant not active')
        
        return tenant
    def no_tenant_found(self, request, hostname):
        return render(
            request,
            "tenant_not_found.html",
            status=404
        )