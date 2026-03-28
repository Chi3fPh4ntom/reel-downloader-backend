"""
Celery tasks for video downloading
"""
from celery import shared_task
from .services import download_video
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def download_video_task(self, url, platform='auto'):
    """
    Async task to download video
    """
    try:
        logger.info(f"Starting download task for URL: {url}")
        
        result = download_video(url, platform)
        
        if result.get('success'):
            logger.info(f"Download successful: {result.get('filename')}")
            return {
                'success': True,
                'download_url': result.get('download_url'),
                'filename': result.get('filename'),
                'platform': result.get('platform'),
                'file_size': result.get('file_size'),
                'expires_in_hours': 24
            }
        else:
            logger.error(f"Download failed: {result.get('error')}")
            raise Exception(result.get('error', 'Unknown download error'))
            
    except Exception as exc:
        logger.error(f"Download task error: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60)
