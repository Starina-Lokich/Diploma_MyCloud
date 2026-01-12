from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 6:
            raise ValidationError("Пароль должен содержать минимум 6 символов")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r'\d', password):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Пароль должен содержать хотя бы один специальный символ")
    
    def get_help_text(self):
        return "Пароль должен содержать минимум 6 символов, заглавную букву, цифру и специальный символ"