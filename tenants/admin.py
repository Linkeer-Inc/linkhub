import random

from django import forms
from django.contrib import admin
from .models import Tenant, TenantDomain

def random_css_hex_color():
    return "#{:06X}".format(random.randint(0, 0xFFFFFF))

class TenantModelForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['primary_color'].initial = random_css_hex_color()

@admin.register(Tenant)
class TenantsAdmin(admin.ModelAdmin):
    form = TenantModelForm
    list_display = ['name', 'schema_name', 'created_on', 'is_primary', 'is_active', 'description', 'primary_color']
    search_fields = ['name', 'schema_name']

@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_active']
    search_fields = ['domain', 'tenant']
    exclude = ['is_primary']