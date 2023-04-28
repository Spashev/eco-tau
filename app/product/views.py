from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions, status, filters, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.http import Http404

from product.serializers import ProductListSerializer, ProductCreateSerializer, BookingSerializer, \
    ProductLikeSerializer, ProductRetrieveSerializer, UploadFilesSerializer, CategorySerializer
from product.models import Product, Booking, Image, Category
from product.filters import ProductFilterSet, BookingFilterSet
from product.permissions import ProductPermissions
from utils.permissions import AuthorOrReadOnly

class ProductViewSet(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
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
                return Response({'uploaded_files': 'Неверный формат файла'}, status=status.HTTP_400_BAD_REQUEST)
        for file in uploaded_files:
            Image.objects.create(product=product, original=file, thumbnail=file)

        return Response({'message': 'Images saved success'}, status=status.HTTP_200_OK)


class ProductRetrieveViewSet(
    generics.GenericAPIView
):
    serializer_class = ProductRetrieveSerializer
    authentication_classes = []
    permission_classes = []
    filterset_class = ProductFilterSet
    queryset = Product.active_objects.all()

    def get(self, request, pk, *args, **kwargs):
        try:
            product = Product.active_objects.get(pk=pk)
            serializer = ProductRetrieveSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise Http404


class ProductListViewSet(
    generics.GenericAPIView
):
    serializer_class = ProductListSerializer
    authentication_classes = []
    permission_classes = []
    filterset_class = ProductFilterSet
    queryset = Product.active_objects.all()

    def get(self, request, *args, **kwargs):
        products = Product.active_objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 25
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)



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


class CategoryViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Category.objects.all()
