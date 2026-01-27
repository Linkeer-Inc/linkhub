from django.contrib import admin
from .models import Link, LinkCategory

from tenants.models import TenantDomain

@admin.register(Link)
class LinksAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active']
    search_fields = ['name', 'url']

    def get_queryset(self, request):
        return Link.all_objects.all()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'domain':
            kwargs['queryset'] = TenantDomain.objects.exclude(domain='localhost')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
@admin.register(LinkCategory)
class LinkCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']