from django.contrib import admin
from links.models import Link

@admin.register(Link)
class LinksAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active']
    search_fields = ['name', 'url']

    def get_queryset(self, request):
        return Link.all_objects.all()
