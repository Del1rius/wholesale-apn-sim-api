# 📡 APN & SIM Management API

> A comprehensive enterprise-grade REST API for managing Access Point Names (APNs) and SIM card inventory with multi-tenant support.

[![Django](https://img.shields.io/badge/Django-6.0.5-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.17.1-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Authentication](#-authentication)
- [Usage Examples](#-usage-examples)
- [Docker Deployment](#-docker-deployment)
- [Project Structure](#-project-structure)
- [Authors](#-authors)

---

## 🎯 Overview

The **APN & SIM Management API** is a robust backend solution designed for telecommunications providers and enterprises to efficiently manage their SIM card inventory, APN configurations, and data usage tracking. Built with Django and Django REST Framework, it provides a scalable, secure, and feature-rich platform for multi-tenant operations.

This project serves as an **NQF Level 5 Capstone Project** demonstrating advanced Python development skills, RESTful API design, microservices architecture, automated background processing, and enterprise-grade security practices.

### Business Problem Statement

Telecommunications providers and wholesale SIM resellers face significant challenges in managing large-scale SIM card inventories, monitoring data usage in real-time, and preventing service abuse through automated limit enforcement. Traditional manual monitoring approaches are:

- ❌ **Time-intensive** - Manual checks cannot scale to thousands of SIM cards
- ❌ **Error-prone** - Human oversight leads to missed limit violations
- ❌ **Costly** - Undetected overages result in financial losses
- ❌ **Reactive** - Issues discovered after the fact, not proactively

**Solution**: This API provides an **automated, real-time monitoring system** that:
- ✅ Tracks data usage continuously via background workers
- ✅ Automatically suspends SIM cards when limits are exceeded
- ✅ Provides multi-tenant isolation for wholesale operations
- ✅ Offers role-based access control for secure operations
- ✅ Delivers comprehensive usage analytics and reporting

### Key Capabilities

- 🏢 **Multi-Tenant Architecture** - Isolated data management for multiple organizations
- 📊 **Inventory Management** - Track and manage SIM cards and APN configurations
- 📈 **Usage Analytics** - Monitor data consumption and usage patterns
- 🔐 **Role-Based Access Control** - Granular permissions for Network Admins and Client Managers
- 🔄 **RESTful API** - Clean, intuitive endpoints following REST best practices
- 📚 **Auto-Generated Documentation** - Interactive API docs with Swagger/OpenAPI
- 🤖 **Automated Suspension** - Real-time limit enforcement via Celery workers
- 🐳 **Containerized Deployment** - Docker-based microservices architecture

---

## ✨ Features

### Core Functionality

- ✅ **User Management**
  - Custom user model with organization association
  - Role-based access (Network Administrator, Client Manager)
  - JWT-based authentication with token refresh
  - User profile management

- ✅ **Organization Management**
  - Multi-tenant support with data isolation
  - Organization-specific configurations
  - Industry classification and contact management

- ✅ **Inventory Module**
  - SIM card lifecycle management
  - APN configuration and assignment
  - Bulk import/export capabilities
  - Status tracking (Active, Inactive, Suspended)

- ✅ **Usage Tracking**
  - Real-time data usage monitoring
  - Historical usage analytics
  - Threshold alerts and notifications
  - Billing integration support

### Security Features

- 🔒 JWT token-based authentication
- 🛡️ CORS protection
- 🔑 Environment-based secret management
- 👥 Role-based access control (RBAC)
- 🔐 Password validation and hashing
- 🚦 **API Rate Limiting & Throttling**
  - Anonymous users: 100 requests/hour
  - Authenticated users: 1,000 requests/hour
  - Burst protection: 60 requests/minute
  - Usage logging: 500 requests/minute
  - Admin bypass for unlimited access
  - See [RATE_LIMITING.md](RATE_LIMITING.md) for details

---

## 🛠️ Tech Stack

| Category             | Technology                          |
| -------------------- | ----------------------------------- |
| **Framework**        | Django 6.0.5                        |
| **API**              | Django REST Framework 3.17.1        |
| **Authentication**   | JWT (djangorestframework-simplejwt) |
| **Database**         | MySQL 8.0+                          |
| **Documentation**    | drf-yasg (Swagger/OpenAPI)          |
| **Containerization** | Docker & Docker Compose             |
| **Python Version**   | 3.10+                               |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client Applications                  │
│              (Web, Mobile, Third-party APIs)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS/REST
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Django REST Framework                   │
│  ┌──────────────┬──────────────┬──────────────────────┐ │
│  │   Users API  │ Inventory API│   Usage API          │ │
│  └──────────────┴──────────────┴──────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │         JWT Authentication Middleware             │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ ORM
                     │
┌────────────────────▼────────────────────────────────────┐
│                      MySQL Database                      │
│  ┌──────────┬──────────────┬──────────┬──────────────┐  │
│  │  Users   │ Organizations│ Inventory│    Usage     │  │
│  └──────────┴──────────────┴──────────┴──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **MySQL 8.0+** - [Download](https://dev.mysql.com/downloads/)
- **pip** - Python package manager
- **virtualenv** - For isolated Python environments
- **Git** - Version control

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/Tauriqbaker/APN-SIM-Management-API.git
cd APN-SIM-Management-API
```

2. **Create and activate virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

### Environment Configuration

1. **Create `.env` file in the project root**

```bash
# Copy the example environment file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

2. **Configure environment variables**

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=apn_sim_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

3. **Create MySQL database**

```sql
CREATE DATABASE apn_sim_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**

```bash
python manage.py createsuperuser
```

**OR load test data with pre-configured users:**

```bash
python manage.py seed_database
```

This will populate your database with:
- Multiple test organizations (Vodacom, MTN, Cell C, Telkom, Rain)
- Admin and client manager users for each organization
- Sample SIM cards with various statuses
- Usage records and billing cycles

**Demo Login Credentials:**
- Username: `admin_vodacom_south_a`
- Password: `TestPass123!`

> 📋 See `DEMO_CREDENTIALS.md` for all available demo accounts

6. **Run development server**

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

---

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **Django Admin**: `http://localhost:8000/admin/`

### API Endpoints Overview

#### Authentication

```
POST   /api/auth/register/          - Register new user
POST   /api/auth/login/             - Login and get JWT tokens
POST   /api/auth/token/refresh/     - Refresh access token
POST   /api/auth/logout/            - Logout (blacklist token)
```

#### Users

```
GET    /api/users/                  - List all users (Admin only)
GET    /api/users/{id}/             - Get user details
PUT    /api/users/{id}/             - Update user
DELETE /api/users/{id}/             - Delete user
GET    /api/users/me/               - Get current user profile
```

#### Organizations

```
GET    /api/organizations/          - List organizations
POST   /api/organizations/          - Create organization
GET    /api/organizations/{id}/     - Get organization details
PUT    /api/organizations/{id}/     - Update organization
DELETE /api/organizations/{id}/     - Delete organization
```

#### Inventory

```
GET    /api/inventory/sims/         - List SIM cards
POST   /api/inventory/sims/         - Add new SIM card
GET    /api/inventory/sims/{id}/    - Get SIM card details
PUT    /api/inventory/sims/{id}/    - Update SIM card
DELETE /api/inventory/sims/{id}/    - Delete SIM card
GET    /api/inventory/apns/         - List APN configurations
POST   /api/inventory/apns/         - Create APN configuration
GET    /api/inventory/apns/{id}/    - Get APN details
PUT    /api/inventory/apns/{id}/    - Update APN configuration
DELETE /api/inventory/apns/{id}/    - Delete APN configuration
```

#### Usage

```
GET    /api/usage/                  - Get usage statistics
GET    /api/usage/{sim_id}/         - Get SIM-specific usage
POST   /api/usage/                  - Record usage data
POST   /api/usage/report/           - Generate usage report
GET    /api/usage/logs/             - Get usage logs
```

---

## 🗄️ Database Schema

### Core Models

#### User Model
```python
- id (PK)
- username (unique)
- email (unique)
- password (hashed)
- organization_id (FK)
- role (network_admin | client_manager)
- phone_number
- is_active
- date_joined
```

#### Organization Model
```python
- org_id (UUID, PK)
- name
- industry
- contact_email (unique)
- date_created
```

### Relationships

```
Organization (1) ──────< (N) User
Organization (1) ──────< (N) SIM Card (planned)
SIM Card (1) ──────< (N) Usage Record (planned)
```

---

## 🔐 Authentication

This API uses **JWT (JSON Web Tokens)** for authentication.

### Getting Access Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using the Token

Include the access token in the Authorization header:

```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Token Refresh

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

---

## 💡 Usage Examples

### Register a New Organization and User

```python
import requests

# Register organization
org_data = {
    "name": "Acme Telecom",
    "industry": "Telecommunications",
    "contact_email": "admin@acmetelecom.com"
}
response = requests.post("http://localhost:8000/api/organizations/", json=org_data)
org_id = response.json()["org_id"]

# Register user
user_data = {
    "username": "john_admin",
    "email": "john@acmetelecom.com",
    "password": "SecurePass123!",
    "organization": org_id,
    "role": "network_admin",
    "phone_number": "+1234567890"
}
response = requests.post("http://localhost:8000/api/auth/register/", json=user_data)
```

### Authenticate and Access Protected Endpoint

```python
# Login
login_data = {
    "username": "john_admin",
    "password": "SecurePass123!"
}
response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
access_token = response.json()["access"]

# Access protected endpoint
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8000/api/users/me/", headers=headers)
print(response.json())
```

---

## 🐳 Docker Deployment

### Using Docker Compose

1. **Build and start containers**

```bash
docker-compose up -d --build
```

2. **Run migrations**

```bash
docker-compose exec web python manage.py migrate
```

3. **Load seed data (recommended)**

```bash
docker-compose exec web python manage.py seed_database
```

This provides demo accounts for testing. See `DEMO_CREDENTIALS.md` for login details.

**OR create a superuser manually:**

```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Access the application**

- API: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Execute commands in container
docker-compose exec web python manage.py <command>
```

---

## 📁 Project Structure

```
APN-SIM-Management-API/
│
├── config/                          # Project configuration
│   ├── __pycache__/                # Python cache files
│   ├── __init__.py                 # Package initializer
│   ├── settings.py                 # Django settings
│   ├── urls.py                     # Main URL configuration
│   ├── wsgi.py                     # WSGI configuration
│   └── asgi.py                     # ASGI configuration
│
├── users/                           # User management app
│   ├── __pycache__/                # Python cache files
│   ├── api/                        # API endpoints
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── serializers.py          # DRF serializers
│   │   ├── urls.py                 # API URL routes
│   │   └── views.py                # API views
│   ├── migrations/                 # Database migrations
│   ├── __init__.py
│   ├── admin.py                    # Admin configuration
│   ├── apps.py                     # App configuration
│   ├── dashboard_urls.py           # Dashboard URL routes
│   ├── dashboard_views.py          # Dashboard views
│   ├── models.py                   # User and Organization models
│   └── tests.py                    # Unit tests
│
├── inventory/                       # SIM & APN inventory app
│   ├── __pycache__/                # Python cache files
│   ├── api/                        # API endpoints
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── serializers.py          # Inventory serializers
│   │   ├── urls.py                 # Inventory API routes
│   │   └── views.py                # Inventory API views
│   ├── migrations/                 # Database migrations
│   ├── __init__.py
│   ├── admin.py                    # Admin configuration
│   ├── apps.py                     # App configuration
│   ├── models.py                   # Inventory models
│   ├── tests.py                    # Unit tests
│   └── views.py                    # Inventory views
│
├── usage/                           # Usage tracking app
│   ├── __pycache__/                # Python cache files
│   ├── api/                        # API endpoints
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── serializers.py          # Usage serializers
│   │   ├── urls.py                 # Usage API routes
│   │   └── views.py                # Usage API views
│   ├── migrations/                 # Database migrations
│   ├── __init__.py
│   ├── admin.py                    # Admin configuration
│   ├── apps.py                     # App configuration
│   ├── models.py                   # Usage models
│   ├── tests.py                    # Unit tests
│   └── views.py                    # Usage views
│
├── static/                          # Static files
│   ├── css/                        # Stylesheets
│   │   ├── base.css                # Base styles
│   │   ├── dashboard.css           # Dashboard styles
│   │   ├── login.css               # Login page styles
│   │   ├── password.css            # Password change styles
│   │   ├── sim_detail.css          # SIM detail page styles
│   │   └── sim_list.css            # SIM list page styles
│   └── js/                         # JavaScript files
│       ├── dashboard.js            # Dashboard functionality
│       ├── main.js                 # Main JavaScript
│       └── sim_detail.js           # SIM detail functionality
│
├── templates/                       # HTML templates
│   ├── base.html                   # Base template
│   ├── dashboard.html              # Dashboard page
│   ├── login.html                  # Login page
│   ├── password_change.html        # Password change page
│   ├── password_change_done.html   # Password change confirmation
│   ├── sim_detail.html             # SIM detail page
│   └── sim_list.html               # SIM list page
│
├── venv/                            # Virtual environment
│   ├── Include/
│   ├── Lib/
│   ├── Scripts/
│   ├── .gitignore
│   └── pyvenv.cfg
│
├── .git/                            # Git repository
├── .vscode/                         # VS Code settings
│   └── settings.json
│
├── .dockerignore                    # Docker ignore rules
├── .env                             # Environment variables
├── .gitignore                       # Git ignore rules
├── create_bulk_test_data.py         # Bulk test data generator
├── create_test_data.py              # Test data generator
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                       # Docker configuration
├── manage.py                        # Django management script
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 📖 Project Documentation

### Core Documentation

| Document                                                 | Description                   | Purpose                                 |
| -------------------------------------------------------- | ----------------------------- | --------------------------------------- |
| [README.md](README.md)                                   | Main project documentation    | Overview, setup, and usage instructions |
| [ERD_DIAGRAM.md](ERD_DIAGRAM.md)                         | Entity Relationship Diagram   | Database schema and relationships       |
| [SYSTEM_FLOW_DIAGRAM.md](SYSTEM_FLOW_DIAGRAM.md)         | System architecture and flows | Automated processes and data flow       |
| [TESTING_SUMMARY.md](TESTING_SUMMARY.md)                 | Test results and coverage     | Comprehensive testing evidence          |
| [PEP8_COMPLIANCE_REPORT.md](PEP8_COMPLIANCE_REPORT.md)   | Code quality analysis         | PEP-8 compliance and code standards     |
| [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md) | Container deployment          | Docker setup and troubleshooting        |
| [DEMO_CREDENTIALS.md](DEMO_CREDENTIALS.md)               | Test user accounts            | Demo login credentials                  |

### API Documentation

- **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **ReDoc**: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)
- **Admin Panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 🎬 Live Demonstration Guide

This section provides a step-by-step walkthrough of the **automated SIM suspension feature**, demonstrating the core business value of the system.

### Demo Scenario: Automated Data Limit Enforcement

**Objective**: Demonstrate that the system automatically suspends a SIM card when its data usage exceeds the configured limit.

---

### Step 1: Environment Setup

**Start the Docker containers**:
```bash
docker compose up -d
```

**Verify all services are running**:
```bash
docker ps
```

Expected: 5 containers running (db, rabbitmq, web, celery_worker, flower)

---

### Step 2: Login to Dashboard

**Access the dashboard**:
```
http://localhost:8000/dashboard/
```

**Login credentials** (from seed data):
- Username: `admin_vodacom_south_a`
- Password: `TestPass123!`

**Expected**: Dashboard showing SIM card inventory and usage statistics

---

### Step 3: Identify Test SIM Card

From the dashboard or API, select a SIM card for testing:

**API Request**:
```bash
curl -X GET http://localhost:8000/api/inventory/sims/ \
  -H "Authorization: Bearer <your_access_token>"
```

**Example SIM Card**:
```json
{
  "sim_id": "abc123...",
  "iccid": "8927000000000000001",
  "phone_number": "+27821234567",
  "status": "assigned",
  "data_limit_mb": 1000,
  "carrier": "Vodacom"
}
```

**Note the following**:
- `sim_id`: Unique identifier
- `data_limit_mb`: 1000 MB (1 GB limit)
- `status`: "assigned" (currently active)

---

### Step 4: Check Current Usage

**Query current usage for the SIM**:
```bash
curl -X GET "http://localhost:8000/api/usage/usage-records/?sim_card=<sim_id>" \
  -H "Authorization: Bearer <your_access_token>"
```

**Calculate total usage**:
```json
{
  "count": 3,
  "results": [
    {"data_consumed_mb": 250.50, "recorded_at": "2026-06-04T10:00:00Z"},
    {"data_consumed_mb": 350.25, "recorded_at": "2026-06-04T14:30:00Z"},
    {"data_consumed_mb": 200.00, "recorded_at": "2026-06-05T09:00:00Z"}
  ]
}
```

**Total Usage**: 250.50 + 350.25 + 200.00 = **800.75 MB**  
**Limit**: 1000 MB  
**Status**: Within limit ✅

---

### Step 5: Simulate Usage Exceeding Limit

**Create a new usage record that exceeds the limit**:
```bash
curl -X POST http://localhost:8000/api/usage/usage-records/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sim_card": "<sim_id>",
    "data_consumed_mb": 300.00,
    "recorded_at": "2026-06-05T10:30:00Z"
  }'
```

**New Total**: 800.75 + 300.00 = **1100.75 MB** 🔴 **EXCEEDS LIMIT**

---

### Step 6: Monitor Automated Suspension

**Watch Celery worker logs in real-time**:
```bash
docker logs -f apnsimmanagementapi-celery_worker-1
```

**Expected output**:
```
[2026-06-05 10:30:15,234: INFO/MainProcess] Task usage.tasks.check_sim_data_limit[abc-def-123] received
[2026-06-05 10:30:15,456: INFO/ForkPoolWorker-1] Checking SIM 8927000000000000001
[2026-06-05 10:30:15,678: INFO/ForkPoolWorker-1] Total usage: 1100.75 MB, Limit: 1000 MB
[2026-06-05 10:30:15,890: WARNING/ForkPoolWorker-1] SIM 8927000000000000001 exceeded limit - SUSPENDING
[2026-06-05 10:30:16,123: INFO/ForkPoolWorker-1] SIM 8927000000000000001 status changed to 'suspended'
[2026-06-05 10:30:16,345: INFO/MainProcess] Task usage.tasks.check_sim_data_limit[abc-def-123] succeeded in 0.112s
```

**Timing**: Suspension occurs within **seconds** of usage record creation ⚡

---

### Step 7: Verify Suspension in Dashboard

**Refresh the dashboard**:
```
http://localhost:8000/dashboard/
```

**Expected changes**:
- 🔴 **Status Badge**: Changed from "ASSIGNED" to "SUSPENDED"
- 📊 **Usage Bar**: Shows red (over 100%)
- ⚠️ **Alert Icon**: Warning indicator displayed
- 📈 **Usage**: Shows "1100.75 MB / 1000 MB (110%)"

**Screenshot opportunity**: Capture this view for demonstration

---

### Step 8: Verify Suspension via API

**Query the SIM card again**:
```bash
curl -X GET "http://localhost:8000/api/inventory/sims/<sim_id>/" \
  -H "Authorization: Bearer <your_access_token>"
```

**Response**:
```json
{
  "sim_id": "abc123...",
  "iccid": "8927000000000000001",
  "phone_number": "+27821234567",
  "status": "suspended",  // ← Changed from "assigned"
  "data_limit_mb": 1000,
  "carrier": "Vodacom",
  "date_modified": "2026-06-05T10:30:16Z"  // ← Timestamp of suspension
}
```

---

### Step 9: Monitor in Flower Dashboard

**Access Flower monitoring interface**:
```
http://localhost:5555
```

**View task execution**:
- Navigate to "Tasks" tab
- Find `usage.tasks.check_sim_data_limit`
- View execution history, success rate, timing

**Expected**:
- ✅ Task status: SUCCESS
- ⏱️ Execution time: < 1 second
- 📊 Success rate: 100%

---

### Step 10: Admin Reactivation

**Login as network admin**:
- Username: `Admin`
- Password: `TestPass123!`

**Reactivate the SIM via API**:
```bash
curl -X PATCH "http://localhost:8000/api/inventory/sims/<sim_id>/" \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "assigned",
    "data_limit_mb": 2000
  }'
```

**Result**: SIM reactivated with increased limit (2000 MB)

**Demonstration complete** ✅

---

### Demo Verification Checklist

Use this checklist during live demonstration:

- [ ] All Docker containers running (5/5)
- [ ] Successfully logged into dashboard
- [ ] Identified test SIM card with known limit
- [ ] Verified current usage is below limit
- [ ] Created usage record exceeding limit
- [ ] Observed Celery worker processing in logs
- [ ] Confirmed status changed to "suspended" in dashboard
- [ ] Verified suspension via API query
- [ ] Checked task execution in Flower
- [ ] Demonstrated admin reactivation capability

---

### Key Demonstration Points

During the demo, emphasize these aspects:

1. **Automation** 🤖
   - No manual intervention required
   - Suspension happens within seconds of limit breach
   - Reduces operational overhead

2. **Real-Time Monitoring** ⚡
   - Background workers continuously process usage data
   - Immediate detection of limit violations
   - Proactive vs. reactive approach

3. **Scalability** 📈
   - Architecture handles thousands of SIM cards
   - Celery workers can be scaled horizontally
   - Message queue ensures reliable processing

4. **Security** 🔐
   - Role-based access control enforced
   - Only admins can reactivate suspended SIMs
   - Audit trail maintained via date_modified

5. **Business Value** 💰
   - Prevents revenue loss from overages
   - Automates compliance enforcement
   - Reduces manual monitoring costs
   - Provides real-time visibility

---

## 👥 Authors

- **Timothy Barry** - [GitHub](https://github.com/TimothyBarry)
- **Tauriq Baker** - [GitHub](https://github.com/Tauriqbaker)
- **Yahya Baker** - [GitHub](https://github.com/YahyaBaker)

---

## 🗺️ Roadmap

### Phase 1 - Foundation ✅
- [x] Project setup and configuration
- [x] User authentication with JWT
- [x] Multi-tenant organization model
- [x] API documentation with Swagger

### Phase 2 - Core Features ✅
- [x] SIM card inventory management
- [x] APN configuration system
- [x] Bulk import/export functionality
- [x] Advanced search and filtering

### Phase 3 - Analytics ✅
- [x] Usage tracking and monitoring
- [x] Real-time data consumption alerts
- [x] Historical analytics dashboard
- [x] Usage reporting system

### Phase 4 - Enhancement 📋
- [ ] Mobile application
- [ ] Advanced reporting features
- [ ] Third-party integrations
- [ ] Performance optimization
- [ ] Automated billing system

---

## 🏆 Project Compliance

### Academic Requirements (NQF Level 5)

✅ **Demonstrates Advanced Python Skills**
- Object-oriented design with Django models
- RESTful API development with DRF
- Asynchronous task processing with Celery
- Database design and optimization

✅ **Enterprise-Grade Architecture**
- Microservices containerization (Docker)
- Message queue integration (RabbitMQ)
- Background worker processes (Celery)
- Automated monitoring and alerting

✅ **Security Best Practices**
- JWT authentication
- Role-based access control
- Field-level encryption (APN credentials)
- Rate limiting and throttling

✅ **Code Quality Standards**
- **PEP-8 Compliance**: 93.81% (B+ rating)
- Comprehensive test coverage (44 tests, 100% pass rate)
- Documented codebase with docstrings
- See [PEP8_COMPLIANCE_REPORT.md](PEP8_COMPLIANCE_REPORT.md)

✅ **Testing Evidence**
- 44 Django TestCase tests (100% passing)
- Rate limiting tests (5/5 passing)
- Endpoint functionality tests (24/24 passing)
- See [TESTING_SUMMARY.md](TESTING_SUMMARY.md)

✅ **Documentation**
- Entity Relationship Diagram (ERD)
- System Flow Diagram
- API documentation (Swagger/OpenAPI)
- Deployment guides
- Testing reports

---

## 📊 Project Statistics

| Metric              | Value  |
| ------------------- | ------ |
| Lines of Code       | ~8,000 |
| API Endpoints       | 24+    |
| Database Tables     | 6      |
| Docker Containers   | 5      |
| Test Cases          | 44     |
| Test Pass Rate      | 100%   |
| PEP-8 Compliance    | 93.81% |
| Documentation Pages | 7      |

---

## 🎓 Skills Demonstrated

This capstone project demonstrates proficiency in:

### Backend Development
- ✅ Python 3.10+ programming
- ✅ Django web framework
- ✅ Django REST Framework (DRF)
- ✅ Database design (MySQL)
- ✅ ORM and query optimization

### API Design
- ✅ RESTful architecture
- ✅ JWT authentication
- ✅ API versioning
- ✅ Rate limiting
- ✅ API documentation (Swagger)

### DevOps & Infrastructure
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Environment configuration
- ✅ Deployment automation

### Asynchronous Processing
- ✅ Celery task queues
- ✅ RabbitMQ message broker
- ✅ Background workers
- ✅ Task monitoring (Flower)

### Security
- ✅ Authentication & Authorization
- ✅ Data encryption
- ✅ CORS configuration
- ✅ SQL injection prevention
- ✅ XSS protection

### Testing
- ✅ Unit testing
- ✅ Integration testing
- ✅ API endpoint testing
- ✅ Rate limit testing

### Code Quality
- ✅ PEP-8 standards
- ✅ Code documentation
- ✅ Version control (Git)
- ✅ Code review practices

---

<div align="center">

**Made with ❤️ by the APN & SIM Management Team**

[Report Bug](https://github.com/Tauriqbaker/APN-SIM-Management-API/issues) · [Request Feature](https://github.com/Tauriqbaker/APN-SIM-Management-API/issues)

</div>
