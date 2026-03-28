# Backend Deployment Guide - Free Tier Hosting

**For:** ReelDownloader Django Backend  
**Requirements:** Docker support, 512MB+ RAM, Python 3.11+

---

## 🎯 Best Free Tier Options (2026)

### 1. **Render** ⭐ RECOMMENDED
- ✅ Free PostgreSQL database included
- ✅ 750 hours/month free (enough for 1 service)
- ✅ Auto-deploy from GitHub
- ✅ Docker support
- ✅ SSL included
- ❌ Sleeps after 15 min inactivity (wakes on request)

**Limits:**
- RAM: 512MB
- CPU: 0.5 vCPU
- Storage: 500MB (ephemeral)
- Database: 1GB PostgreSQL (free tier)

---

### 2. **Railway**
- ✅ $5 free credit/month (enough for small app)
- ✅ PostgreSQL included
- ✅ Docker support
- ✅ Auto-deploy from GitHub
- ✅ No sleep
- ❌ More complex pricing after free credit

**Limits:**
- RAM: 512MB
- CPU: 1 vCPU
- Storage: 5GB
- Usage-based pricing

---

### 3. **Fly.io**
- ✅ 3 free VMs (256MB each)
- ✅ PostgreSQL included
- ✅ Docker support
- ✅ Global edge locations
- ❌ Requires credit card
- ❌ More complex setup

**Limits:**
- RAM: 256MB per VM
- CPU: Shared CPU
- Storage: 3GB persistent
- 3 VMs free

---

### 4. **Oracle Cloud Free Tier**
- ✅ 4 ARM cores + 24GB RAM (always free!)
- ✅ PostgreSQL self-hosted
- ✅ Docker support
- ✅ No sleep
- ❌ Requires credit card verification
- ❌ More setup work

**Limits:**
- RAM: 24GB (ARM instances)
- CPU: 4 OCPU (ARM)
- Storage: 200GB
- Most generous free tier

---

## 📋 Pre-Deployment Checklist

### 1. **Update Backend Configuration**

**File:** `.env`
```env
# Production settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,*.render.com,*.railway.app

# Database (use DATABASE_URL from hosting provider)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com

# Celery (Redis)
CELERY_BROKER_URL=redis://redis-host:6379/0
CELERY_RESULT_BACKEND=redis://redis-host:6379/0
```

---

### 2. **Update Dockerfile for Production**

**File:** `Dockerfile`
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "core.wsgi:application"]
```

---

### 3. **Update docker-compose.yml**

**File:** `docker-compose.prod.yml`
```yaml
version: '3.8'

services:
  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn --bind 0.0.0.0:8000 --workers 2 core.wsgi:application"
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: reel_downloader
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  celery:
    build: .
    command: celery -A core worker --loglevel=info
    env_file: .env
    depends_on:
      - web
      - redis

volumes:
  postgres_data:
  redis_data:
```

---

## 🚀 Deployment Guides

### Option 1: Render (Easiest) ⭐

**Step 1: Push to GitHub**
```bash
cd /home/openclaw/Projects/reel_downloader_backend
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/reel-downloader-backend.git
git push -u origin main
```

**Step 2: Create Render Account**
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"

**Step 3: Configure Web Service**
```
Name: reel-downloader-backend
Region: Choose closest to you
Branch: main
Root Directory: (leave blank)
Runtime: Docker
Build Command: (leave blank)
Start Command: (leave blank - uses Dockerfile)
```

**Step 4: Environment Variables**
```
DEBUG=False
SECRET_KEY=<generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
ALLOWED_HOSTS=*
USE_SQLITE=False
DATABASE_URL=<from Render PostgreSQL>
CELERY_BROKER_URL=<from Render Redis or use SQLite backend>
```

**Step 5: Create PostgreSQL Database**
1. New + → PostgreSQL
2. Name: reel-downloader-db
3. Database URL will be auto-injected

**Step 6: Deploy**
1. Click "Create Web Service"
2. Wait for build (~5 minutes)
3. App will be live at: `https://reel-downloader-backend.onrender.com`

**Step 7: Update Flutter App**
```dart
// lib/providers/download_provider.dart
const String _backendBaseUrl = 'https://reel-downloader-backend.onrender.com';
```

**Cost:** $0 (free tier)  
**Setup Time:** ~15 minutes

---

### Option 2: Railway

**Step 1: Push to GitHub** (same as Render)

**Step 2: Create Railway Account**
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"

**Step 3: Configure**
1. Select your repo
2. Railway auto-detects Dockerfile
3. Click "Deploy"

**Step 4: Add PostgreSQL**
1. Click "New" → "Database" → "PostgreSQL"
2. Railway auto-injects `DATABASE_URL`

**Step 5: Add Redis** (optional for Celery)
1. Click "New" → "Redis"
2. Railway auto-injects `REDIS_URL`

**Step 6: Environment Variables**
```
DEBUG=False
SECRET_KEY=<generate secret key>
ALLOWED_HOSTS=*
```

**Step 7: Deploy**
1. Click "Deploy"
2. Wait for build
3. App live at: `https://your-app.up.railway.app`

**Cost:** $0 with $5 free credit  
**Setup Time:** ~10 minutes

---

### Option 3: Fly.io

**Step 1: Install Fly CLI**
```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

**Step 2: Create App**
```bash
cd /home/openclaw/Projects/reel_downloader_backend
fly launch --name reel-downloader-backend
```

**Step 3: Configure**
```
Would you like to copy its configuration to the new app? Yes
App Name: reel-downloader-backend
Select region: Choose closest
```

**Step 4: Add PostgreSQL**
```bash
fly pg create --name reel-downloader-db
fly postgres attach --app reel-downloader-backend reel-downloader-db
```

**Step 5: Deploy**
```bash
fly deploy
```

**Step 6: Set Secrets**
```bash
fly secrets set SECRET_KEY=<your-secret-key>
fly secrets set DEBUG=False
```

**Cost:** $0 (3 free VMs)  
**Setup Time:** ~20 minutes

---

### Option 4: Oracle Cloud Free Tier (Most Powerful)

**Step 1: Create Account**
1. Go to https://oracle.com/cloud/free
2. Sign up (requires credit card)
3. Verify identity

**Step 2: Create VM Instance**
1. Console → Compute → Instances
2. Create Instance
3. Configuration:
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.A1.Flex (4 OCPU, 24GB RAM)
   - Networking: Assign public IP

**Step 3: SSH into VM**
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<your-ip>
```

**Step 4: Install Docker**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
exit
# SSH again
```

**Step 5: Deploy**
```bash
git clone https://github.com/yourusername/reel-downloader-backend.git
cd reel-downloader-backend
docker compose -f docker-compose.prod.yml up -d
```

**Step 6: Configure Nginx** (reverse proxy)
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/reeldownloader
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/reeldownloader /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Cost:** $0 (always free)  
**Setup Time:** ~45 minutes  
**Best for:** Production, high traffic

---

## 🔧 Post-Deployment Steps

### 1. **Test Backend API**
```bash
curl https://your-backend-url.com/api/health/
# Should return: {"status": "healthy", "service": "reel-downloader-api"}
```

### 2. **Test Download**
```bash
curl -X POST https://your-backend-url.com/api/test-download/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.instagram.com/reel/DWNRNQYk_qM/",
    "platform": "instagram",
    "direct": true
  }'
```

### 3. **Update Flutter App**
```dart
// lib/providers/download_provider.dart
const String _backendBaseUrl = 'https://your-backend-url.com';
```

### 4. **Rebuild APK**
```bash
cd /home/openclaw/Projects/reel_downloader_app
flutter clean
flutter pub get
flutter build apk --release
```

---

## 📊 Comparison Table

| Feature | Render | Railway | Fly.io | Oracle |
|---------|--------|---------|--------|--------|
| **Ease** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **RAM** | 512MB | 512MB | 256MB | 24GB |
| **CPU** | 0.5 vCPU | 1 vCPU | Shared | 4 OCPU |
| **Storage** | 500MB | 5GB | 3GB | 200GB |
| **Database** | 1GB PG | Included | Included | Self-hosted |
| **Sleep** | Yes (15min) | No | No | No |
| **Setup Time** | 15min | 10min | 20min | 45min |
| **Best For** | Testing | Small apps | Edge apps | Production |

---

## 🎯 Recommendation

**For Testing/Development:**
→ **Render** (easiest, free PostgreSQL)

**For Small Production:**
→ **Railway** (no sleep, simple pricing)

**For High Traffic:**
→ **Oracle Cloud** (24GB RAM free!)

---

## 🐛 Troubleshooting

### "App won't start"
```bash
# Check logs
docker logs <container-id>

# Check environment variables
docker exec -it <container-id> env
```

### "Database connection failed"
```bash
# Check DATABASE_URL format
postgresql://user:password@host:5432/dbname

# Test connection
psql $DATABASE_URL
```

### "CORS errors"
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
]
```

---

## 📚 Resources

- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Fly.io Docs](https://fly.io/docs)
- [Oracle Cloud Free Tier](https://oracle.com/cloud/free)

---

**Need help with a specific provider?** Let me know which one you choose! 🚀
