# File: storage/serializers.py
from rest_framework import serializers
from .models import File
import os
import uuid
from django.conf import settings
import re

class FileSerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField()
    user_id = serializers.PrimaryKeyRelatedField(
        source='user.id', read_only=True
    )
    username = serializers.CharField(
        source='user.username', read_only=True
    )


    class Meta:
        model = File
        fields = '__all__'
        depth = 1  # Включаем связанные объекты


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    comment = serializers.CharField(required=False)

    def validate_file(self, value):

        if not hasattr(value, 'size'):
            raise serializers.ValidationError("Некорректный объект файла")

         # Конфигурируемый размер из settings.py
        max_size_mb = getattr(settings, 'MAX_FILE_SIZE_MB', 10)  # По умолчанию 10MB
        max_size = max_size_mb * 1024 * 1024

        if value.size > max_size:
            file_size_mb = value.size / (1024 * 1024)            
            raise serializers.ValidationError(
                f"Файл слишком большой ({file_size_mb:.2f} MB). "
                f"Максимальный размер: {max_size_mb} MB"
            )

        # Проверка MIME-типа
        allowed_mime_types = getattr(settings, 'ALLOWED_MIME_TYPES', [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf',
            'text/plain', 'text/csv',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/zip',
        ])

        if hasattr(value, 'content_type') and value.content_type:
            if value.content_type not in allowed_mime_types:
                raise serializers.ValidationError(
                    f"Тип файла '{value.content_type}' не разрешен"
                )

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        uploaded_file = validated_data['file']

        if not user.storage_path:
            user.storage_path = f"user_{user.id}/"
            user.save(update_fields=['storage_path'])

        # Безопасное имя файла
        original_name = uploaded_file.name
        # Удаляем опасные символы, оставляем только буквы, цифры, точки, дефисы, подчеркивания
        safe_name = re.sub(r'[^\w\.-]', '_', original_name)
        file_ext = os.path.splitext(safe_name)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"

        # Формирование пути: user_<ID>/<UUID>.<ext>
        file_path = os.path.join(user.storage_path, unique_name)
        full_path = os.path.join(settings.STORAGE_PATH, file_path)

        # Создание директорий
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Сохранение файла
        with open(full_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Создание объекта File 
        file = File.objects.create(
            user=user,
            original_name=original_name,
            unique_name=unique_name,
            size=uploaded_file.size,
            comment=validated_data.get('comment', ''),
            public_link=uuid.uuid4(),
            file_path=file_path  # Сохраняем относительный путь
        )

        return file
