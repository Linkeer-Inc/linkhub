import uuid
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class TenantDomain(DomainMixin):
    created_on = models.DateTimeField(auto_now_add=True,null=False)

class Tenant(TenantMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100,unique=True,null=False)
    is_primary = models.BooleanField(default=False,null=False)
    is_active = models.BooleanField(default=True,null=False)
    created_on = models.DateField(auto_now_add=True,null=False)
    
    auto_drop_schema = False