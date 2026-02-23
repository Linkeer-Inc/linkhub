import uuid

from django.core.validators import MinValueValidator
from django.db import models

from tenants.models import TenantDomain

class ActiveLinksManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class LinkCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)

    def __str__(self) -> str:
        return self.name

class Link(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.ForeignKey(TenantDomain, on_delete=models.PROTECT, related_name="links")
    category = models.ForeignKey(LinkCategory, on_delete=models.CASCADE, null=True, related_name="category")
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True, default="")
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    exibition_order = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    emphasis = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)

    objects = ActiveLinksManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["domain", "exibition_order"], name="unique_exibition_order_per_domain")
        ]

    def __str__(self) -> str:
        return self.name

class LinkClick(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    link = models.ForeignKey(Link, on_delete=models.SET_NULL, null=True, blank=True, related_name="clicks")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    payload = models.JSONField(null=True, blank=True)
    referrer = models.URLField(max_length=2000, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    client_x = models.IntegerField(null=True, blank=True)
    client_y = models.IntegerField(null=True, blank=True)
    viewport_width = models.IntegerField(null=True, blank=True)
    viewport_height = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        link_id = self.link_id if getattr(self, "link_id", None) else "unknown"
        return f"LinkClick {self.id} for {link_id} at {self.timestamp}"