from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import re


class UserSerializer(serializers.ModelSerializer):
    total_file_size = serializers.IntegerField(read_only=True)  # Сырые байты
    formatted_total_file_size = serializers.SerializerMethodField()
    file_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_admin',
            'storage_path',
            'total_file_size',
            'formatted_total_file_size',
            'file_count'
        ]
        read_only_fields = ['id', 'storage_path', 'total_file_size', 'formatted_total_file_size']

    def get_formatted_total_file_size(self, obj):
        return obj.formatted_total_file_size

    def get_total_file_size(self, obj):
        request = self.context.get('request')
        if request and request.user.is_admin:
            return obj.formatted_total_file_size(as_string=True)
        return obj.formatted_total_file_size(as_string=False)

    def get_file_count(self, obj):
        return obj.files.count()


class UserRegisterSerializer(serializers.ModelSerializer): #
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'is_admin']
        extra_kwargs = {
            'is_admin': {'default': False},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate_email(self, value):
    
        # Регулярное выражение для email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError(
                "Введите корректный email адрес"
            )
        # Проверка уникальности
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email уже используется")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Имя пользователя уже занято.")
        return value

    def validate_password(self, value):
    
        # Проверка длины
        if len(value) < 6:
            raise serializers.ValidationError("Пароль должен содержать минимум 6 символов")
        
        # Проверка заглавной буквы
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну заглавную букву")
        
        # Проверка цифры
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру")
        
        # Проверка специального символа
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы один специальный символ (!@#$%^&* и т.д.)")
        
        # Также использовать стандартную валидацию Django
        from django.contrib.auth.password_validation import validate_password
        validate_password(value)
        
        return value

    def create(self, validated_data):
        # print("Validated data:", validated_data)
        try:
            user = CustomUser.objects.create_user(
                username=validated_data['username'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                email=validated_data['email'],
                password=validated_data['password']
            )
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Ошибка создания пользователя: {str(e)}")
