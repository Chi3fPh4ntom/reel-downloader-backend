# Instagram Proxy Configuration

Instagram blocks server IPs (like Render.com, AWS, etc.) from scraping. Using proxies allows you to bypass these IP-based blocks by routing requests through residential or datacenter IPs that Instagram hasn't blocked.

## How It Works

The downloader uses proxy rotation:
1. First tries without a proxy (direct connection)
2. If blocked, rotates through configured proxies until one works
3. Supports both authenticated (user:pass) and open proxies

## Quick Setup

### Option 1: Environment Variable (Recommended for Production)

Set the `INSTAGRAM_PROXIES` environment variable with comma-separated proxy URLs:

```bash
# Single proxy
INSTAGRAM_PROXIES=http://user:pass@proxy-ip:port

# Multiple proxies (rotation)
INSTAGRAM_PROXIES=http://user1:pass1@proxy1:port,http://user2:pass2@proxy2:port,http://user3:pass3@proxy3:port
```

**For Render.com:**
1. Go to your Render dashboard → reel-downloader-backend
2. Click **Environment**
3. Add new variable: `INSTAGRAM_PROXIES`
4. Value: Your proxy URLs (comma-separated)
5. Click **Save Changes** (triggers redeploy)

### Option 2: proxies.txt File (Development)

Create a `proxies.txt` file in the project root:

```
# One proxy per line, comments start with #
http://user:pass@proxy1.example.com:8080
http://user:pass@proxy2.example.com:8080
192.168.1.100:3128
```

## Proxy Format

Supported formats:
- `http://user:pass@ip:port` - Authenticated HTTP proxy
- `https://user:pass@ip:port` - Authenticated HTTPS proxy
- `http://ip:port` - Open HTTP proxy (no auth)
- `ip:port` - Assumes HTTP protocol

## Proxy Providers

### Free Proxies (Testing Only)

Free proxies are unreliable and slow, but useful for testing:

| Source | URL | Notes |
|--------|-----|-------|
| ProxyScrape | https://www.proxyscrape.com/free-proxy-list | HTTP/HTTPS, updates frequently |
| Spys.one | https://spys.one/en/http-proxy-list/ | Filter by country, anonymity |
| Geonode | https://proxylist.geonode.com/api/proxy-list | JSON API available |

**Warning:** Free proxies often don't work with Instagram and may be slow/unreliable.

### Paid Proxies (Production Recommended)

For production use, invest in quality proxies:

#### Residential Proxies (Best Success Rate)

| Provider | Price | Features |
|----------|-------|----------|
| **Bright Data** | ~$15/GB | Best quality, 72M+ IPs, excellent for Instagram |
| **Smartproxy** | ~$12/GB | Good balance of price/quality |
| **IPRoyal** | ~$7/GB | Budget residential, decent success rate |

#### Datacenter Proxies (Cheaper, Higher Block Risk)

| Provider | Price | Features |
|----------|-------|----------|
| **Webshare** | ~$3/month | 100 proxies, fast, some may be blocked |
| **Proxy-Cheap** | ~$5/month | Unlimited bandwidth, mixed success |
| **ScraperAPI** | ~$29/month | API-based, handles rotation automatically |

#### Scraping APIs (Easiest, Most Expensive)

These handle everything (proxies, rotation, CAPTCHAs):

| Provider | Price | Notes |
|----------|-------|-------|
| **ScraperAPI** | $29/month | Instagram-specific endpoints |
| **ZenRows** | $29/month | Good documentation |
| **ScrapingBee** | $49/month | Headless browser support |

## Testing Proxies

Test your proxies before deploying:

```bash
# Test single proxy
curl -x http://user:pass@proxy-ip:port https://www.instagram.com -I

# Should return HTTP 200 or 301/302
# If you get 403/429, the proxy IP is blocked
```

## Troubleshooting

### "All extraction methods failed"
- Proxy IPs may all be blocked by Instagram
- Try adding more proxies to the rotation
- Consider switching to residential proxies

### "Connection timeout"
- Proxy server may be down
- Check proxy credentials (user:pass)
- Verify proxy port is correct

### "Proxy authentication required"
- Missing or incorrect username/password
- Format should be: `http://user:pass@ip:port`

### Works locally but not on Render
- Render.com IPs are heavily blocked
- You MUST use proxies on Render
- Add proxies via Environment variables

## Best Practices

1. **Use multiple proxies** - Rotation increases success rate
2. **Residential > Datacenter** - Residential IPs are less likely to be blocked
3. **Monitor success rate** - Track which proxies work best
4. **Rotate regularly** - Don't overuse single proxy IPs
5. **Keep backups** - Have extra proxies ready

## Example Configuration

**Render.com Environment Variables:**
```
INSTAGRAM_PROXIES=http://user1:pass1@proxy1.smartproxy.com:10000,http://user2:pass2@proxy2.smartproxy.com:10001,http://user3:pass3@proxy3.smartproxy.com:10002
```

**docker-compose.yml:**
```yaml
services:
  web:
    environment:
      - INSTAGRAM_PROXIES=http://user:pass@proxy-ip:port
```

## Cost Estimates

| Usage Level | Proxy Type | Monthly Cost |
|-------------|------------|--------------|
| Light (< 100/day) | Webshare datacenter | ~$5 |
| Medium (< 500/day) | Smartproxy residential | ~$75 |
| Heavy (> 1000/day) | Bright Data residential | ~$300+ |

## Security Notes

- Never commit proxy credentials to version control
- Use environment variables for sensitive data
- Add `proxies.txt` to `.gitignore`
- Rotate proxy credentials periodically
