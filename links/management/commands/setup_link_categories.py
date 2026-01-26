from django.core.management.base import BaseCommand

from links.models import LinkCategory

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais'

    def handle(self, *args, **options):    
        try:        
            linkCategories = [
                LinkCategory(name="Instagram"),
                LinkCategory(name="WhatsApp"),
                LinkCategory(name="Site"),
                LinkCategory(name="Linkedin"),
                LinkCategory(name="YouTube"),
                LinkCategory(name="Outros"),
            ]

            LinkCategory.objects.bulk_create(linkCategories,ignore_conflicts=True)
        except RuntimeError:
            print("Skipping link categories initialization...")
