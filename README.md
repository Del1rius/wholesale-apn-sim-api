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

### Key Capabilities

- 🏢 **Multi-Tenant Architecture** - Isolated data management for multiple organizations
- 📊 **Inventory Management** - Track and manage SIM cards and APN configurations
- 📈 **Usage Analytics** - Monitor data consumption and usage patterns
- 🔐 **Role-Based Access Control** - Granular permissions for Network Admins and Client Managers
- 🔄 **RESTful API** - Clean, intuitive endpoints following REST best practices
- 📚 **Auto-Generated Documentation** - Interactive API docs with Swagger/OpenAPI

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

<div align="center">

**Made with ❤️ by the APN & SIM Management Team**

[Report Bug](https://github.com/Tauriqbaker/APN-SIM-Management-API/issues) · [Request Feature](https://github.com/Tauriqbaker/APN-SIM-Management-API/issues)

</div>
