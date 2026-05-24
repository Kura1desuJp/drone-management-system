from rest_framework import viewsets, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, GroupSerializer
from drones.permissions import AdminOnlyPermission


# ============================================================
# АВТЕНТИФІКАЦІЯ
# ============================================================

class LoginView(APIView):
    """Вхід у систему. POST: { username, password }"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        if not username or not password:
            return Response(
                {'detail': 'Введіть логін та пароль.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Check inactive first — ModelBackend returns None for inactive users
        try:
            candidate = User.objects.get(username=username)
            if candidate.check_password(password) and not candidate.is_active:
                return Response(
                    {'detail': 'Обліковий запис деактивовано.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'detail': 'Невірний логін або пароль.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Вихід із системи."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Ви вийшли з системи.'}, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    Профіль поточного користувача.
    GET  — отримати дані
    PATCH — змінити email/ім'я/пароль (без зміни ролей та прав)
    """
    permission_classes = [permissions.IsAuthenticated]

    # Поля, що захищені від самостійної зміни
    _PROTECTED = {'is_staff', 'is_superuser', 'is_active', 'groups'}

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        safe_data = {k: v for k, v in request.data.items() if k not in self._PROTECTED}
        serializer = UserSerializer(request.user, data=safe_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ============================================================
# УПРАВЛІННЯ КОРИСТУВАЧАМИ ТА РОЛЯМИ (лише Адміністратор)
# ============================================================

class UserViewSet(viewsets.ModelViewSet):
    """Управління користувачами — лише Адміністратор."""
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [AdminOnlyPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']


class GroupViewSet(viewsets.ModelViewSet):
    """Управління групами/ролями — лише Адміністратор."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AdminOnlyPermission]
