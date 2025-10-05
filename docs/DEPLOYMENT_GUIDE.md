# 🚀 Deployment Guide

## 📋 Table of Contents
1. [Deployment Options](#deployment-options)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Cloud Platforms](#cloud-platforms)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Deployment Options

### Quick Comparison

| Option | Best For | Difficulty | Cost |
|--------|----------|------------|------|
| Local Development | Testing, Development | Easy | Free |
| Docker | Consistency, Portability | Medium | Free |
| VPS (DigitalOcean, AWS) | Production | Medium | $5-20/mo |
| Heroku | Quick Deploy | Easy | $7+/mo |
| Railway | Modern Deploy | Easy | $5+/mo |
| Render | Free Tier | Easy | Free tier |

---

## 💻 Local Development

### Prerequisites
```bash
# Required
Python 3.9+
pip (Python package manager)

# Optional
Git
Visual Studio Code
```

### Setup Steps

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/BackendStudentManagement.git
cd BackendStudentManagement
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run Application
```bash
# Using Python directly
python scripts/run.py

# Using PowerShell script
.\scripts\start.ps1

# Using setup script
.\scripts\setup.bat  # Windows
./scripts/setup.sh   # Mac/Linux
```

#### 5. Access Application
```
API: http://localhost:8001
Swagger UI: http://localhost:8001/docs
ReDoc: http://localhost:8001/redoc
```

---

## 🐳 Docker Deployment

### Using Existing Dockerfile

#### 1. Build Image
```bash
docker build -t student-management:latest .
```

#### 2. Run Container
```bash
docker run -d \
  --name student-api \
  -p 8001:8001 \
  -v $(pwd)/students.db:/app/students.db \
  -v $(pwd)/logs:/app/logs \
  student-management:latest
```

#### 3. Check Status
```bash
# View logs
docker logs student-api

# Access container
docker exec -it student-api bash

# Stop container
docker stop student-api

# Remove container
docker rm student-api
```

### Using Docker Compose

#### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: student-api
    ports:
      - "8001:8001"
    volumes:
      - ./students.db:/app/students.db
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
      - DATABASE_URL=sqlite:///./students.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: student-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
    restart: unless-stopped
```

#### Commands
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

---

## 🏭 Production Deployment

### 1. Environment Configuration

#### .env.production
```bash
# Application
APP_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8001

# Database
DATABASE_URL=postgresql://user:password@localhost/studentdb
# Or for SQLite
DATABASE_URL=sqlite:///./students.db

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/student-api/app.log
```

### 2. Production Settings

#### app/core/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_env: str = "production"
    debug: bool = False
    app_name: str = "Student Management API"
    version: str = "1.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    workers: int = 4  # CPU cores * 2 + 1
    
    # Database
    database_url: str = "sqlite:///./students.db"
    
    # Security
    secret_key: str
    allowed_hosts: list[str] = ["*"]
    
    # CORS
    cors_origins: list[str] = []
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env.production"
```

### 3. Using Gunicorn

#### Install
```bash
pip install gunicorn uvicorn[standard]
```

#### Run
```bash
# Basic
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001

# With configuration file
gunicorn -c gunicorn.conf.py app.main:app
```

#### gunicorn.conf.py
```python
import multiprocessing

# Server socket
bind = "0.0.0.0:8001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "./logs/access.log"
errorlog = "./logs/error.log"
loglevel = "info"

# Process naming
proc_name = "student-api"

# Server mechanics
daemon = False
pidfile = "./gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
```

### 4. Systemd Service (Linux)

#### /etc/systemd/system/student-api.service
```ini
[Unit]
Description=Student Management API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/student-api
Environment="PATH=/var/www/student-api/venv/bin"
ExecStart=/var/www/student-api/venv/bin/gunicorn \
    -c /var/www/student-api/gunicorn.conf.py \
    app.main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

#### Commands
```bash
# Enable and start
sudo systemctl enable student-api
sudo systemctl start student-api

# Check status
sudo systemctl status student-api

# View logs
sudo journalctl -u student-api -f

# Restart
sudo systemctl restart student-api

# Stop
sudo systemctl stop student-api
```

### 5. Nginx Reverse Proxy

#### /etc/nginx/sites-available/student-api
```nginx
upstream student_api {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Logging
    access_log /var/log/nginx/student-api-access.log;
    error_log /var/log/nginx/student-api-error.log;
    
    # Max upload size
    client_max_body_size 10M;
    
    # Proxy settings
    location / {
        proxy_pass http://student_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if any)
    location /static/ {
        alias /var/www/student-api/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        proxy_pass http://student_api/health;
        access_log off;
    }
}
```

#### Enable Site
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/student-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 6. SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured)
sudo systemctl status certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## ☁️ Cloud Platforms

### 1. Heroku

#### Procfile
```
web: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

#### Commands
```bash
# Login
heroku login

# Create app
heroku create student-management-api

# Add PostgreSQL (optional)
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Scale
heroku ps:scale web=1
```

### 2. Railway

#### railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Commands
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up

# View logs
railway logs
```

### 3. Render

#### render.yaml
```yaml
services:
  - type: web
    name: student-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
      - key: DATABASE_URL
        fromDatabase:
          name: studentdb
          property: connectionString
    healthCheckPath: /health

databases:
  - name: studentdb
    databaseName: students
    user: studentuser
```

### 4. AWS EC2

#### Setup Steps
```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Update system
sudo apt-get update
sudo apt-get upgrade -y

# 4. Install Python and dependencies
sudo apt-get install python3.9 python3.9-venv python3-pip nginx -y

# 5. Create application directory
sudo mkdir -p /var/www/student-api
sudo chown ubuntu:ubuntu /var/www/student-api

# 6. Clone repository
cd /var/www
git clone https://github.com/yourusername/BackendStudentManagement.git student-api
cd student-api

# 7. Setup virtual environment
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 8. Configure systemd service (see above)
# 9. Configure Nginx (see above)
# 10. Setup SSL (see above)
```

---

## 📊 Monitoring

### 1. Application Monitoring

#### Health Check Endpoint
```python
# app/api/endpoints/health.py

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### 2. Log Monitoring

#### Using tail
```bash
# Follow logs
tail -f logs/api.log

# Last 100 lines
tail -n 100 logs/api.log

# Search for errors
grep "ERROR" logs/api_errors.log
```

#### Using journalctl (systemd)
```bash
# Follow service logs
sudo journalctl -u student-api -f

# Last 100 lines
sudo journalctl -u student-api -n 100

# Errors only
sudo journalctl -u student-api -p err
```

### 3. Performance Monitoring

#### Using htop
```bash
# Install
sudo apt-get install htop

# Run
htop
```

#### Using prometheus (Advanced)
```python
# Install
pip install prometheus-client

# Add to main.py
from prometheus_client import make_asgi_app

# Mount prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 8001
lsof -i :8001  # Mac/Linux
netstat -ano | findstr :8001  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

#### 2. Database Locked
```bash
# Check database connections
fuser students.db  # Linux

# Kill all Python processes
pkill python
```

#### 3. Permission Denied
```bash
# Fix file permissions
sudo chown -R $USER:$USER /var/www/student-api
sudo chmod -R 755 /var/www/student-api
```

#### 4. Module Not Found
```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt
```

#### 5. Nginx 502 Bad Gateway
```bash
# Check if application is running
sudo systemctl status student-api

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test Nginx configuration
sudo nginx -t
```

### Debug Mode

```python
# Set in .env or environment
DEBUG=true
LOG_LEVEL=DEBUG

# Run with debug logging
LOG_LEVEL=DEBUG python scripts/run.py
```

---

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Dependencies updated
- [ ] Security vulnerabilities checked
- [ ] Environment variables configured
- [ ] Database backed up

### Deployment
- [ ] Build successful
- [ ] Application starts without errors
- [ ] Health check endpoint responding
- [ ] API endpoints accessible
- [ ] Static files serving correctly
- [ ] SSL certificate valid

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Test critical user flows
- [ ] Check performance metrics
- [ ] Verify database connections
- [ ] Test backup/restore procedures
- [ ] Update documentation

---

**Last Updated**: October 5, 2025
**Version**: 1.0.0
