import os
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from product.models import Product, Image
from utils.validator import MAX_FILE_SIZE
from utils.serializers import ImageSerializer


class UploadFilesSerializer(serializers.ModelSerializer):
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=MAX_FILE_SIZE, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    class Meta:
        model = Image
        fields = (
            'id',
            'uploaded_files',
        )
        read_only_fields = (
            'id',
        )


class ImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = (
            'id',
            'original',
            'thumbnail',
            'product',
        )
