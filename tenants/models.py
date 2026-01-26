import uuid

from django.db import models
from django.db.models import Q
from django_tenants.utils import get_public_schema_name
from django_tenants.models import TenantMixin, DomainMixin

from .validators import validate_file_extension, validate_file_size

class TenantDomain(DomainMixin):
    created_on = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)

def tenant_branding_upload_to(instance, filename):
    return f"tenants/{instance.id}/branding/{filename}"

class Tenant(TenantMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=100,null=True)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)
    branding_icon = models.ImageField(
        upload_to=tenant_branding_upload_to,
        null=True,
        validators=[validate_file_extension,validate_file_size]
    )
    primary_color = models.CharField(max_length=40)

    auto_drop_schema = False

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schema_name'],
                condition=Q(schema_name=get_public_schema_name()),
                name='unique_public_schema'
            )
        ]
    
    def __str__(self):
        return self.name