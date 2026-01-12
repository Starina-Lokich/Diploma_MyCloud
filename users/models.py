from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import Sum


class CustomUser(AbstractUser):
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z][a-zA-Z0-9]{3,19}$',
        message="Логин должен начинаться с буквы, содержать только латинские буквы и цифры, длина от 4 до 20 символов."
    )

    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[username_validator]
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=False)
    is_admin = models.BooleanField(default=False)
    storage_path = models.CharField(max_length=255, blank=True)

    # Переопределите поля groups и user_permissions с уникальными related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user',
    )

    def save(self, *args, **kwargs):
        # Сохраняем объект, чтобы получить ID
        super().save(*args, **kwargs)

        if not self.storage_path:
            self.storage_path = f"user_{self.id}/"
            super().save(update_fields=['storage_path'])

    @property
    def formatted_total_file_size(self):
        total_size = self.files.aggregate(total=Sum('size'))['total'] or 0

        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024:
                return f"{total_size:.2f} {unit}"
            total_size /= 1024
        return f"{total_size:.2f} TB"

    def __str__(self):
        return f"{self.username} ({'admin' if self.is_admin else 'user'})"