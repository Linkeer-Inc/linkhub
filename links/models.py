import uuid
from django.core.validators import MinValueValidator
from django.db import models

from tenants.models import TenantDomain

class ActiveLinksManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
class LinkCategory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        unique=True,
        max_length=100
    )

    def __str__(self):
        return self.name

class Link(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    domain = models.ForeignKey(
        TenantDomain,
        on_delete=models.PROTECT,
        related_name="links"
    )
    category = models.ForeignKey(
        LinkCategory,
        on_delete=models.CASCADE,
        related_name="link_category",
    )
    name = models.CharField(max_length=100,unique=True)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    exibition_order = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)],
        null=False
    )
    created_on = models.DateField(auto_now_add=True)

    objects = ActiveLinksManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['domain', 'exibition_order'],
                name='unique_exibition_order_per_domain'
            )
        ]

    def __str__(self):
        return self.name