# Reel Downloader Backend

Production-ready Django backend for downloading Instagram and Facebook videos.

## Features

- 🎬 Instagram Reel/Post downloading (via instaloader)
- 📹 Facebook Video downloading (via yt-dlp)
- 🐳 Dockerized deployment
- ⚡ Async task processing with Celery
- 🔒 Secure download links with expiry
- 📊 REST API for Flutter app integration

## Quick Start

### Development (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run server
python manage.py runserver
```

### Production (With Docker)

```bash
# Build and start all services
docker-compose up --build

# Access API at http://localhost:8000
```

## API Endpoints

### Health Check
```bash
GET /api/health/
```

### Request Download
```bash
POST /api/download/
Content-Type: application/json

{
  "url": "https://www.instagram.com/reel/...",
  "platform": "auto"  // auto, instagram, facebook
}

Response:
{
  "status": "processing",
  "task_id": "abc123",
  "status_url": "/api/task-status/abc123/"
}
```

### Check Task Status
```bash
GET /api/task-status/<task_id>/

Response:
{
  "state": "SUCCESS",
  "download_url": "/media/downloads/video.mp4",
  "filename": "video.mp4",
  "expires_in_hours": 24
}
```

### Test Download (Sync)
```bash
POST /api/test-download/
Content-Type: application/json

{
  "url": "https://www.instagram.com/reel/...",
  "platform": "instagram"
}

Response:
{
  "success": true,
  "download_url": "/media/downloads/video.mp4",
  "filename": "video.mp4"
}
```

## Testing

```bash
# Run test script
python test_download.py

# Test with Instagram URL
python test_download.py
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Flutter App │────▶│ Django API   │────▶│ Celery       │
│             │     │ (Gunicorn)   │     │ Workers      │
└─────────────┘     └──────────────┘     └──────────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐     ┌──────────────┐
                    │ PostgreSQL   │     │ Redis        │
                    │ (Database)   │     │ (Broker)     │
                    └──────────────┘     └──────────────┘
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DEBUG | True | Debug mode |
| SECRET_KEY | (required) | Django secret key |
| DB_NAME | reel_downloader | Database name |
| DB_USER | postgres | Database user |
| DB_PASSWORD | postgres | Database password |
| DB_HOST | db | Database host |
| CELERY_BROKER_URL | redis://redis:6379/0 | Redis broker URL |

## Supported Platforms

- ✅ Instagram (Reels, Posts, IGTV)
- ✅ Facebook (Videos, Reels)
- 🔄 More platforms coming soon

## License

MIT
