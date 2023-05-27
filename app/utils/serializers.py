from rest_framework import serializers

from account.models import User
from product.models import Image

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'full_name'
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
            'width',
            'height',
            'mimetype'
        )


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)
