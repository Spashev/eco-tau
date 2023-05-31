from rest_framework import viewsets, mixins, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from drf_yasg import openapi
from django.db.models import Q

from product.serializers import ProductListSerializer, ProductCreateSerializer, BookingSerializer, \
    ProductLikeSerializer, ProductRetrieveSerializer, UploadFilesSerializer, CategorySerializer, \
    ProductSearchSerializer, CommentSerializer, FavoritesListSerializer
from product.models import Product, Booking, Image, Category, Comment, Favorites
from product.filters import BookingFilterSet, ProductFilterSet
from product.permissions import ProductPermissions, CommentPermissions, ProductPreviewPermissions
from utils.logger import log_exception

category = openapi.Parameter('category', openapi.IN_QUERY, description="Category", type=openapi.TYPE_INTEGER)


class ProductViewSet(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProductListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductPermissions)
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
        try:
            obj = self.get_object()
            user = request.user
            likes = user.likes.filter(product=obj)
            if likes:
                likes.first().delete()
                return Response({'message': 'Product like removed.'}, status=status.HTTP_200_OK)
            else:
                obj.likes.create(user=user)

            return Response({'message': 'Product liked.'}, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Product like error {str(e)}')
            raise Http404

    @action(detail=True, methods=['post'], url_path='images')
    def save_image(self, request, pk):
        try:
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
        except Exception as e:
            log_exception(e, f'Save image error {str(e)}')
            raise Http404


class ProductRetrieveViewSet(
    generics.GenericAPIView
):
    serializer_class = ProductRetrieveSerializer
    authentication_classes = []
    permission_classes = []
    queryset = Product.active_objects.all()

    def get(self, request, pk, *args, **kwargs):
        try:
            product = Product.active_objects.get(pk=pk)
            serializer = ProductRetrieveSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Product details {str(e)}')
            raise Http404


class ProductListViewSet(
    generics.ListAPIView,
    generics.GenericAPIView
):
    serializer_class = ProductListSerializer
    authentication_classes = []
    permission_classes = []
    filterset_class = ProductFilterSet
    filterset_fields = ('price_per_night', 'price_per_week', 'price_per_month', 'name', 'address', 'category')
    queryset = Product.active_objects.prefetch_related('booking_set').all()


class ProductSearchViewSet(
    generics.GenericAPIView
):
    serializer_class = ProductSearchSerializer
    authentication_classes = []
    permission_classes = []
    queryset = Product.active_objects.prefetch_related('booking_set')

    def post(self, request):
        try:
            queryset = self.get_queryset()
            name = request.data.get('name', None)
            owner = request.data.get('owner', None)
            rooms_qty = request.data.get('rooms_qty', None)
            guest_qty = request.data.get('guest_qty', None)
            date_start = request.data.get('date_start', None)
            date_end = request.data.get('date_end', None)
            if name:
                queryset = queryset.filter(name=name)
            if owner:
                queryset = queryset.filter(owner=owner)
            if rooms_qty:
                queryset = queryset.filter(rooms_qty=rooms_qty)
            if guest_qty:
                queryset = queryset.filter(guest_qty=guest_qty)
            if date_start and date_end:
                booking_products_id = Booking.objects.filter(
                    Q(start_date__range=(date_start, date_end)) | Q(end_date__range=(date_start, date_end))
                    | (Q(start_date__gt=date_start) & Q(end_date__lt=date_start))
                    | (Q(start_date__gt=date_end) & Q(end_date__lt=date_end))
                    | (Q(start_date__lt=date_start) & Q(start_date__gt=date_end) & Q(end_date__lt=date_end))
                    | (Q(end_date__lt=date_end) & Q(start_date__gt=date_start) & Q(end_date__lt=date_start))
                ).values_list(
                    'product__id', flat=True)
                queryset = queryset.exclude(id__in=booking_products_id)
            paginator = PageNumberPagination()
            paginator.page_size = 25
            result = paginator.paginate_queryset(queryset, request)
            serializer = ProductRetrieveSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            log_exception(e, f'Search error {str(e)}')
            raise Http404


class ProductPreviewViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProductListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductPreviewPermissions)
    queryset = Product.objects.all()


class FavoritesViewSet(
    generics.GenericAPIView
):
    serializer_class = FavoritesListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Favorites.objects.all()

    def get(self, request):
        try:
            user = request.user
            favorites = user.favorites.all()
            serializer = FavoritesListSerializer(favorites)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Product not found {str(e)}')
            raise Http404


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, CommentPermissions)


class BookingViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticatedOrReadOnly)
    serializer_class = BookingSerializer
    filterset_class = BookingFilterSet
    queryset = Booking.objects.all()

    def get_serializer_class(self):
        serializer = self.serializer_class

        return serializer


class CategoryViewSet(
    generics.ListAPIView,
    viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
