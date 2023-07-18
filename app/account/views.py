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
)
from utils.logger import log_exception


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
            cache_key = f'activation_code:{user.id}'
            activation_code = cache.get(cache_key)

            if activation_code and code == activation_code:
                user.is_active = True
                user.save()
                return Response({"message": "User activated"}, status=status.HTTP_200_OK)
        return Response({"message": "Activation code error"}, status=status.HTTP_400_BAD_REQUEST)
