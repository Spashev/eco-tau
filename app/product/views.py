from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from product.serializers import ProductListSerializer, ProductCreateSerializer, BookingSerializer, \
    ProductLikeSerializer, ProductRetrieveSerializer
from product.models import Product, Booking
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
    permission_classes = (ProductPermissions, permissions.IsAuthenticatedOrReadOnly)
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


class BookingViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = BookingSerializer
    permission_classes = (permissions.IsAdminUser,)
    filterset_class = BookingFilterSet
    queryset = Booking.objects.all()

    def get_serializer_class(self):
        serializer = self.serializer_class

        return serializer
