from django.db.models import Q
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account import RoleType, RoleClientManagerType
from account.models import User
from utils.serializers import ChoiceField
from utils.validator import validate_date_of_birth_manager, validate_date_of_birth_user


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'date_of_birth',
            'role'
        )
        read_only_fields = ['id']


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = ChoiceField(choices=RoleClientManagerType, default=RoleClientManagerType.CLIENT)
    date_of_birth = serializers.DateField(validators=[validate_date_of_birth_user])

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'date_of_birth',
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
    date_of_birth = serializers.DateField(validators=[validate_date_of_birth_user])

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'date_of_birth',
            'is_active',
        )
        read_only_fields = ['id']


class CheckEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
        )


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


class CreateManagerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(validators=[validate_date_of_birth_manager])

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'date_of_birth',
            'iin',
            'password',
        )
        read_only_fields = ['id']

    @transaction.atomic
    def create(self, validated_data):
        instance: User = User.objects.create_user(**validated_data, role=RoleType.MANAGER, is_staff=True)
        return instance


class UpdateManagerSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(validators=[validate_date_of_birth_manager])

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'date_of_birth',
            'is_active',
            'iin',
        )
        read_only_fields = ['id']


class UserActivateSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    class Meta:
        model = User
        fields = (
            'code',
            'email'
        )


class UserEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = (
            'email',
        )
