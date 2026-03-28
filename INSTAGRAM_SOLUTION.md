# Instagram Download Solution

## Problem

Instagram has significantly tightened their API security in 2025-2026. Public access to video URLs now requires:
- Authentication (login cookies)
- Rate limiting protection
- Browser fingerprinting bypass

## Current Status

| Method | Status | Notes |
|--------|--------|-------|
| Instaloader (public) | ❌ Blocked | Returns 401 Unauthorized |
| fastdl.app | ❌ Blocked | Returns 403 Forbidden |
| indown.io | ❌ Limited | Rate limited / blocked |
| savefrom.net | ⚠️ Intermittent | Works sometimes |
| yt-dlp | ✅ Works | For Facebook only |

## Solutions

### Option 1: User-Provided Cookies (Recommended for MVP)

Allow users to provide their Instagram session cookies:

```python
# In settings.py
INSTAGRAM_SESSIONID = config('INSTAGRAM_SESSIONID', default='')

# In services.py
L = instaloader.Instaloader()
L.load_session_from_file('username')  # or from cookie
```

**Pros:**
- Works reliably
- No external dependencies
- Free

**Cons:**
- Users need to extract cookies
- Cookies expire
- Security concerns

### Option 2: Paid API Service

Use a commercial Instagram API:

| Service | Price | Reliability |
|---------|-------|-------------|
| HikerAPI | $0.00069/req | ⭐⭐⭐⭐⭐ |
| Apify | $0.005/req | ⭐⭐⭐⭐⭐ |
| RapidAPI (various) | $10-50/mo | ⭐⭐⭐⭐ |

**Example with HikerAPI:**
```python
import requests

def download_with_hikerapi(url):
    response = requests.get(
        'https://api.hikerapi.com/v1/instagram',
        params={'url': url},
        headers={'Authorization': 'Bearer YOUR_API_KEY'}
    )
    return response.json()
```

### Option 3: Self-Hosted Browser Automation

Use Playwright/Selenium to scrape Instagram:

```python
from playwright.sync_api import sync_playwright

def scrape_instagram(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        video_url = page.evaluate('() => document.querySelector("video").src')
        return video_url
```

**Pros:**
- No API costs
- Full control

**Cons:**
- Slow (5-10 seconds per video)
- Resource intensive
- Still may get blocked

### Option 4: Hybrid Approach (Recommended for Production)

1. **Try free methods first** (savefrom, indown)
2. **Fallback to paid API** if free methods fail
3. **Cache results** to minimize API calls
4. **Rate limit** user requests

## Implementation Plan

### Phase 1: MVP (Current)
- ✅ Facebook download (yt-dlp works)
- ⚠️ Instagram: Show "Requires authentication" message
- ⚠️ Provide cookie input option for advanced users

### Phase 2: Enhanced
- Add HikerAPI integration
- Implement caching layer
- Add rate limiting

### Phase 3: Production
- Multiple API fallbacks
- User authentication system
- Premium tier for unlimited downloads

## Code Implementation

Add to `downloader/services.py`:

```python
def download_instagram_with_api(url, shortcode):
    """Use HikerAPI as fallback"""
    API_KEY = settings.HIKERAPI_KEY
    
    if not API_KEY:
        return {'success': False, 'error': 'API key not configured'}
    
    response = requests.get(
        'https://api.hikerapi.com/v1/instagram',
        params={'url': url},
        headers={'Authorization': f'Bearer {API_KEY}'},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            video_url = data['data']['video_url']
            return download_video_file(video_url, shortcode, 'instagram')
    
    return {'success': False, 'error': 'API failed'}
```

## Testing

For now, test with Facebook:
```bash
python test_facebook.py
```

Or use the test endpoint with a Facebook URL:
```bash
curl -X POST http://localhost:8000/api/test-download/ \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://www.facebook.com/watch/?v=...", "platform": "facebook"}'
```

## Recommendation

**For immediate testing:**
1. Use Facebook videos (yt-dlp works perfectly)
2. For Instagram, either:
   - Get a HikerAPI key (https://hikerapi.com)
   - Or implement cookie-based authentication

**For production:**
- Use hybrid approach with multiple fallbacks
- Budget ~$50-100/month for API costs at scale
- Implement user accounts and rate limiting
