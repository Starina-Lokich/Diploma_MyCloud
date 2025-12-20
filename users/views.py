from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import CustomUser
from .serializers import UserSerializer, UserRegisterSerializer
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .permissions import IsAdminUser
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})


# @method_decorator(ensure_csrf_cookie, name='dispatch')
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            res = Response(UserSerializer(user).data)
            print("Serialized data:", res)
            return res
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)  # Уничтожаем сессию
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "isAuthenticated": True,
            "user": UserSerializer(request.user).data
        })

class UserViewSet(viewsets.ModelViewSet): #
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs): #
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_queryset(self):
        # Для обычных пользователей возвращаем только их профиль без подсчета
        if not self.request.user.is_admin:
            return CustomUser.objects.filter(id=self.request.user.id)

        # Для администраторов добавляем аннотацию total_file_size
        return CustomUser.objects.annotate(
            total_file_size=Sum('files__size', default=0)  # default=0 для пользователей без файлов
        ).all()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Request ", request.data)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)

            return Response({
                'user': UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "is_admin": request.user.is_admin
        })
