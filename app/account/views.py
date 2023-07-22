from datetime import datetime

from rest_framework import viewsets, mixins, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache

from account import RoleType
from account.models import User
from account.serializers import (
    ListUserSerializer,
    CreateUserSerializer,
    ResetPasswordSerializer,
    UpdateUserSerializer,
    UpdateManagerSerializer,
    CreateManagerSerializer,
    CheckEmailSerializer,
    UserActivateSerializer,
    UserEmailSerializer,
)
from utils.logger import log_exception
from utils.utils import has_passed_30_minutes
from utils.models import generate_activation_code
from account.tasks import send_email

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed


class UserTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            return response
        except AuthenticationFailed as e:
            if e == 'Не найдено активной учетной записи с указанными данными':
                return Response({
                        'message': str(e),
                        'detail_code': 'account_not_active'
                    },
                    status=e.status_code
                )
            return Response({
                'message': str(e),
                'detail_code': 'user_not_found'
            }, status=e.status_code)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    filterset_fields = ['email']
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == 'reset_password':
            serializer = ResetPasswordSerializer
        elif self.action == 'update':
            serializer = UpdateUserSerializer
        elif self.action == 'partial_update':
            serializer = UpdateUserSerializer

        return serializer

    @action(methods=['GET'], detail=False, url_path='me')
    def me(self, requests, *args, **kwargs) -> Response:
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, url_path='reset-password')
    def reset_password(self, request, *args, **kwargs) -> Response:
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(status=200)
        except Exception as e:
            log_exception(e, f'Failed to reset password {str(e)}')


class UserCreateView(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CreateUserSerializer
    authentication_classes = []
    permission_classes = []


class UserCheckEmailView(
    generics.GenericAPIView
):
    serializer_class = CheckEmailSerializer
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs) -> Response:
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class CreateManagerViewSet(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.filter(role=RoleType.MANAGER)
    serializer_class = ListUserSerializer
    filterset_fields = ['email']
    permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticatedOrReadOnly)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == 'create':
            serializer = CreateManagerSerializer
        elif self.action == 'update':
            serializer = UpdateManagerSerializer
        elif self.action == 'partial_update':
            serializer = UpdateManagerSerializer

        return serializer


class UserActivateView(
    generics.GenericAPIView
):
    serializer_class = UserActivateSerializer
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs) -> Response:
        email = request.data.get('email')
        code = request.data.get('code')
        user = User.objects.filter(email=email).first()

        if user is not None:
            try_key = f'activation_try_{user.id}'
            activation_try = cache.get(try_key)

            try_time_key = f'activation_try_time_{user.id}'
            try_time = cache.get(try_time_key)

            if activation_try is None or has_passed_30_minutes(try_time):
                try_time_key = f'activation_try_time_{user.id}'
                activation_try = 1
                cache.set(try_time_key, datetime.now())

            if activation_try and activation_try > 3:
                return Response({"message": "Too many failed attempts, please try again after 30min"},
                                status=status.HTTP_200_OK)

            cache_key = f'activation_code:{user.id}'
            activation_code = cache.get(cache_key)

            if activation_code and code == activation_code:
                user.is_active = True
                user.save()
                return Response({"message": "User activated"}, status=status.HTTP_200_OK)
            activation_try += 1
            cache.set(try_key, activation_try)
        return Response({"message": "Activation code error"}, status=status.HTTP_400_BAD_REQUEST)


class ResendActivateView(
    generics.GenericAPIView
):
    serializer_class = UserEmailSerializer
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs) -> Response:
        email = request.data.get('email')

        try:
            user = User.objects.filter(email=email).first()
            if user is not None:
                cache_key = f'activation_code:{user.id}'
                activation_code = generate_activation_code()
                cache.set(cache_key, activation_code)

                send_email.delay(
                    "Код активации",
                    [email],
                    'email/resend_notification.html',
                    {'text': activation_code, 'from_email': 'info@example.com'}
                )
        except Exception as e:
            log_exception(e, 'Error in send_activation_code')
            return Response({"message": "Activation code error"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Activation code sended"}, status=status.HTTP_200_OK)
