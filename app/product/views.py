import os
import time
from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from product.serializers import ProductListSerializer, ProductCreateSerializer, BookingSerializer, \
    ProductLikeSerializer, ProductRetrieveSerializer, UploadFilesSerializer
from product.models import Product, Booking, Image
from product.filters import ProductFilterSet, BookingFilterSet
from product.permissions import ProductPermissions
from utils.permissions import AuthorOrReadOnly

class ProductViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProductListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductPermissions)
    filterset_class = ProductFilterSet
    queryset = Product.active_objects.all()

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == 'create':
            serializer = ProductCreateSerializer
        elif self.action == 'retrieve':
            serializer = ProductRetrieveSerializer
        elif self.action == 'like':
            serializer = ProductLikeSerializer
        elif self.action == 'save_image':
            serializer = UploadFilesSerializer

        return serializer

    @action(detail=True, methods=['put'], url_path='like')
    def like(self, request, pk):
        obj = self.get_object()
        user = request.user
        likes = user.likes.filter(product=obj)
        if likes:
            likes.first().delete()
        else:
            obj.likes.create(user=user)
        like_count = obj.likes.count()

        return Response({'likes': like_count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='images')
    def save_image(self, request, pk):
        product = self.get_object()
        data = request.data
        uploaded_files = data.pop('uploaded_files')
        for file in uploaded_files:
            if file.content_type != 'image/png' and file.content_type != 'image/jpeg' \
                    and file.content_type != 'image/jpg' and file.content_type != 'image/gif':
                raise serializers.ValidationError({'uploaded_files': ['Неверный формат файла']})
        for file in uploaded_files:
            original_path = default_storage.save(f'images/original/{time.time()}.jpg', ContentFile(file.read()))
            thumbnail_path = default_storage.save(f'images/thumbnail/{time.time()}.jpg', ContentFile(file.read()))
            Image.objects.create(product=product, original=original_path, thumbnail=thumbnail_path)

        return Response({'message': 'Images saved success'}, status=status.HTTP_200_OK)


class BookingViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = BookingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_class = BookingFilterSet
    queryset = Booking.objects.all()

    def get_serializer_class(self):
        serializer = self.serializer_class

        return serializer
