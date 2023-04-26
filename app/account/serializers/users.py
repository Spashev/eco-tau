from django.db.models import Q
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account import RoleType
from account.models import User


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

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'phone_number',
            'password'
        )
        read_only_fields = ['id']

    @transaction.atomic
    def create(self, validated_data):
        instance: User = User.objects.create_user(**validated_data, role=RoleType.CLIENT)
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

    def update(self, instance, validated_data):
        instance.update(**validated_data)

        return instance


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
