from django.contrib import admin
from .models import File

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'user', 'size', 'upload_date', 'last_download')
    list_filter = ('user',)
    search_fields = ('original_name', 'comment')
    readonly_fields = ('unique_name', 'public_link', 'size', 'upload_date', 'last_download')
