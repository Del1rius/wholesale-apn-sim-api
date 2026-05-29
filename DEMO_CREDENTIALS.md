# Demo Login Credentials

After running `python manage.py seed_database`, you can log in with any of the following accounts:

## Password for All Accounts
**Password:** `TestPass123!`

---

## Superuser Accounts

| Username | Email                          | Organization | Role      |
| -------- | ------------------------------ | ------------ | --------- |
| `Admin`  | timothy.barry@redacademy.co.za | -            | Superuser |

---

## Vodacom South Africa

| Username                | Email                 | Role                  |
| ----------------------- | --------------------- | --------------------- |
| `admin_vodacom_south_a` | admin@vodacom.co.za   | Network Administrator |
| `manager_vodacom_south` | manager@vodacom.co.za | Client Manager        |

---

## MTN Group

| Username            | Email           | Role                  |
| ------------------- | --------------- | --------------------- |
| `admin_mtn_group`   | admin@mtn.com   | Network Administrator |
| `manager_mtn_group` | manager@mtn.com | Client Manager        |

---

## Telkom SA

| Username            | Email                | Role                  |
| ------------------- | -------------------- | --------------------- |
| `admin_telkom_sa`   | admin@telkom.co.za   | Network Administrator |
| `manager_telkom_sa` | manager@telkom.co.za | Client Manager        |

---

## Cell C

| Username         | Email               | Role                  |
| ---------------- | ------------------- | --------------------- |
| `admin_cell_c`   | admin@cellc.co.za   | Network Administrator |
| `manager_cell_c` | manager@cellc.co.za | Client Manager        |

---

## Rain Networks

| Username                | Email              | Role                  |
| ----------------------- | ------------------ | --------------------- |
| `admin_rain_networks`   | admin@rain.co.za   | Network Administrator |
| `manager_rain_networks` | manager@rain.co.za | Client Manager        |

---

## Test User

| Username   | Email            | Role         |
| ---------- | ---------------- | ------------ |
| `testuser` | test@example.com | Test Account |

---

## Role Permissions

### Network Administrator
- Full access to organization's SIM cards and APNs
- Can view and manage all inventory
- Can update data limits
- Can view usage analytics

### Client Manager
- View-only access to organization's SIM cards
- Can view usage reports
- Cannot modify inventory or settings

### Superuser
- Full system access
- Can manage all organizations
- Can create/delete users
- Access to Django admin panel
