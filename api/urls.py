"""
API URL Configuration
"""
from django.urls import path
from .views import DownloadView, TaskStatusView, TestDownloadView, HealthView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('download/', DownloadView.as_view(), name='download'),
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    path('test-download/', TestDownloadView.as_view(), name='test-download'),
]
