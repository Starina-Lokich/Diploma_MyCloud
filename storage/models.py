import os
import uuid
from django.db import models
from django.conf import settings
from users.models import CustomUser


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='files'
    )
    original_name = models.CharField(max_length=255)
    unique_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    last_download = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    public_link = models.UUIDField(default=uuid.uuid4, unique=True)
    file_path = models.CharField(max_length=512, default='')  # Путь относительно STORAGE_PATH

    def get_absolute_path(self):
        return os.path.join(
            settings.STORAGE_PATH,
            self.file_path)
