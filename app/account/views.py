from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
from account.models import User
from account.serializers import (
    ListUserSerializer,
    CreateUserSerializer,
    ResetPasswordSerializer,
    UpdateUserSerializer
)


logger = logging.getLogger(__name__)

class UserViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    filterset_fields = ['email']

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == 'create':
            serializer = CreateUserSerializer
        elif self.action == 'reset_password':
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
            logger.error(f'Failed to reset password {str(e)}')
