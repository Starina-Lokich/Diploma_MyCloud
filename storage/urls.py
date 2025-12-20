from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    FileViewSet,
    FileUploadView,
    FileDownloadView,
    PublicFileDownloadView,
    FileUpdateView,
    FilePreviewView,
)

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/<uuid:pk>/download/', FileDownloadView.as_view(), name='file-download'),
    path('files/<uuid:pk>/preview/', FilePreviewView.as_view(), name='file-preview'),
    path('files/<uuid:pk>/update/', FileUpdateView.as_view(), name='file-update'),
    path('public/<uuid:public_link>/', PublicFileDownloadView.as_view(), name='public-file-download'),
] + router.urls
