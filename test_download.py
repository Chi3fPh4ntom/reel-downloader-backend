#!/usr/bin/env python
"""
Test script for video download functionality
Run this to test download link generation without Docker
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Override to use SQLite for testing
os.environ['USE_SQLITE'] = 'True'

django.setup()

from downloader.services import test_download_sync

def test_instagram_download():
    """Test Instagram reel download"""
    test_url = "https://www.instagram.com/reel/DWXwb3IkwvL/?igsh=dnhzYzkzejlmZWh2"
    
    print("=" * 60)
    print("Testing Instagram Download")
    print("=" * 60)
    print(f"URL: {test_url}")
    print("-" * 60)
    
    result = test_download_sync(test_url, 'instagram')
    
    print("\nResult:")
    if result.get('success'):
        print("✅ SUCCESS!")
        print(f"Download URL: {result.get('download_url')}")
        print(f"Filename: {result.get('filename')}")
        print(f"Platform: {result.get('platform')}")
        print(f"File Size: {result.get('file_size', 'N/A')} bytes")
    else:
        print("❌ FAILED")
        print(f"Error: {result.get('error')}")
    
    print("=" * 60)
    return result


def test_api_endpoint():
    """Test the API endpoint directly"""
    import requests
    
    print("\n" + "=" * 60)
    print("Testing API Endpoint")
    print("=" * 60)
    
    test_url = "https://www.instagram.com/reel/DWXwb3IkwvL/?igsh=dnhzYzkzejlmZWh2"
    
    try:
        response = requests.post(
            'http://localhost:8000/api/test-download/',
            json={'url': test_url, 'platform': 'instagram'},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running. Start with: docker-compose up")
    except Exception as e:
        print(f"Error: {e}")
    
    print("=" * 60)


if __name__ == '__main__':
    print("\n🎬 Reel Downloader Backend - Test Script\n")
    
    # Run sync test
    result = test_instagram_download()
    
    # Try API test (will fail if server not running)
    print("\n💡 To test API endpoint, run: docker-compose up")
    print("   Then run this script again or use curl:\n")
    print("   curl -X POST http://localhost:8000/api/test-download/ \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"url\": \"https://www.instagram.com/reel/DWXwb3IkwvL/?igsh=dnhzYzkzejlmZWh2\"}'")
    print()
    
    # Exit with appropriate code
    sys.exit(0 if result.get('success') else 1)
