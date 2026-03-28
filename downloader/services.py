"""
Video Download Services
Handles Instagram and Facebook video downloading
Uses parth-dl for Instagram (no login required)
Returns best quality direct download URLs
"""
import os
import re
import uuid
import logging
import shutil
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


def detect_platform(url):
    """Detect platform from URL"""
    if 'instagram.com' in url:
        return 'instagram'
    elif 'facebook.com' in url or 'fb.watch' in url:
        return 'facebook'
    return 'unknown'


def select_best_quality_format(formats):
    """
    Select the best quality format from available formats
    
    Args:
        formats: List of format dicts with width, height, url, etc.
    
    Returns:
        Best format dict based on resolution
    """
    if not formats:
        return None
    
    # Sort by resolution (width * height), highest first
    def get_resolution_score(fmt):
        width = fmt.get('width', 0)
        height = fmt.get('height', 0)
        has_audio = fmt.get('has_audio', False)
        # Prefer formats with audio
        audio_bonus = 1000000 if has_audio else 0
        return (width * height) + audio_bonus
    
    sorted_formats = sorted(formats, key=get_resolution_score, reverse=True)
    return sorted_formats[0]


def download_instagram_video(url, download_to_server=False):
    """
    Download Instagram video using parth-dl (no login required)
    Always returns best quality URL
    
    Args:
        url: Instagram reel/post URL
        download_to_server: If True, download file to server and return server URL
                           If False, extract direct URL and return Instagram CDN URL
    
    Returns:
        dict with success status and download_url
    """
    try:
        from parth_dl import InstagramDownloader
        
        # Extract shortcode for filename
        match = re.search(r'(?:reel|p)/([A-Za-z0-9_-]+)', url)
        shortcode = match.group(1) if match else 'unknown'
        
        logger.info(f"Processing Instagram reel: {shortcode}")
        
        # Initialize downloader
        dl = InstagramDownloader(verbose=False)
        
        try:
            # Get video info
            info = dl.get_info(url)
            
            if not info:
                return {
                    'success': False,
                    'error': 'Could not extract video information'
                }
            
            # Extract formats and select best quality
            formats = info.get('formats', [])
            
            if not formats:
                return {
                    'success': False,
                    'error': 'No video formats available'
                }
            
            # Select best quality format
            best_format = select_best_quality_format(formats)
            video_url = best_format.get('url')
            
            if not video_url:
                return {
                    'success': False,
                    'error': 'Could not extract video URL'
                }
            
            # Get video metadata
            width = best_format.get('width', 0)
            height = best_format.get('height', 0)
            has_audio = best_format.get('has_audio', False)
            duration = info.get('duration', 0)
            
            # Determine quality label
            if height >= 1920:
                quality = '1080p'
            elif height >= 1280:
                quality = '720p'
            elif height >= 720:
                quality = '480p'
            else:
                quality = '360p'
            
            if download_to_server:
                # Download to server
                return download_video_to_server(video_url, shortcode, 'instagram')
            else:
                # Return direct URL with metadata
                return {
                    'success': True,
                    'download_url': video_url,
                    'filename': f"instagram_{shortcode}.mp4",
                    'platform': 'instagram',
                    'direct_url': True,
                    'quality': quality,
                    'resolution': f"{width}x{height}",
                    'has_audio': has_audio,
                    'duration': duration,
                    'file_size_estimate': None,  # Can't know without downloading
                    'message': f'Best quality ({quality}) direct download URL from Instagram CDN'
                }
            
        except Exception as e:
            logger.error(f"parth-dl extraction error: {str(e)}")
            return {
                'success': False,
                'error': f'Extraction failed: {str(e)}'
            }
            
    except ImportError:
        logger.error("parth-dl not installed")
        return {
            'success': False,
            'error': 'parth-dl library not installed'
        }
    except Exception as e:
        logger.error(f"Instagram download error: {str(e)}")
        return {
            'success': False,
            'error': f'Instagram download failed: {str(e)}'
        }


def download_facebook_video(url, download_to_server=False):
    """
    Download Facebook video using yt-dlp with improved configuration
    Based on: https://github.com/sh13y/Facebook-Video-Download-API
    Always returns best quality
    """
    try:
        import yt_dlp
        
        # Improved yt-dlp options for Facebook
        ydl_opts = {
            'format': 'best[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': False,  # Show warnings for debugging
            'extract_flat': False,
            'no_download': True,  # Don't download, just extract info
            'retries': 5,  # Increased retries for redirect issues
            'fragment_retries': 5,
            'ignoreerrors': False,
            'no_check_certificate': True,
            'extractaudio': False,
            # Add user agent to avoid blocking
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            # Handle redirects better
            'cookiefile': None,
            # Merge audio and video for Facebook
            'merge_output_format': 'mp4',
        }
        
        logger.info(f"Processing Facebook video: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return {
                    'success': False,
                    'error': 'No video information found'
                }
            
            # Get best format URL
            video_url = info.get('url')
            title = info.get('title', 'facebook_video')
            width = info.get('width', 0)
            height = info.get('height', 0)
            duration = info.get('duration', 0)
            
            if not video_url:
                # Try to get from formats list
                formats = info.get('formats', [])
                if formats:
                    # Sort by resolution and get best
                    best_format = max(formats, key=lambda x: x.get('height', 0) * x.get('width', 0))
                    video_url = best_format.get('url')
            
            if not video_url:
                return {
                    'success': False,
                    'error': 'Could not extract Facebook video URL. Video may be private or have restrictions.'
                }
            
            # Determine quality label
            if height >= 1920:
                quality = '1080p'
            elif height >= 1280:
                quality = '720p'
            elif height >= 720:
                quality = '480p'
            else:
                quality = '360p'
            
            # Generate safe filename
            safe_title = re.sub(r'[^\w\s-]', '', title)
            safe_title = re.sub(r'[-\s]+', '-', safe_title).strip()
            shortcode = safe_title[:50] if safe_title else 'facebook_video'
            
            if download_to_server:
                # Download to server
                return download_video_to_server(video_url, shortcode, 'facebook')
            else:
                # Return direct URL with metadata
                return {
                    'success': True,
                    'download_url': video_url,
                    'filename': f"facebook_{shortcode}.mp4",
                    'platform': 'facebook',
                    'direct_url': True,
                    'quality': quality,
                    'resolution': f"{width}x{height}",
                    'duration': duration,
                    'message': f'Best quality ({quality}) direct download URL from Facebook CDN'
                }
            
    except yt_dlp.DownloadError as e:
        error_msg = str(e)
        logger.error(f"yt-dlp DownloadError: {error_msg}")
        
        # Handle common Facebook errors
        if "redirect" in error_msg.lower() or "302" in error_msg:
            if 'fb.watch' in url:
                return {
                    'success': False,
                    'error': 'fb.watch URL needs the full Facebook URL. Please: 1) Open the video on Facebook, 2) Copy the complete facebook.com URL, 3) Try again.'
                }
            else:
                return {
                    'success': False,
                    'error': 'URL redirect issue. Please try using the direct Facebook video URL.'
                }
        elif "private" in error_msg.lower() or "not available" in error_msg.lower():
            return {
                'success': False,
                'error': 'This video is private or not available for download.'
            }
        elif "age" in error_msg.lower():
            return {
                'success': False,
                'error': 'This video has age restrictions and cannot be downloaded.'
            }
        elif "no video formats found" in error_msg.lower():
            return {
                'success': False,
                'error': 'No video formats found. The video may be private, live, or have download restrictions. Try: 1) Using a different Facebook URL format, 2) Opening the video directly on Facebook, 3) Copying the URL from the address bar.'
            }
        else:
            return {
                'success': False,
                'error': f'Facebook download failed: {error_msg}'
            }
    except Exception as e:
        logger.error(f"Facebook download error: {str(e)}")
        return {
            'success': False,
            'error': f'Facebook download failed: {str(e)}'
        }


def download_video_to_server(video_url, shortcode, platform):
    """Download video file to server storage"""
    try:
        import requests
        
        temp_dir = settings.MEDIA_ROOT / 'temp' / str(uuid.uuid4())
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{platform}_{shortcode}.mp4"
        video_path = temp_dir / filename
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(video_url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        final_dir = settings.MEDIA_ROOT / 'downloads'
        final_dir.mkdir(parents=True, exist_ok=True)
        final_path = final_dir / filename
        
        shutil.move(str(video_path), str(final_path))
        
        download_url = f"{settings.MEDIA_URL}downloads/{filename}"
        
        return {
            'success': True,
            'download_url': download_url,
            'filename': filename,
            'platform': platform,
            'file_size': os.path.getsize(final_path),
            'direct_url': False
        }
        
    except Exception as e:
        logger.error(f"Server download error: {str(e)}")
        return {
            'success': False,
            'error': f'Server download failed: {str(e)}'
        }


def download_video(url, platform='auto', download_to_server=False):
    """
    Main download function that routes to appropriate platform handler
    
    Args:
        url: Video URL (Instagram or Facebook)
        platform: auto, instagram, or facebook
        download_to_server: If True, download to server storage
                           If False, return direct CDN URL (best quality)
    """
    if platform == 'auto':
        platform = detect_platform(url)
    
    if platform == 'instagram':
        return download_instagram_video(url, download_to_server)
    elif platform == 'facebook':
        return download_facebook_video(url, download_to_server)
    else:
        return {
            'success': False,
            'error': f'Unsupported platform: {platform}'
        }


def test_download_sync(url, platform='instagram', download_to_server=False):
    """
    Synchronous test download function
    
    Args:
        url: Video URL
        platform: instagram or facebook
        download_to_server: If True, download to server; if False, return best quality direct URL
    """
    logger.info(f"Test download requested for: {url} (platform: {platform}, server: {download_to_server})")
    result = download_video(url, platform, download_to_server)
    logger.info(f"Test download result: {result}")
    return result
