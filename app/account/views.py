from datetime import datetime

from rest_framework import viewsets, mixins, permissions, status, generics, views

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
    ObtainTokenSerializer,
)
from utils.logger import log_exception
from utils.utils import has_passed_30_minutes, has_passed_2_minutes
from utils.models import generate_activation_code
from account.tasks import send_email
from account.authentication import JWTAuthentication


class ObtainTokenView(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = ObtainTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = User.objects.filter(email=email).first()
        if user is None:
            return Response({'message': 'User not found', 'detail_code': 'user_not_found'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({'message': 'User not active', 'detail_code': 'user_not_active'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if user is None or not user.check_password(password):
            return Response({'message': 'Invalid credentials', 'detail_code': 'invalid_credentials'},
                            status=status.HTTP_400_BAD_REQUEST)

        print(user, email, password)

        jwt_token = JWTAuthentication.create_jwt(user)
        create_refresh_token = JWTAuthentication.create_refresh_token(user)

        return Response({
            'access': jwt_token,
            'refresh': create_refresh_token
        })


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
        try:
            user = self.request.user
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except Exception as e:
            log_exception(e, 'Error user me')

        return Response(status=status.HTTP_404_NOT_FOUND)

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
                resend_key = f'activation_resend_{user.id}'
                activation_resend_time = cache.get(resend_key)

                resend_ty_key = f'activation_resend_try_{user.id}'
                activation_resend_try_count = cache.get(resend_ty_key)

                if activation_resend_time is None or has_passed_2_minutes(activation_resend_time):

                    if activation_resend_try_count is not None and activation_resend_try_count > 3:
                        return Response({"message": "Too many activation code resend requests, wait 1 day."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    activation_code = generate_activation_code()
                    self.set_activation_code(user.id, activation_code)
                    self.set_resend_time(user.id)
                    self.set_resend_try_count(user.id, activation_resend_try_count)

                    send_email.delay(
                        "Код активации",
                        [email],
                        'email/resend_notification.html',
                        {'text': activation_code, 'from_email': 'info@example.com'}
                    )
                else:
                    return Response({"message": "Please wait 2 minutes to resend the activation code."},
                                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_exception(e, 'Error in send_activation_code')
            return Response({"message": "Activation code error"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Activation code sended"}, status=status.HTTP_200_OK)

    def set_activation_code(self, user_id: int, activation_code) -> None:
        cache_key = f'activation_code:{user_id}'
        cache.set(cache_key, activation_code)

    def set_resend_time(self, user_id: int) -> None:
        resend_key = f'activation_resend_{user_id}'
        cache.set(resend_key, datetime.now())

    def set_resend_try_count(self, user_id: int, activation_resend_try_count) -> None:
        if activation_resend_try_count:
            resend_ty_key = f'activation_resend_try_{user_id}'
            cache.set(resend_ty_key, activation_resend_try_count + 1)
        else:
            resend_ty_key = f'activation_resend_try_{user_id}'
            cache.set(resend_ty_key, 1)
