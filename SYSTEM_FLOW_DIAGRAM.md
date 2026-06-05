# System Flow Diagram

## Wholesale APN & SIM Management API - Architecture & Process Flows

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SYSTEM ARCHITECTURE                                 │
│                   Wholesale APN & SIM Management API                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   Web Browser    │         │  Mobile Client   │         │  External API    │
│   (Dashboard)    │         │   Application    │         │   Integrations   │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
         │                  HTTPS / REST API                       │
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                          ┌───────────▼────────────┐
                          │    NGINX / Proxy       │
                          │   (Load Balancer)      │
                          └───────────┬────────────┘
                                      │
                          ┌───────────▼────────────────────────────────────┐
                          │         Django REST Framework API              │
                          │              (Port 8000)                       │
                          │                                                │
                          │  ┌──────────────┬──────────────┬────────────┐ │
                          │  │  Users API   │ Inventory API│ Usage API  │ │
                          │  └──────────────┴──────────────┴────────────┘ │
                          │                                                │
                          │  ┌────────────────────────────────────────┐   │
                          │  │  Authentication Middleware (JWT)       │   │
                          │  │  Rate Limiting & Throttling            │   │
                          │  │  CORS Protection                       │   │
                          │  └────────────────────────────────────────┘   │
                          └───────────┬────────────────────┬───────────────┘
                                      │                    │
                                      │                    │
                   ┌──────────────────┴──────┐    ┌────────▼────────────┐
                   │     MySQL Database      │    │  RabbitMQ Message   │
                   │       (Port 3306)       │    │  Broker (Port 5672) │
                   │                         │    │                     │
                   │  ┌──────────────────┐   │    │  Task Queue for     │
                   │  │  organizations   │   │    │  Background Jobs    │
                   │  │  users           │   │    │                     │
                   │  │  apns            │   │    └──────────┬──────────┘
                   │  │  sim_cards       │   │               │
                   │  │  billing_cycles  │   │               │
                   │  │  usage_records   │   │       ┌───────▼──────────┐
                   │  └──────────────────┘   │       │  Celery Workers  │
                   │                         │       │                  │
                   └─────────────────────────┘       │  • Data Ingest   │
                                                     │  • Limit Checks  │
                                                     │  • Auto-Suspend  │
                                                     │  • Alerts        │
                                                     │                  │
                                                     └──────────┬───────┘
                                                                │
                                                     ┌──────────▼───────────┐
                                                     │   Flower Dashboard   │
                                                     │  Monitoring (5555)   │
                                                     └──────────────────────┘
```

---

## 1. Automated Data Usage Ingestion Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              AUTOMATED DATA USAGE INGESTION & PROCESSING                     │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: External Data Source
┌───────────────────────┐
│  Carrier Network API  │
│  (Vodacom, MTN, etc.) │
│                       │
│  • Real-time usage    │
│  • Batch CDR files    │
│  • SMS notifications  │
└───────────┬───────────┘
            │
            │ HTTP POST / File Upload
            │
Step 2: API Endpoint     ▼
┌─────────────────────────────────────────┐
│  POST /api/usage/usage-records/         │
│                                         │
│  Request Body:                          │
│  {                                      │
│    "sim_card": "uuid",                  │
│    "data_consumed_mb": 150.50,          │
│    "recorded_at": "2026-06-05T10:30:00" │
│  }                                      │
└───────────┬─────────────────────────────┘
            │
            │ Authentication & Validation
            │
Step 3: Django View      ▼
┌──────────────────────────────────────────┐
│  DataUsageRecordViewSet.create()        │
│                                          │
│  1. Authenticate JWT token              │
│  2. Validate request data                │
│  3. Check SIM card exists                │
│  4. Create DataUsageRecord               │
│  5. Trigger background task              │
└───────────┬──────────────────────────────┘
            │
            │ Save to Database
            │
Step 4: Database         ▼
┌──────────────────────────────────────────┐
│  INSERT INTO data_usage_records          │
│                                          │
│  record_id: UUID                         │
│  sim_card_id: FK → sim_cards.sim_id     │
│  data_consumed_mb: 150.50                │
│  recorded_at: 2026-06-05 10:30:00        │
│  source: "api_import"                    │
└───────────┬──────────────────────────────┘
            │
            │ Emit Event
            │
Step 5: Message Queue    ▼
┌──────────────────────────────────────────┐
│  RabbitMQ Task Queue                     │
│                                          │
│  Task: check_sim_data_limit              │
│  Args: {sim_id: "uuid"}                  │
│  Priority: HIGH                          │
└───────────┬──────────────────────────────┘
            │
            │ Celery Worker Picks Task
            │
Step 6: Background Task  ▼
┌──────────────────────────────────────────┐
│  Celery Worker: check_sim_data_limit()  │
│                                          │
│  1. Calculate total usage for SIM        │
│  2. Compare with data_limit_mb           │
│  3. If exceeded → suspend SIM            │
│  4. Send alert notification              │
└───────────┬──────────────────────────────┘
            │
            │ (If limit exceeded)
            │
Step 7: Auto-Suspension  ▼
┌──────────────────────────────────────────┐
│  UPDATE sim_cards                        │
│  SET status = 'suspended'                │
│  WHERE sim_id = 'uuid'                   │
│                                          │
│  + Log suspension event                  │
│  + Notify organization admins            │
└───────────┬──────────────────────────────┘
            │
            │ Real-time Update
            │
Step 8: Dashboard Update ▼
┌──────────────────────────────────────────┐
│  Dashboard View: /dashboard/sims/        │
│                                          │
│  🔴 SIM Status: SUSPENDED                │
│  📊 Usage: 1050 MB / 1000 MB (105%)      │
│  ⚠️  Alert: Data limit exceeded          │
└──────────────────────────────────────────┘
```

---

## 2. Automated SIM Suspension Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED SIM SUSPENSION FLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

START: Usage Record Created
         │
         ▼
┌────────────────────────┐
│  New DataUsageRecord   │
│  Saved to Database     │
└───────┬────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  Celery Task: check_sim_data_limit()       │
│                                             │
│  Query: SELECT SUM(data_consumed_mb)        │
│         FROM data_usage_records             │
│         WHERE sim_card_id = ?               │
│         AND billing_cycle_id = ?            │
└───────┬─────────────────────────────────────┘
        │
        ▼
┌────────────────────────┐
│  Calculate Total Usage │
│  total_usage_mb        │
└───────┬────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Compare with data_limit_mb     │
│                                 │
│  IF total_usage >= data_limit:  │
└───┬─────────────────────────┬───┘
    │                         │
    │ YES                     │ NO
    │                         │
    ▼                         ▼
┌──────────────────────┐  ┌───────────────────┐
│  SUSPEND SIM         │  │  Continue Normal  │
│                      │  │  Operation        │
│  Actions:            │  └───────────────────┘
│  1. Update status    │
│  2. Log event        │
│  3. Send alerts      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  UPDATE sim_cards                        │
│  SET status = 'suspended',               │
│      date_modified = NOW()               │
│  WHERE sim_id = ?                        │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Create Suspension Log Entry             │
│                                          │
│  log_entry = {                           │
│    "action": "auto_suspend",             │
│    "reason": "data_limit_exceeded",      │
│    "total_usage": "1050 MB",             │
│    "limit": "1000 MB",                   │
│    "timestamp": "2026-06-05T10:30:00"    │
│  }                                       │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Send Email Notification                 │
│                                          │
│  TO: Network Admins (organization)       │
│  SUBJECT: "SIM Suspended - Limit Hit"   │
│  BODY:                                   │
│    • SIM: [ICCID]                        │
│    • Usage: 1050 MB / 1000 MB            │
│    • Status: SUSPENDED                   │
│    • Action Required: Review & Reactivate│
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Dashboard Real-Time Update              │
│                                          │
│  • Status badge changes to 🔴 SUSPENDED  │
│  • Usage bar shows red (over limit)      │
│  • Alert icon displayed                  │
│  • Notification sent to logged-in users  │
└──────────────────────────────────────────┘
       │
       ▼
    [END]
```

---

## 3. User Authentication & Authorization Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION & AUTHORIZATION FLOW                       │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Login Request
┌─────────────────────────────────────┐
│  POST /api/auth/login/              │
│                                     │
│  {                                  │
│    "username": "admin_vodacom",     │
│    "password": "TestPass123!"       │
│  }                                  │
└───────────┬─────────────────────────┘
            │
            ▼
Step 2: Credential Verification
┌─────────────────────────────────────┐
│  Django Authentication Backend      │
│                                     │
│  1. Validate username exists        │
│  2. Check password hash             │
│  3. Verify account is_active        │
└───────────┬─────────────────────────┘
            │
            ▼
Step 3: Generate JWT Tokens
┌─────────────────────────────────────┐
│  JWT Token Generation               │
│                                     │
│  Access Token: (60 min lifetime)    │
│  {                                  │
│    "user_id": 123,                  │
│    "username": "admin_vodacom",     │
│    "role": "network_admin",         │
│    "org_id": "uuid",                │
│    "exp": 1234567890                │
│  }                                  │
│                                     │
│  Refresh Token: (7 day lifetime)    │
└───────────┬─────────────────────────┘
            │
            ▼
Step 4: Return Tokens
┌─────────────────────────────────────┐
│  Response (200 OK)                  │
│                                     │
│  {                                  │
│    "access": "eyJ0eXAi...",         │
│    "refresh": "eyJ0eXAi...",        │
│    "user": {                        │
│      "id": 123,                     │
│      "username": "admin_vodacom",   │
│      "role": "network_admin",       │
│      "organization": {...}          │
│    }                                │
│  }                                  │
└───────────┬─────────────────────────┘
            │
            ▼
Step 5: Authenticated API Request
┌─────────────────────────────────────┐
│  GET /api/inventory/sims/           │
│                                     │
│  Headers:                           │
│    Authorization: Bearer eyJ0eXAi...│
└───────────┬─────────────────────────┘
            │
            ▼
Step 6: Token Validation
┌─────────────────────────────────────┐
│  JWT Authentication Middleware      │
│                                     │
│  1. Extract token from header       │
│  2. Verify signature                │
│  3. Check expiration                │
│  4. Load user from payload          │
└───────────┬─────────────────────────┘
            │
            ▼
Step 7: Permission Check
┌─────────────────────────────────────┐
│  Role-Based Access Control          │
│                                     │
│  IF role == "network_admin":        │
│    → Full CRUD access               │
│    → Bypass rate limits             │
│    → View all org data              │
│                                     │
│  IF role == "client_manager":       │
│    → Read-only access               │
│    → Rate limited (60/min)          │
│    → View own org data only         │
└───────────┬─────────────────────────┘
            │
            ▼
Step 8: Execute Request
┌─────────────────────────────────────┐
│  Execute API Logic                  │
│                                     │
│  • Filter by organization           │
│  • Apply rate limiting              │
│  • Return filtered data             │
└─────────────────────────────────────┘
```

---

## 4. Rate Limiting & Throttling Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RATE LIMITING & THROTTLING FLOW                        │
└─────────────────────────────────────────────────────────────────────────────┘

Incoming API Request
         │
         ▼
┌────────────────────────┐
│  Check User Status     │
└────┬──────────┬────────┘
     │          │
     │          │
┌────▼─────┐  ┌▼──────────┐  ┌──────────────┐
│Anonymous │  │Authenticated│  │  Superuser/  │
│   User   │  │    User     │  │Network Admin │
└────┬─────┘  └┬────────────┘  └──────┬───────┘
     │         │                       │
     ▼         ▼                       ▼
┌─────────┐ ┌──────────┐     ┌────────────────┐
│100 req/ │ │ 60 req/  │     │   Unlimited    │
│  hour   │ │  minute  │     │   (Bypassed)   │
└────┬────┘ └─────┬────┘     └────────┬───────┘
     │            │                    │
     ▼            ▼                    ▼
┌──────────────────────────────────────────────┐
│  Check Request Count in Cache (Redis/Memory)│
│                                              │
│  Key: "throttle_{user_id}_{scope}"          │
│  Value: {request_count, window_start}       │
└────┬─────────────────────────────────────────┘
     │
     ▼
┌────────────────────────┐
│  Compare with Limit    │
└─┬──────────────────┬───┘
  │                  │
  │ Within Limit     │ Exceeded
  │                  │
  ▼                  ▼
┌──────────────┐  ┌─────────────────────────┐
│ Allow Request│  │  Return 429 Too Many    │
│ Increment    │  │       Requests          │
│ Counter      │  │                         │
└──────────────┘  │  Headers:               │
                  │  X-RateLimit-Limit: 60  │
                  │  X-RateLimit-Remaining: 0│
                  │  Retry-After: 45 seconds │
                  └─────────────────────────┘
```

---

## 5. Dashboard Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DASHBOARD DATA FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

User Opens Dashboard
         │
         ▼
┌────────────────────────────┐
│  GET /dashboard/           │
│                            │
│  Authentication: Cookie    │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Django Template View                  │
│                                        │
│  1. Verify session authentication      │
│  2. Get user organization              │
│  3. Query SIM cards for org            │
│  4. Calculate usage statistics         │
└───────────┬────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Database Queries                      │
│                                        │
│  SIM Cards:                            │
│    • Total count                       │
│    • Status breakdown                  │
│    • Near-limit SIMs                   │
│                                        │
│  Usage Records:                        │
│    • Today's consumption               │
│    • Billing cycle totals              │
│    • Top consumers                     │
└───────────┬────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Render HTML Template                  │
│                                        │
│  • SIM status cards                    │
│  • Usage charts (Chart.js)             │
│  • Alert notifications                 │
│  • Action buttons                      │
└───────────┬────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  JavaScript AJAX Calls                 │
│  (Auto-refresh every 30 seconds)       │
│                                        │
│  GET /api/inventory/sims/?status=...   │
│  GET /api/usage/usage-records/recent/  │
└───────────┬────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Real-Time Updates                     │
│                                        │
│  • Status badges update                │
│  • Usage bars re-render                │
│  • Alerts appear/disappear             │
│  • Counts refresh                      │
└────────────────────────────────────────┘
```

---

## 6. Docker Container Orchestration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOCKER CONTAINER ORCHESTRATION                            │
└─────────────────────────────────────────────────────────────────────────────┘

docker-compose up
         │
         ▼
┌────────────────────────────────────────┐
│  Container: db (MySQL 8.0)             │
│  Port: 3307:3306                       │
│  Volume: mysql_data:/var/lib/mysql     │
│  Status: ✅ Ready                       │
└───────────┬────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Container: rabbitmq                   │
│  Port: 5672 (AMQP), 15672 (Management)│
│  Healthcheck: rabbitmq-diagnostics ping│
│  Status: ✅ Ready                       │
└───────────┬────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Container: web (Django)               │
│  Port: 8000:8000                       │
│  Command: python manage.py runserver   │
│  Depends: db, rabbitmq                 │
│  Status: ✅ Running                     │
└───────────┬────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Container: celery_worker              │
│  Command: celery -A config worker      │
│  Depends: db, rabbitmq                 │
│  Tasks:                                │
│    • check_sim_data_limit              │
│    • bulk_import_sim_cards             │
│    • check_sim_inventory_levels        │
│  Status: ✅ Running                     │
└───────────┬────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Container: flower                     │
│  Port: 5555:5555                       │
│  Command: celery -A config flower      │
│  Monitoring: Celery task queue         │
│  Status: ✅ Running                     │
└────────────────────────────────────────┘

All containers running in network: apnsimmanagementapi_default
```

---

## Key System Features

### 1. **Automated Monitoring**
- Celery workers continuously monitor SIM usage
- Real-time limit checks on every usage record insertion
- Automated suspension without manual intervention

### 2. **Microservices Architecture**
- Independent containers for each service
- Horizontal scaling capability
- Isolated failure domains

### 3. **Message Queue Processing**
- RabbitMQ handles asynchronous task distribution
- Celery workers process tasks in background
- Retry mechanisms for failed tasks

### 4. **Multi-Tenant Isolation**
- Organization-based data filtering
- Role-based access control
- Separate billing cycles per organization

### 5. **Security Layers**
- JWT token authentication
- Rate limiting and throttling
- Encrypted sensitive data (APN credentials)
- HTTPS/TLS in production

---

## Performance Metrics

| Component              | Metric      | Target      |
| ---------------------- | ----------- | ----------- |
| API Response Time      | Average     | < 200ms     |
| Database Query Time    | Average     | < 50ms      |
| Celery Task Processing | Average     | < 5 seconds |
| Dashboard Load Time    | First Paint | < 1 second  |
| Concurrent Users       | Supported   | 1000+       |
| Rate Limit Enforcement | Accuracy    | 100%        |

---

*This System Flow Diagram illustrates the complete architecture and automated processes for the Wholesale APN & SIM Management API NQF Level 5 Capstone Project.*
