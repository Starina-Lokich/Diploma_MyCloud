from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_admin', 'storage_path')
    search_fields = ('username', 'email')
    list_filter = ('is_admin',)
    readonly_fields = ('storage_path',)
