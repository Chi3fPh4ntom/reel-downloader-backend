"""
API Views for Reel Downloader
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from downloader.tasks import download_video_task
from downloader.services import test_download_sync
import logging

logger = logging.getLogger(__name__)


class DownloadView(APIView):
    """
    API endpoint to request video download.
    Accepts Instagram/Facebook URL and returns download link.
    """
    
    def post(self, request):
        url = request.data.get('url')
        platform = request.data.get('platform', 'auto')  # auto, instagram, facebook
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return Response(
                {'error': 'Invalid URL format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Queue the download task
            task = download_video_task.delay(url, platform)
            
            return Response({
                'status': 'processing',
                'task_id': task.id,
                'message': 'Download initiated. Use task_id to check status.',
                'status_url': f'/api/task-status/{task.id}/'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return Response(
                {'error': f'Failed to initiate download: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskStatusView(APIView):
    """
    Check the status of a download task.
    """
    
    def get(self, request, task_id):
        from celery.result import AsyncResult
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            return Response({
                'task_id': task_id,
                'state': 'PENDING',
                'message': 'Task is waiting to be processed'
            })
        elif task_result.state == 'STARTED':
            return Response({
                'task_id': task_id,
                'state': 'STARTED',
                'message': 'Task is being processed'
            })
        elif task_result.state == 'SUCCESS':
            return Response({
                'task_id': task_id,
                'state': 'SUCCESS',
                'download_url': task_result.result.get('download_url'),
                'filename': task_result.result.get('filename'),
                'platform': task_result.result.get('platform'),
                'expires_in_hours': task_result.result.get('expires_in_hours', 24)
            })
        elif task_result.state == 'FAILURE':
            return Response({
                'task_id': task_id,
                'state': 'FAILURE',
                'error': str(task_result.result)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'task_id': task_id,
                'state': task_result.state
            })


class TestDownloadView(APIView):
    """
    Synchronous test endpoint for immediate download link generation.
    Use this for testing without Celery.
    
    Request body:
    - url: Video URL (Instagram or Facebook)
    - platform: auto, instagram, or facebook (default: instagram)
    - direct: true/false (default: true) - If true, returns direct CDN URL
                                      If false, downloads to server first
    """
    
    def post(self, request):
        url = request.data.get('url')
        platform = request.data.get('platform', 'instagram')
        direct = request.data.get('direct', True)  # Default to direct URL
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # direct=True means return CDN URL (don't download to server)
            # direct=False means download to server first
            download_to_server = not direct
            result = test_download_sync(url, platform, download_to_server)
            
            if result.get('success'):
                response_data = {
                    'success': True,
                    'download_url': result.get('download_url'),
                    'filename': result.get('filename'),
                    'platform': result.get('platform'),
                    'direct_url': result.get('direct_url', direct),
                }
                
                if result.get('direct_url'):
                    response_data['message'] = 'Direct download URL - App should download from this URL'
                    response_data['note'] = 'This URL may expire after some time. Download immediately.'
                else:
                    response_data['message'] = 'File downloaded to server'
                    response_data['file_size'] = result.get('file_size')
                    response_data['expires_in_hours'] = 24
                
                return Response(response_data)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Test download error: {str(e)}")
            return Response(
                {'error': f'Test download failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthView(APIView):
    """
    Health check endpoint.
    """
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'reel-downloader-api'
        })
