from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db.models import Sum
from django.shortcuts import get_object_or_404  # ДОБАВИТЬ
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import CustomUser
from .serializers import UserSerializer, UserRegisterSerializer
from django.middleware.csrf import get_token
from django.http import JsonResponse

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)  # УДАЛЕН print()
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "isAuthenticated": True,
            "user": UserSerializer(request.user).data
        })

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_queryset(self):
        if not self.request.user.is_admin:
            return CustomUser.objects.filter(id=self.request.user.id)

        return CustomUser.objects.annotate(
            total_file_size=Sum('files__size', default=0)
        ).all()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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

# ДОБАВИТЬ этот класс
class UserAdminToggleView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def patch(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        is_admin = request.data.get('is_admin')
        if is_admin is not None:
            user.is_admin = is_admin
            user.save()
        return Response(UserSerializer(user).data)