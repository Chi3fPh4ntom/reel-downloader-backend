# Instagram Download Solution

## Problem

Instagram has significantly tightened their API security in 2025-2026. Public access to video URLs now requires:
- Authentication (login cookies)
- Rate limiting protection
- Browser fingerprinting bypass

## Current Status

| Method | Status | Notes |
|--------|--------|-------|
| parth-dl | ✅ Works | No login required, uses GraphQL extraction |
| yt-dlp | ⚠️ Fallback | Works as fallback, may require auth |
| Instaloader (public) | ❌ Blocked | Returns 401 Unauthorized |
| fastdl.app | ❌ Blocked | Returns 403 Forbidden |
| indown.io | ❌ Limited | Rate limited / blocked |
| savefrom.net | ⚠️ Intermittent | Works sometimes |

## Solution Implemented

The backend now uses **parth-dl** (primary) with **yt-dlp** (fallback) for Instagram extraction:

### Key Features

1. **Retry Logic with Exponential Backoff**
   - Up to 3 retry attempts
   - 2-second initial delay, doubling each retry
   - Automatic retry on rate limiting/network errors

2. **yt-dlp Fallback**
   - If parth-dl fails after all retries, attempts yt-dlp extraction
   - Provides detailed error messages for debugging

3. **Improved Error Handling**
   - Better error messages for production debugging
   - Specific handling for rate limiting scenarios

### Code Changes

In `downloader/services.py`:

```python
def download_instagram_video(url, download_to_server=False):
    """
    Download Instagram video using parth-dl with retry logic
    and yt-dlp fallback
    """
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        # Try parth-dl extraction
        # If it fails with retryable error, retry with backoff
        # If all parth-dl attempts fail, try yt-dlp fallback
```

## Testing

Test with Instagram reel:
```bash
python -c "
from downloader.services import download_video
result = download_video('https://www.instagram.com/reel/DWuZmPGuPwA/', 'instagram')
print(result)
"
```

Or use the API endpoint:
```bash
curl -X POST http://localhost:8000/api/test-download/ \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://www.instagram.com/reel/DWuZmPGuPwA/", "platform": "instagram"}'
```

## Troubleshooting

If Instagram extraction fails:

1. **Rate Limiting**: Instagram may be rate-limiting the server IP. Wait and retry.

2. **Network Issues**: Check server network connectivity to Instagram CDN.

3. **Private/Deleted Content**: The video may be private, deleted, or unavailable.

4. **Production vs Local**: If local works but production fails:
   - Different IP addresses may be rate-limited differently
   - Network routes may differ between environments

## Alternative Solutions (if needed)

### Option 1: User-Provided Cookies

Allow users to provide Instagram session cookies:

```python
# In settings.py
INSTAGRAM_SESSIONID = config('INSTAGRAM_SESSIONID', default='')
```

### Option 2: Paid API Service

Use a commercial Instagram API:

| Service | Price | Reliability |
|---------|-------|-------------|
| HikerAPI | $0.00069/req | ⭐⭐⭐⭐⭐ |
| Apify | $0.005/req | ⭐⭐⭐⭐⭐ |

### Option 3: Browser Automation

Use Playwright/Selenium for scraping (slower but more reliable).

## Dependencies

- `parth-dl==1.0.1` - Primary Instagram extractor
- `yt-dlp==2026.3.17` - Facebook extractor + Instagram fallback
- `requests==2.31.0` - HTTP library

## Recommendation

**Current approach (parth-dl + yt-dlp fallback) should work for most cases.**

If you encounter persistent issues:
1. Check server IP is not blocked by Instagram
2. Consider adding a paid API as fallback
3. Implement caching to reduce extraction frequency