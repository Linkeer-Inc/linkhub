from django.contrib import admin
from .models import Link, LinkCategory, LinkClick

from tenants.models import TenantDomain

@admin.register(Link)
class LinksAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "is_active"]
    search_fields = ["name", "url"]

    def get_queryset(self, request):
        return Link.all_objects.all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "domain":
            kwargs["queryset"] = TenantDomain.objects.exclude(domain="localhost")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(LinkCategory)
class LinkCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(LinkClick)
class LinkClickAdmin(admin.ModelAdmin):
    list_display = ["short_id", "link", "timestamp", "referrer", "ip_address"]
    list_filter = ["timestamp", "link"]
    search_fields = ["link__name", "referrer", "user_agent", "payload"]
    readonly_fields = [
        "id",
        "link",
        "timestamp",
        "referrer",
        "ip_address",
        "user_agent",
        "client_x",
        "client_y",
        "viewport_width",
        "viewport_height",
        "payload",
    ]
    ordering = ["-timestamp"]

    fieldsets = (
        (None, {"fields": ("id", "link", "timestamp")}),
        ("Client", {"fields": ("ip_address", "referrer", "user_agent")}),
        ("Coordinates", {"fields": ("client_x", "client_y", "viewport_width", "viewport_height")}),
        ("Payload", {"fields": ("payload",)}),
    )

    def short_id(self, obj):
        return str(obj.id)[:8]

    short_id.admin_order_field = "id"
    short_id.short_description = "ID"