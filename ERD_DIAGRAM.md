# Entity Relationship Diagram (ERD)

## Wholesale APN & SIM Management API - Database Schema

---

## Entity Relationship Diagram (Visual Representation)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                 │
│                     Wholesale APN & SIM Management API                       │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────┐
                    │      ORGANIZATION            │
                    │──────────────────────────────│
                    │ PK: org_id (UUID)            │
                    │──────────────────────────────│
                    │     name (VARCHAR 255)       │
                    │     industry (VARCHAR 255)   │
                    │     contact_email (EMAIL)    │
                    │     date_created (DATETIME)  │
                    └──────────────┬───────────────┘
                                   │
                                   │ 1
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              │                    │                    │
           N  │                 N  │                 N  │
    ┌─────────▼──────────┐  ┌──────▼──────────────┐  ┌▼─────────────────────┐
    │       USER          │  │       APN           │  │    BILLING_CYCLE      │
    │─────────────────────│  │─────────────────────│  │──────────────────────│
    │ PK: id (INT)        │  │ PK: apn_id (UUID)   │  │ PK: cycle_id (UUID)  │
    │ FK: organization_id │  │ FK: organization_id │  │ FK: organization_id  │
    │─────────────────────│  │─────────────────────│  │──────────────────────│
    │     username        │  │     name            │  │     start_date       │
    │     email           │  │     apn_string      │  │     end_date         │
    │     password        │  │     username ⚡      │  │     is_active        │
    │     role            │  │     password ⚡      │  │     date_created     │
    │     phone_number    │  │     auth_type       │  │     date_modified    │
    │     is_active       │  │     is_active       │  └──────────┬───────────┘
    │     date_joined     │  │     date_created    │             │
    └─────────────────────┘  │     date_modified   │             │
          (AbstractUser)     └──────────┬──────────┘             │
                                        │                        │
                                        │ 1                      │
                                        │                        │
                                     N  │                        │
                            ┌───────────▼────────────────┐       │
                            │       SIM_CARD             │       │
                            │────────────────────────────│       │
                            │ PK: sim_id (UUID)          │       │
                            │ FK: organization_id        │       │
                            │ FK: apn_id                 │       │
                            │────────────────────────────│       │
                            │     iccid (UNIQUE)         │       │
                            │     phone_number (UNIQUE)  │       │
                            │     status                 │       │
                            │     carrier                │       │
                            │     network_type           │       │
                            │     data_limit_mb          │       │
                            │     activation_date        │       │
                            │     expiry_date            │       │
                            │     date_created           │       │
                            │     date_modified          │       │
                            │     notes                  │       │
                            └───────────┬────────────────┘       │
                                        │                        │
                                        │ 1                      │
                                        │                        │
                                     N  │                     N  │
                            ┌───────────▼────────────────────────▼──────┐
                            │       DATA_USAGE_RECORD                   │
                            │───────────────────────────────────────────│
                            │ PK: record_id (UUID)                      │
                            │ FK: sim_card_id                           │
                            │ FK: billing_cycle_id                      │
                            │───────────────────────────────────────────│
                            │     data_consumed_mb (DECIMAL 10,2)       │
                            │     timestamp (DATETIME)                  │
                            │     recorded_at (DATETIME)                │
                            │     source (VARCHAR 50)                   │
                            │     notes (TEXT)                          │
                            └───────────────────────────────────────────┘

⚡ = Encrypted Field (EncryptedCharField)
```

---

## Relationship Details

### 1. **Organization → User** (One-to-Many)
- **Cardinality**: 1:N
- **Relationship**: One organization can have multiple users
- **Foreign Key**: `User.organization_id` references `Organization.org_id`
- **Delete Rule**: CASCADE (if organization deleted, users are deleted)
- **Business Rule**: Users belong to a single organization (multi-tenancy)

### 2. **Organization → APN** (One-to-Many)
- **Cardinality**: 1:N
- **Relationship**: One organization can have multiple APNs
- **Foreign Key**: `APN.organization_id` references `Organization.org_id`
- **Delete Rule**: CASCADE (if organization deleted, APNs are deleted)
- **Business Rule**: APNs can be organization-specific or shared (NULL org_id)

### 3. **Organization → SIMCard** (One-to-Many)
- **Cardinality**: 1:N
- **Relationship**: One organization can own multiple SIM cards
- **Foreign Key**: `SIMCard.organization_id` references `Organization.org_id`
- **Delete Rule**: SET_NULL (if organization deleted, SIMs remain but unassigned)
- **Business Rule**: SIM ownership tracked per organization

### 4. **Organization → BillingCycle** (One-to-Many)
- **Cardinality**: 1:N
- **Relationship**: One organization has multiple billing cycles
- **Foreign Key**: `BillingCycle.organization_id` references `Organization.org_id`
- **Delete Rule**: CASCADE (if organization deleted, billing cycles are deleted)
- **Business Rule**: Each organization has distinct billing periods

### 5. **APN → SIMCard** (One-to-Many)
- **Cardinality**: 1:N
- **Relationship**: One APN configuration can be assigned to multiple SIM cards
- **Foreign Key**: `SIMCard.apn_id` references `APN.apn_id`
- **Delete Rule**: SET_NULL (if APN deleted, SIM remains but unassigned)
- **Business Rule**: SIM cards use APN configurations for data connectivity

### 6. **SIMCard → DataUsageRecord** (One-to-Many)
- **Cardinality**: 1:N
- **Relationship**: One SIM card generates multiple usage records
- **Foreign Key**: `DataUsageRecord.sim_card_id` references `SIMCard.sim_id`
- **Delete Rule**: CASCADE (if SIM deleted, usage records are deleted)
- **Business Rule**: Historical tracking of all data consumption

### 7. **BillingCycle → DataUsageRecord** (One-to-Many)
- **Cardinality**: 1:N
- **Relationship**: One billing cycle contains multiple usage records
- **Foreign Key**: `DataUsageRecord.billing_cycle_id` references `BillingCycle.cycle_id`
- **Delete Rule**: CASCADE (if cycle deleted, associated records are deleted)
- **Business Rule**: Usage tracked within billing periods for reporting

---

## Entity Descriptions

### **Organization**
**Purpose**: Represents enterprise clients in the multi-tenant system

| Attribute     | Type         | Constraints      | Description                    |
| ------------- | ------------ | ---------------- | ------------------------------ |
| org_id        | UUID         | PK, NOT NULL     | Unique organization identifier |
| name          | VARCHAR(255) | NOT NULL         | Organization name              |
| industry      | VARCHAR(255) | NULL             | Industry classification        |
| contact_email | EMAIL        | UNIQUE, NOT NULL | Primary contact email          |
| date_created  | DATETIME     | AUTO             | Record creation timestamp      |

**Indexes**: Primary key on `org_id`, Unique on `contact_email`

---

### **User (extends AbstractUser)**
**Purpose**: System users with role-based access control

| Attribute       | Type         | Constraints      | Description                     |
| --------------- | ------------ | ---------------- | ------------------------------- |
| id              | INT          | PK, AUTO         | User identifier                 |
| organization_id | UUID         | FK, NULL         | Associated organization         |
| username        | VARCHAR(150) | UNIQUE, NOT NULL | Login username                  |
| email           | EMAIL        | UNIQUE           | User email address              |
| password        | VARCHAR(128) | NOT NULL         | Hashed password                 |
| role            | VARCHAR(20)  | NOT NULL         | network_admin or client_manager |
| phone_number    | VARCHAR(20)  | NULL             | Contact number                  |
| is_active       | BOOLEAN      | DEFAULT TRUE     | Account status                  |
| date_joined     | DATETIME     | AUTO             | Registration date               |

**Roles**:
- `network_admin`: Full CRUD access, unlimited API calls
- `client_manager`: Read-only access, rate-limited

**Indexes**: Primary key on `id`, Unique on `username`, `email`, Index on `organization_id`

---

### **APN (Access Point Name)**
**Purpose**: Data connectivity configurations for SIM cards

| Attribute           | Type         | Constraints      | Description                        |
| ------------------- | ------------ | ---------------- | ---------------------------------- |
| apn_id              | UUID         | PK, NOT NULL     | APN identifier                     |
| organization_id     | UUID         | FK, NULL         | Owner organization (NULL = shared) |
| name                | VARCHAR(100) | UNIQUE, NOT NULL | APN name                           |
| apn_string          | VARCHAR(255) | NOT NULL         | APN connection string              |
| username            | ENCRYPTED    | NULL             | Encrypted authentication username  |
| password            | ENCRYPTED    | NULL             | Encrypted authentication password  |
| authentication_type | VARCHAR(20)  | NOT NULL         | none, pap, chap, pap_chap          |
| is_active           | BOOLEAN      | DEFAULT TRUE     | Configuration status               |
| date_created        | DATETIME     | AUTO             | Creation timestamp                 |
| date_modified       | DATETIME     | AUTO_UPDATE      | Last modification                  |

**Security**: Username and password fields use Fernet encryption

**Indexes**: Primary key on `apn_id`, Unique on `name`, Index on `organization_id`

---

### **SIMCard**
**Purpose**: SIM card inventory management

| Attribute       | Type         | Constraints      | Description                                       |
| --------------- | ------------ | ---------------- | ------------------------------------------------- |
| sim_id          | UUID         | PK, NOT NULL     | SIM identifier                                    |
| organization_id | UUID         | FK, NULL         | Owning organization                               |
| apn_id          | UUID         | FK, NULL         | Assigned APN configuration                        |
| iccid           | VARCHAR(22)  | UNIQUE, NOT NULL | Integrated Circuit Card ID                        |
| phone_number    | VARCHAR(20)  | UNIQUE, NULL     | Associated phone number                           |
| status          | VARCHAR(20)  | NOT NULL         | available, assigned, suspended, deactivated, lost |
| carrier         | VARCHAR(100) | NOT NULL         | Network carrier                                   |
| network_type    | VARCHAR(10)  | NOT NULL         | 2G, 3G, 4G, 5G                                    |
| data_limit_mb   | INT          | NULL             | Monthly data limit (1-100,000 MB)                 |
| activation_date | DATE         | NULL             | Service activation date                           |
| expiry_date     | DATE         | NULL             | Service expiry date                               |
| date_created    | DATETIME     | AUTO             | Creation timestamp                                |
| date_modified   | DATETIME     | AUTO_UPDATE      | Last modification                                 |
| notes           | TEXT         | NULL             | Additional information                            |

**Status Values**:
- `available`: Ready for assignment
- `assigned`: Active and in use
- `suspended`: Temporarily disabled (automated when limit exceeded)
- `deactivated`: Permanently disabled
- `lost`: Reported lost/stolen

**Indexes**: Primary key on `sim_id`, Unique on `iccid`, `phone_number`, Index on `organization_id`, `apn_id`, `status`

---

### **BillingCycle**
**Purpose**: Billing period tracking for organizations

| Attribute       | Type     | Constraints  | Description             |
| --------------- | -------- | ------------ | ----------------------- |
| cycle_id        | UUID     | PK, NOT NULL | Cycle identifier        |
| organization_id | UUID     | FK, NOT NULL | Associated organization |
| start_date      | DATE     | NOT NULL     | Cycle start date        |
| end_date        | DATE     | NOT NULL     | Cycle end date          |
| is_active       | BOOLEAN  | DEFAULT TRUE | Cycle status            |
| date_created    | DATETIME | AUTO         | Creation timestamp      |
| date_modified   | DATETIME | AUTO_UPDATE  | Last modification       |

**Constraints**: UNIQUE(organization_id, start_date, end_date)

**Indexes**: Primary key on `cycle_id`, Index on `organization_id`, Composite index on `(organization_id, start_date, end_date)`

---

### **DataUsageRecord**
**Purpose**: Individual data consumption tracking

| Attribute        | Type          | Constraints           | Description                |
| ---------------- | ------------- | --------------------- | -------------------------- |
| record_id        | UUID          | PK, NOT NULL          | Record identifier          |
| sim_card_id      | UUID          | FK, NOT NULL          | Associated SIM card        |
| billing_cycle_id | UUID          | FK, NULL              | Associated billing cycle   |
| data_consumed_mb | DECIMAL(10,2) | NOT NULL              | Data consumed in megabytes |
| timestamp        | DATETIME      | AUTO                  | Record creation time       |
| recorded_at      | DATETIME      | NOT NULL              | Actual usage timestamp     |
| source           | VARCHAR(50)   | DEFAULT 'celery_task' | Data source                |
| notes            | TEXT          | NULL                  | Additional information     |

**Data Sources**:
- `celery_task`: Automated ingestion via Celery workers
- `manual_entry`: Manual input by administrators
- `api_import`: Bulk API imports

**Indexes**: 
- Primary key on `record_id`
- Composite index on `(sim_card_id, recorded_at DESC)`
- Composite index on `(billing_cycle_id, recorded_at DESC)`

---

## Key Business Rules

### Multi-Tenancy
- Organizations are isolated - users can only see their organization's data
- Network admins have elevated permissions within their organization
- Superusers can see all organizations

### Data Limit Enforcement
- When SIM card's cumulative usage exceeds `data_limit_mb`, status automatically changes to `suspended`
- Triggered by Celery background workers monitoring usage records
- Admins can manually reactivate suspended SIMs

### Encryption
- APN credentials (username, password) are encrypted at rest using Fernet encryption
- Encryption key stored in environment variable `FIELD_ENCRYPTION_KEY`

### Cascading Deletes
- Deleting an organization removes all associated users, APNs, billing cycles
- SIM cards are SET_NULL (retained but unassigned) when organization is deleted
- Usage records are CASCADE deleted with parent SIM card

---

## Database Technology

- **RDBMS**: MySQL 8.0+
- **ORM**: Django ORM (Django 6.0.5)
- **Character Set**: utf8mb4
- **Collation**: utf8mb4_unicode_ci
- **Engine**: InnoDB (default)

---

## Schema Version

- **Version**: 1.0
- **Last Updated**: 2026-06-05
- **Migration Files**: 
  - `users/migrations/0001_initial.py`
  - `inventory/migrations/0001_initial.py`
  - `inventory/migrations/0002_add_data_limit_validators.py`
  - `inventory/migrations/0003_alter_apn_password_alter_apn_username.py`
  - `usage/migrations/0001_initial.py`

---

*This ERD represents the complete database schema for the Wholesale APN & SIM Management API NQF Level 5 Capstone Project.*
