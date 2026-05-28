# Database Fixtures

This directory contains seed data for the APN & SIM Management system.

## Usage

### Load Seed Data

To populate your database with test data, run:

```bash
python manage.py seed_database
```

This will load all organizations, users, SIM cards, and usage data.

### Test Credentials

After seeding, you can log in with:

- **Username**: `admin_vodacom_south_a`
- **Password**: `password123`

## Creating New Fixtures

If you need to update the seed data:

1. Make changes to your database through the admin panel or API
2. Export the data:
   ```bash
   python manage.py dumpdata users inventory usage --indent 2 --output fixtures/seed_data.json
   ```

## What's Included

The `seed_data.json` fixture includes:

- **Organizations**: Multiple test organizations (Vodacom, MTN, Cell C, Telkom)
- **Users**: Admin and client manager accounts for each organization
- **SIM Cards**: Test SIM cards with various statuses (active, suspended, deactivated)
- **Usage Records**: Historical usage data for testing analytics
- **Billing Cycles**: Active billing cycles for each organization

## Notes

- Passwords in fixtures are hashed and secure
- All test data uses realistic South African telecom information
- SIM cards have varied usage patterns for testing suspension logic
