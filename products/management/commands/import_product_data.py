import csv
import os
from django.core.management.base import BaseCommand
from products.models import Product
from django.core.files import File
from django.conf import settings

class Command(BaseCommand):
    help = 'Import product data from CSV file'

    def handle(self, *args, **kwargs):
        # Path to the CSV file
        csv_file_path = os.path.join(settings.BASE_DIR, 'data', 'products_recommandation_data.csv')
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Create or update product
                    product, created = Product.objects.get_or_create(
                        name=row['Product_ID'],
                        defaults={
                            'description': row.get('Description', 'No description available'),
                            'price': float(row.get('Price', 0)),
                            'category': row.get('Category', 'Uncategorized')
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Product already exists: {product.name}'))
                        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file not found at {csv_file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}')) 