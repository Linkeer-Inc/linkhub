import uuid
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100,unique=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    
    auto_drop_schema = False

class TenantDomain(DomainMixin):
    pass