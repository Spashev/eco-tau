from rest_framework import serializers

from account.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
        )
        read_only_fields = ['id']

