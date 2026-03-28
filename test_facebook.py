#!/usr/bin/env python
"""
Test Facebook download (should work with yt-dlp)
"""
import os
import sys
import django
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['USE_SQLITE'] = 'True'

django.setup()

from downloader.services import test_download_sync

# Test with a public Facebook video
test_url = "https://www.facebook.com/watch/?v=123456789"  # Example URL

print("=" * 60)
print("Testing Facebook Download")
print("=" * 60)
print(f"URL: {test_url}")
print("-" * 60)

result = test_download_sync(test_url, 'facebook')

print("\nResult:")
if result.get('success'):
    print("✅ SUCCESS!")
    print(f"Download URL: {result.get('download_url')}")
    print(f"Filename: {result.get('filename')}")
else:
    print("❌ FAILED")
    print(f"Error: {result.get('error')}")

print("=" * 60)
