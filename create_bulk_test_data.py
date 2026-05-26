"""
Script to create bulk test data for the APN & SIM Management API
Creates 10 SIMs for each status type with usage data
Run with: Get-Content create_bulk_test_data.py | python manage.py shell
"""

from users.models import Organization, User
from inventory.models import SIMCard, APN
from usage.models import BillingCycle, DataUsageRecord
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

print("=" * 70)
print("Creating Bulk Test Data for APN & SIM Management API")
print("=" * 70)

# Get or create organization
org = Organization.objects.first()
if not org:
    org = Organization.objects.create(
        name="Backspace Technologies",
        industry="Telecommunications",
        contact_email="admin@backspace.tech"
    )
    print(f"✅ Created organization: {org.name}")
else:
    print(f"✅ Using existing organization: {org.name}")

# Get or create APN
apn = APN.objects.first()
if not apn:
    apn = APN.objects.create(
        name="Backspace APN",
        apn_string="internet.backspace",
        organization=org,
        is_active=True
    )
    print(f"✅ Created APN: {apn.name}")
else:
    print(f"✅ Using existing APN: {apn.name}")

# Create billing cycle for current month
today = timezone.now().date()
cycle, created = BillingCycle.objects.get_or_create(
    organization=org,
    start_date=today.replace(day=1),
    end_date=(today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
    defaults={'is_active': True}
)
if created:
    print(f"✅ Created billing cycle: {cycle.start_date} to {cycle.end_date}")
else:
    print(f"✅ Using existing billing cycle: {cycle.start_date} to {cycle.end_date}")

# Delete existing test SIMs to start fresh
existing_count = SIMCard.objects.filter(iccid__startswith='890123456789').count()
if existing_count > 0:
    SIMCard.objects.filter(iccid__startswith='890123456789').delete()
    print(f"🗑️  Deleted {existing_count} existing test SIMs")

# Carriers for variety
carriers = ['Vodacom', 'MTN', 'Cell C', 'Telkom']
network_types = ['4G', '5G']

# Status configurations
status_configs = [
    {'status': 'assigned', 'count': 10, 'label': 'Active (Assigned)'},
    {'status': 'suspended', 'count': 10, 'label': 'Suspended'},
    {'status': 'deactivated', 'count': 10, 'label': 'Deactivated'},
    {'status': 'available', 'count': 10, 'label': 'Unallocated (Available)'},
]

total_created = 0
iccid_counter = 10000

print("\n" + "=" * 70)
print("Creating SIM Cards...")
print("=" * 70)

for config in status_configs:
    status = config['status']
    count = config['count']
    label = config['label']
    
    print(f"\n📱 Creating {count} {label} SIMs...")
    
    for i in range(count):
        iccid_counter += 1
        iccid = f"89012345678901{iccid_counter}"
        phone_number = f"+2781{random.randint(1000000, 9999999)}"
        carrier = random.choice(carriers)
        network_type = random.choice(network_types)
        data_limit = random.choice([1000, 2000, 5000, 10000])  # MB
        
        # Create SIM
        sim = SIMCard.objects.create(
            iccid=iccid,
            phone_number=phone_number,
            status=status,
            carrier=carrier,
            network_type=network_type,
            organization=org,
            apn=apn,
            data_limit_mb=data_limit,
            activation_date=today - timedelta(days=random.randint(1, 90))
        )
        
        # Create usage data for assigned and suspended SIMs
        if status in ['assigned', 'suspended']:
            # Suspended SIMs should have exceeded their limit
            if status == 'suspended':
                # Usage between 100% and 120% of limit
                total_usage = data_limit * random.uniform(1.0, 1.2)
            else:
                # Active SIMs have usage between 10% and 95% of limit
                total_usage = data_limit * random.uniform(0.1, 0.95)
            
            # Split usage into 3-7 records over the past few days
            num_records = random.randint(3, 7)
            remaining_usage = total_usage
            
            for j in range(num_records):
                if j == num_records - 1:
                    # Last record gets remaining usage
                    usage_amount = remaining_usage
                else:
                    # Random portion of remaining usage
                    usage_amount = remaining_usage * random.uniform(0.1, 0.4)
                    remaining_usage -= usage_amount
                
                DataUsageRecord.objects.create(
                    sim_card=sim,
                    billing_cycle=cycle,
                    data_consumed_mb=Decimal(str(round(usage_amount, 2))),
                    recorded_at=timezone.now() - timedelta(hours=random.randint(1, 168)),
                    source='celery_task'
                )
        
        total_created += 1
        if (i + 1) % 5 == 0:
            print(f"   ✓ Created {i + 1}/{count} {label} SIMs")
    
    print(f"   ✅ Completed {count} {label} SIMs")

print("\n" + "=" * 70)
print(f"✅ Successfully created {total_created} SIM cards!")
print("=" * 70)

# Print summary statistics
print("\n📊 Summary:")
print(f"   • Total SIMs: {SIMCard.objects.count()}")
print(f"   • Active (Assigned): {SIMCard.objects.filter(status='assigned').count()}")
print(f"   • Suspended: {SIMCard.objects.filter(status='suspended').count()}")
print(f"   • Deactivated: {SIMCard.objects.filter(status='deactivated').count()}")
print(f"   • Unallocated (Available): {SIMCard.objects.filter(status='available').count()}")
print(f"   • Total Usage Records: {DataUsageRecord.objects.count()}")
print(f"   • Billing Cycles: {BillingCycle.objects.count()}")

print("\n" + "=" * 70)
print("🎉 Bulk test data creation complete!")
print("=" * 70)
