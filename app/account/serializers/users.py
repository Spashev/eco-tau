from django.db.models import Q
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account import RoleType, RoleClientManagerType
from account.models import User
from utils.serializers import ChoiceField


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'full_name',
            'phone_number',
        )
        read_only_fields = ['id']


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = ChoiceField(choices=RoleClientManagerType)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'password',
            'role'
        )
        read_only_fields = ['id']

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data.pop('role') if validated_data.get('role', None) else RoleType.CLIENT
        if role == RoleType.MANAGER:
            instance: User = User.objects.create_user(**validated_data, role=role, is_staff=True)
            instance.role = RoleType.MANAGER
        else:
            instance: User = User.objects.create_user(**validated_data, role=role)
            instance.role = RoleType.CLIENT
        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'is_active',
        )
        read_only_fields = ['id']


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        if instance := User.objects.filter(Q(email=email) | Q(email=email)).first():
            attrs['instance'] = instance
            return attrs
        raise ValidationError({'email': 'User with given login/email does not exist'})

    def save(self, **kwargs):
        instance: User = self.validated_data.get('instance')
        instance.reset_password()
        return instance
