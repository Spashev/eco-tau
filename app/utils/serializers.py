from rest_framework import serializers

from account.models import User
from product.models import Image

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
        )
        read_only_fields = ['id']


class ImageSerializer(serializers.ModelSerializer):
    original = serializers.ImageField(read_only=True)
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Image
        fields = (
            'original',
            'thumbnail',
        )
