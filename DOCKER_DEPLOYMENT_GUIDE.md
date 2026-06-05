# Docker Deployment Guide

## Wholesale APN & SIM Management API - Containerized Deployment

---

## Overview

This guide documents the Docker containerization and deployment architecture for the Wholesale APN & SIM Management API. The application uses a **microservices architecture** with separate containers for the web application, database, message broker, background workers, and monitoring tools.

---

## Architecture Components

### Container Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

                     ┌─────────────────────────────┐
                     │    Host Machine (Windows)    │
                     │    Docker Desktop           │
                     └─────────────┬───────────────┘
                                   │
            ┌──────────────────────┴──────────────────────┐
            │    Docker Network: apnsimmanagementapi_default │
            └──────────────────────┬──────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
    ┌────▼─────┐            ┌──────▼──────┐         ┌──────▼──────┐
    │   db     │            │   rabbitmq  │         │     web     │
    │ MySQL 8.0│            │  RabbitMQ   │         │   Django    │
    │ Port 3307│            │  Port 5672  │         │  Port 8000  │
    └──────────┘            │  Port 15672 │         └──────┬──────┘
                            └─────────────┘                │
                                                           │
                                      ┌────────────────────┴──────────────────┐
                                      │                                       │
                              ┌───────▼────────┐                   ┌─────────▼──────┐
                              │ celery_worker  │                   │     flower     │
                              │  Background    │                   │   Monitoring   │
                              │     Tasks      │                   │   Port 5555    │
                              └────────────────┘                   └────────────────┘
```

---

## Container Specifications

### 1. Database Container (`db`)

**Image**: `mysql:8.0`  
**Purpose**: Persistent data storage for all application data

#### Configuration
```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
    ports:
      - "3307:3306"
    volumes:
      - mysql_data:/var/lib/mysql
```

#### Details
- **External Port**: 3307 (mapped to internal 3306)
- **Volume**: `mysql_data` (persistent storage)
- **Environment Variables**:
  - `DB_NAME`: Database name from `.env.docker`
  - `DB_PASSWORD`: Root password from `.env.docker`
- **Data Persistence**: Yes (Docker volume)
- **Character Set**: utf8mb4
- **Collation**: utf8mb4_unicode_ci

#### Verification
```bash
# Check container status
docker ps | grep db

# Connect to database
docker exec -it apnsimmanagementapi-db-1 mysql -u root -p

# Verify database exists
SHOW DATABASES;
USE apn_sim_db;
SHOW TABLES;
```

---

### 2. Message Broker Container (`rabbitmq`)

**Image**: `rabbitmq:3.12-management`  
**Purpose**: Task queue for asynchronous background jobs

#### Configuration
```yaml
services:
  rabbitmq:
    image: rabbitmq:3.12-management
    ports:
      - "5672:5672"    # AMQP protocol
      - "15672:15672"  # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

#### Details
- **AMQP Port**: 5672 (for Celery workers)
- **Management UI Port**: 15672 (web interface)
- **Default Credentials**: guest/guest
- **Health Check**: Built-in diagnostics every 10 seconds
- **Message Persistence**: Yes (by default)

#### Verification
```bash
# Check container health
docker ps | grep rabbitmq

# Access management interface
# Open browser: http://localhost:15672
# Login: guest / guest

# Check queues
docker exec apnsimmanagementapi-rabbitmq-1 rabbitmqctl list_queues
```

---

### 3. Web Application Container (`web`)

**Image**: Built from `Dockerfile`  
**Purpose**: Django REST Framework API server

#### Configuration
```yaml
services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - rabbitmq
    env_file:
      - .env.docker
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
```

#### Details
- **Base Image**: Python 3.10+ (from Dockerfile)
- **Port**: 8000 (Django development server)
- **Volume Mount**: Current directory → `/app` (hot reload)
- **Dependencies**: Waits for `db` and `rabbitmq` to start
- **Environment**: Loaded from `.env.docker`

#### Key Endpoints
- API Root: `http://localhost:8000/api/`
- Swagger Docs: `http://localhost:8000/swagger/`
- Admin Panel: `http://localhost:8000/admin/`
- Dashboard: `http://localhost:8000/dashboard/`

#### Verification
```bash
# Check container logs
docker logs apnsimmanagementapi-web-1

# Test API
curl http://localhost:8000/api/

# Enter container shell
docker exec -it apnsimmanagementapi-web-1 /bin/bash

# Check Django status
docker exec apnsimmanagementapi-web-1 python manage.py check
```

---

### 4. Celery Worker Container (`celery_worker`)

**Image**: Built from `Dockerfile` (same as web)  
**Purpose**: Background task processing

#### Configuration
```yaml
services:
  celery_worker:
    build: .
    command: celery -A config worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - rabbitmq
    env_file:
      - .env.docker
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
```

#### Details
- **Worker Concurrency**: Auto (based on CPU cores)
- **Log Level**: INFO
- **Task Types**:
  - Data usage monitoring
  - SIM limit checks
  - Automated suspension
  - Bulk imports
  - Inventory alerts
- **Auto-restart**: Yes (on code changes via volume mount)

#### Verification
```bash
# Check worker logs
docker logs -f apnsimmanagementapi-celery_worker-1

# Check active workers
docker exec apnsimmanagementapi-celery_worker-1 celery -A config inspect active

# Check registered tasks
docker exec apnsimmanagementapi-celery_worker-1 celery -A config inspect registered
```

---

### 5. Flower Monitoring Container (`flower`)

**Image**: Built from `Dockerfile` (same as web)  
**Purpose**: Real-time Celery task monitoring

#### Configuration
```yaml
services:
  flower:
    build: .
    command: celery -A config flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - rabbitmq
      - celery_worker
    env_file:
      - .env.docker
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
```

#### Details
- **Port**: 5555 (web interface)
- **Features**:
  - Real-time task monitoring
  - Worker statistics
  - Task history
  - Task rate graphs
  - Worker management
- **Authentication**: None (development only)

#### Verification
```bash
# Access Flower UI
# Open browser: http://localhost:5555

# Check container status
docker ps | grep flower
```

---

## Dockerfile Configuration

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Default command (overridden in docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## Environment Configuration

### Required Environment Variables (`.env.docker`)

```env
# Django Settings
SECRET_KEY=your-production-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web

# Database Configuration (Docker)
DB_NAME=apn_sim_db
DB_USER=root
DB_PASSWORD=your_mysql_root_password
DB_HOST=db
DB_PORT=3306

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//

# Field Encryption (Fernet key)
FIELD_ENCRYPTION_KEY=lkOnyFAi0nmbMz4yFYFcAifo9SQzHFiI-jgdKnOPbVo=

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## Deployment Procedures

### Initial Setup

#### 1. Build and Start Containers
```bash
# Navigate to project directory
cd "c:\Users\Flash_QE\OneDrive - redAcademy (Pty) Ltd\Python Module 1\APN & SIM Management API"

# Build images and start containers
docker compose up -d --build
```

**Expected Output**:
```
[+] Building 45.2s (12/12) FINISHED
[+] Running 6/6
 ✔ Network apnsimmanagementapi_default      Created
 ✔ Container apnsimmanagementapi-db-1       Started
 ✔ Container apnsimmanagementapi-rabbitmq-1 Started
 ✔ Container apnsimmanagementapi-web-1      Started
 ✔ Container apnsimmanagementapi-celery_worker-1 Started
 ✔ Container apnsimmanagementapi-flower-1   Started
```

#### 2. Run Database Migrations
```bash
# Apply database schema
docker compose exec web python manage.py migrate
```

**Expected Output**:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, inventory, sessions, usage, users
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying usage.0001_initial... OK
```

#### 3. Load Seed Data (Demo Accounts)
```bash
# Load pre-configured test data
docker compose exec web python manage.py seed_database
```

**Seed Data Includes**:
- 5 Organizations (Vodacom, MTN, Cell C, Telkom, Rain)
- Multiple admin and client manager users
- Sample SIM cards with various statuses
- Sample APNs
- Usage records and billing cycles

#### 4. Create Superuser (Alternative to Seed Data)
```bash
# Create admin account manually
docker compose exec web python manage.py createsuperuser
```

---

### Verification Checklist

#### ✅ All Containers Running
```bash
docker ps

# Should show 5 containers:
# - apnsimmanagementapi-db-1
# - apnsimmanagementapi-rabbitmq-1
# - apnsimmanagementapi-web-1
# - apnsimmanagementapi-celery_worker-1
# - apnsimmanagementapi-flower-1
```

#### ✅ Database Connected
```bash
docker compose exec web python manage.py dbshell

# Should connect to MySQL prompt
```

#### ✅ RabbitMQ Accessible
```bash
# Open browser: http://localhost:15672
# Login: guest / guest
# Should see RabbitMQ management interface
```

#### ✅ API Responding
```bash
curl http://localhost:8000/api/
# Should return JSON with available endpoints
```

#### ✅ Celery Worker Active
```bash
docker compose exec celery_worker celery -A config inspect active
# Should show worker is online
```

#### ✅ Flower Monitoring
```bash
# Open browser: http://localhost:5555
# Should see Flower dashboard with worker statistics
```

---

## Container Management

### Common Commands

#### View Container Status
```bash
# List all containers
docker ps

# List all containers (including stopped)
docker ps -a

# Check specific container
docker ps | grep web
```

#### View Container Logs
```bash
# All containers
docker compose logs

# Specific container
docker compose logs web

# Follow logs in real-time
docker compose logs -f web

# Last 50 lines
docker compose logs --tail=50 web
```

#### Restart Containers
```bash
# Restart all containers
docker compose restart

# Restart specific container
docker compose restart web

# Restart after code changes
docker compose restart web celery_worker
```

#### Stop Containers
```bash
# Stop all containers
docker compose down

# Stop and remove volumes (⚠️ deletes database)
docker compose down -v
```

#### Execute Commands in Container
```bash
# Open bash shell
docker compose exec web bash

# Run Django management command
docker compose exec web python manage.py <command>

# Run Django shell
docker compose exec web python manage.py shell
```

---

## Troubleshooting

### Issue 1: Containers Not Starting

**Symptoms**: `docker compose up` fails or containers exit immediately

**Solutions**:
```bash
# Check logs for errors
docker compose logs

# Check specific container
docker compose logs web

# Rebuild containers
docker compose up -d --build --force-recreate
```

### Issue 2: Database Connection Errors

**Symptoms**: `django.db.utils.OperationalError: (2002, "Can't connect to MySQL")`

**Solutions**:
```bash
# Verify database container is running
docker ps | grep db

# Check database logs
docker compose logs db

# Restart database
docker compose restart db

# Wait for database to be ready
docker compose exec web python manage.py wait_for_db
```

### Issue 3: Celery Worker Not Processing Tasks

**Symptoms**: Tasks stuck in queue, not being processed

**Solutions**:
```bash
# Check worker logs
docker compose logs celery_worker

# Verify RabbitMQ is running
docker ps | grep rabbitmq

# Check task queue
docker compose exec rabbitmq rabbitmqctl list_queues

# Restart worker
docker compose restart celery_worker
```

### Issue 4: Port Already in Use

**Symptoms**: `Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use`

**Solutions**:
```bash
# Find process using the port
netstat -ano | findstr :8000

# Kill the process (Windows)
taskkill /PID <process_id> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Issue 5: Encryption Key Error

**Symptoms**: `ImproperlyConfigured: FIELD_ENCRYPTION_KEY defined incorrectly`

**Solutions**:
```bash
# Generate new Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Update .env.docker with the generated key
FIELD_ENCRYPTION_KEY=<generated_key>

# Restart containers
docker compose restart
```

---

## Performance Optimization

### Resource Limits

Add resource constraints to `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Celery Worker Scaling

Scale Celery workers horizontally:

```bash
# Run 3 worker instances
docker compose up -d --scale celery_worker=3
```

### Database Performance

```bash
# Monitor MySQL performance
docker compose exec db mysql -u root -p -e "SHOW PROCESSLIST;"

# Check slow queries
docker compose exec db mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query_log';"
```

---

## Production Deployment Considerations

### Security Enhancements

1. **Change default credentials**
   - RabbitMQ: guest/guest
   - MySQL: root password
   - Django SECRET_KEY

2. **Enable HTTPS**
   - Add nginx reverse proxy
   - Configure SSL certificates
   - Update CORS settings

3. **Disable debug mode**
   ```env
   DEBUG=False
   ```

4. **Use secrets management**
   - Docker secrets
   - Environment variable encryption
   - Key vault integration

### High Availability

1. **Database replication**
   - MySQL master-slave setup
   - Automatic failover

2. **Load balancing**
   - Multiple web containers
   - Nginx load balancer

3. **Persistent storage**
   - External volume mounts
   - Backup strategy

### Monitoring

1. **Container health checks**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/api/"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

2. **Logging aggregation**
   - Centralized logging
   - Log rotation
   - Error tracking (Sentry)

3. **Performance monitoring**
   - Prometheus + Grafana
   - Application Performance Monitoring (APM)

---

## Deployment Evidence

### Container Status Screenshot

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Expected Output**:
```
NAMES                                    STATUS          PORTS
apnsimmanagementapi-flower-1            Up 2 hours      0.0.0.0:5555->5555/tcp
apnsimmanagementapi-celery_worker-1     Up 2 hours      
apnsimmanagementapi-web-1               Up 2 hours      0.0.0.0:8000->8000/tcp
apnsimmanagementapi-rabbitmq-1          Up 2 hours      0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
apnsimmanagementapi-db-1                Up 2 hours      0.0.0.0:3307->3306/tcp
```

### Network Configuration

```bash
docker network inspect apnsimmanagementapi_default
```

Shows all containers connected to the same network for inter-container communication.

---

## Conclusion

The Wholesale APN & SIM Management API is fully containerized using Docker and Docker Compose, providing:

✅ **Microservices Architecture** - Separate containers for each component  
✅ **Easy Deployment** - Single command to start entire stack  
✅ **Development Parity** - Same environment for dev and production  
✅ **Scalability** - Can scale workers independently  
✅ **Isolation** - Each service runs in isolated container  
✅ **Persistence** - Database data persists across restarts  

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-05  
**Project**: Wholesale APN & SIM Management API (NQF Level 5 Capstone)

---

*This deployment guide provides comprehensive documentation of the Docker containerization for academic and professional evaluation purposes.*
