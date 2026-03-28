#!/usr/bin/env python3
"""
Integration test for Django backend
Tests real API calls to running backend server
"""
import requests
import json
import sys

BACKEND_URL = "http://localhost:8000"

def test_health():
    """Test backend health endpoint"""
    print("\n🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        print("   ✅ Backend is healthy!\n")
        return True
    except Exception as e:
        print(f"   ❌ Health check failed: {e}\n")
        return False

def test_instagram_download():
    """Test Instagram video download"""
    print("🎬 Testing Instagram download...")
    url = "https://www.instagram.com/reel/DWNRNQYk_qM/?igsh=ZGd1OHQxeHBmaTRy"
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/test-download/",
            json={
                'url': url,
                'platform': 'instagram',
                'direct': True
            },
            timeout=60
        )
        
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Success: {data.get('success')}")
        
        if data.get('success'):
            print(f"   Download URL: {data['download_url'][:100]}...")
            print(f"   Filename: {data['filename']}")
            print(f"   Platform: {data['platform']}")
            print("   ✅ Instagram download test PASSED!\n")
            return True, data['download_url']
        else:
            print(f"   ❌ Download failed: {data.get('error')}\n")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}\n")
        return False, None

def test_video_download(video_url):
    """Download actual video from CDN URL"""
    print("📥 Testing video file download from CDN...")
    
    try:
        response = requests.get(video_url, timeout=60)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Size: {len(response.content) / 1024:.2f} KB")
        
        assert response.status_code == 200
        assert len(response.content) > 100 * 1024  # > 100KB
        
        # Check not HTML
        content = response.content[:100].decode('utf-8', errors='ignore').lower()
        assert '<!doctype html' not in content
        assert '<html' not in content
        
        print("   ✅ Video download test PASSED!")
        print(f"   Valid video file: {len(response.content) / 1024 / 1024:.2f} MB\n")
        return True
        
    except Exception as e:
        print(f"   ❌ Video download failed: {e}\n")
        return False

def main():
    print("=" * 60)
    print("BACKEND INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("❌ Backend is not running!")
        print("   Run: docker compose up -d")
        sys.exit(1)
    
    # Test 2: Instagram download
    success, video_url = test_instagram_download()
    if not success:
        print("❌ Instagram extraction failed")
        sys.exit(1)
    
    # Test 3: Download video
    if not test_video_download(video_url):
        print("❌ Video download failed")
        sys.exit(1)
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nBackend is working correctly!")
    print("Flutter app can now call: http://10.0.2.2:8000/api/test-download/")

if __name__ == "__main__":
    main()
