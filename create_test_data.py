"""
Script to create test data for the APN & SIM Management API
Run with: python manage.py shell < create_test_data.py
"""

from users.models import Organization, User
from inventory.models import SIMCard, APN
from usage.models import BillingCycle, DataUsageRecord
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

print("=" * 60)
print("Creating Test Data for APN & SIM Management API")
print("=" * 60)

# Check if organization exists, if not create one
org = Organization.objects.first()
if not org:
    org = Organization.objects.create(
        name="Test Organization",
        industry="Telecommunications",
        contact_email="test@example.com"
    )
    print(f"✅ Created organization: {org.name}")
else:
    print(f"✅ Using existing organization: {org.name}")

# Check if APN exists, if not create one
apn = APN.objects.first()
if not apn:
    apn = APN.objects.create(
        name="Test APN",
        apn_string="internet",
        organization=org,
        is_active=True
    )
    print(f"✅ Created APN: {apn.name}")
else:
    print(f"✅ Using existing APN: {apn.name}")

# Check if SIM exists, if not create one
sim = SIMCard.objects.first()
if not sim:
    sim = SIMCard.objects.create(
        iccid="89012345678901234567",
        phone_number="+27123456789",
        status="assigned",
        carrier="Vodacom",
        network_type="4G",
        organization=org,
        apn=apn,
        data_limit_mb=5000,
        activation_date=timezone.now().date()
    )
    print(f"✅ Created SIM: {sim.iccid}")
else:
    print(f"✅ Using existing SIM: {sim.iccid}")

# Create a billing cycle (current month)
today = timezone.now().date()
cycle = BillingCycle.objects.create(
    organization=org,
    start_date=today.replace(day=1),
    end_date=(today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
    is_active=True
)
print(f"✅ Created billing cycle: {cycle.start_date} to {cycle.end_date}")

# Create some usage records
usage1 = DataUsageRecord.objects.create(
    sim_card=sim,
    billing_cycle=cycle,
    data_consumed_mb=Decimal('150.50'),
    recorded_at=timezone.now(),
    source='celery_task'
)
print(f"✅ Created usage record 1: {usage1.data_consumed_mb} MB")

usage2 = DataUsageRecord.objects.create(
    sim_card=sim,
    billing_cycle=cycle,
    data_consumed_mb=Decimal('200.75'),
    recorded_at=timezone.now() - timedelta(hours=2),
    source='celery_task'
)
print(f"✅ Created usage record 2: {usage2.data_consumed_mb} MB")

usage3 = DataUsageRecord.objects.create(
    sim_card=sim,
    billing_cycle=cycle,
    data_consumed_mb=Decimal('320.00'),
    recorded_at=timezone.now() - timedelta(hours=5),
    source='celery_task'
)
print(f"✅ Created usage record 3: {usage3.data_consumed_mb} MB")

total_usage = 150.50 + 200.75 + 320.00
print("=" * 60)
print(f"✅ Test data created successfully!")
print(f"📊 Total usage for {sim.iccid}: {total_usage} MB ({total_usage/sim.data_limit_mb*100:.1f}% of limit)")
print("=" * 60)
