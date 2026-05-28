"""
Management command to seed the database with test data.

Usage:
    python manage.py seed_database
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seeds the database with test data from fixtures'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding database with test data...'))
        
        try:
            # Load the fixture data
            call_command('loaddata', 'fixtures/seed_data.json', verbosity=2)
            
            self.stdout.write(self.style.SUCCESS('✓ Database seeded successfully!'))
            self.stdout.write(self.style.SUCCESS('\nTest Credentials:'))
            self.stdout.write('  Username: admin_vodacom_south_a')
            self.stdout.write('  Password: password123')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error seeding database: {str(e)}'))
