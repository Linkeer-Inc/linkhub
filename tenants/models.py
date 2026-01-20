import uuid
from django.db import models
from django.db.models import Q
from django_tenants.utils import get_public_schema_name
from django_tenants.models import TenantMixin, DomainMixin

class TenantDomain(DomainMixin):
    created_on = models.DateTimeField(auto_now_add=True)

class Tenant(TenantMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=100,null=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    
    auto_drop_schema = False

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schema_name'],
                condition=Q(schema_name=get_public_schema_name()),
                name='unique_public_schema'
            )
        ]