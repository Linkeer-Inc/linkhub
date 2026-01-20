from django.contrib import admin
from .models import Tenant, TenantDomain

@admin.register(Tenant)
class TenantsAdmin(admin.ModelAdmin):
    list_display = ['name', 'schema_name', 'created_on', 'is_active']
    search_fields = ['name', 'schema_name']

@admin.register(TenantDomain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['tenant_domain']