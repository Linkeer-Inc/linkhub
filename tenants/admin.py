from django.contrib import admin
from django import forms
from .models import Tenant, TenantDomain

@admin.register(Tenant)
class TenantsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        forms.CharField: {
            "widget": forms.TextInput(attrs={"type": "color"})
        }
    }

    list_display = ['name', 'schema_name', 'created_on', 'is_active', 'description', 'primary_color']
    search_fields = ['name', 'schema_name']

@admin.register(TenantDomain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['tenant_domain']