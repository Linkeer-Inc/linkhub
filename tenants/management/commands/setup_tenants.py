from django.core.management.base import BaseCommand

from tenants.models import Tenant, TenantDomain

from os import environ

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais'

    def handle(self, *args, **options):    
        try:        
            primaryTenant, isPrimaryTenantCreated = Tenant.objects.get_or_create(
                schema_name="public",
                name=environ.get('HOST', 'localhost'),
                is_primary=True
            )

            if not isPrimaryTenantCreated:
                raise RuntimeError("Não foi possível criar o tenant primário (localhost)")
            
            _, isPrimaryTenantDomainCreated = TenantDomain.objects.get_or_create(
                tenant_id=primaryTenant.id,
                domain="localhost"
            )

            if not isPrimaryTenantDomainCreated:
                raise RuntimeError("Não foi possível criar o domínio para o tenant primário (localhost)")
        except RuntimeError:
            print("Skipping primary tenant initialization...")
