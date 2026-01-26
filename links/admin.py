from django.contrib import admin
from .models import Link, LinkCategory

from tenants.models import TenantDomain

@admin.register(Link)
class LinksAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active']
    search_fields = ['name', 'url']

    def get_queryset(self, request):
        return Link.all_objects.all()
    
@admin.register(LinkCategory)
class LinksAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']