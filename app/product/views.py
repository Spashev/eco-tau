from rest_framework import viewsets, mixins, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q, Exists, OuterRef
from rest_framework.pagination import LimitOffsetPagination

from product.serializers import ProductListSerializer, ProductCreateSerializer, BookingSerializer, \
    ProductLikeSerializer, ProductRetrieveSerializer, UploadFilesSerializer, CategorySerializer, \
    CommentSerializer, FavoritesListSerializer, TypeSerializer, ConvenienceSerializer
from product.models import Product, Booking, Image, Category, Comment, Favorites, Type, Convenience
from product.filters import BookingFilterSet
from product.permissions import ProductPermissions, CommentPermissions, ProductPreviewPermissions
from utils.logger import log_exception
from account.authentication import JWTAuthentication
from product.mixins import ProductMixins

category = openapi.Parameter('category', openapi.IN_QUERY, description="Category", type=openapi.TYPE_INTEGER)
start_date = openapi.Parameter('start_date', openapi.IN_QUERY, description="Date start", type=openapi.FORMAT_DATE)
end_date = openapi.Parameter('end_date', openapi.IN_QUERY, description="Date end", type=openapi.FORMAT_DATE)
guests_count = openapi.Parameter('guests_count', openapi.IN_QUERY, description="Guests total counts",
                                 type=openapi.TYPE_INTEGER)
min_price = openapi.Parameter('min_price', openapi.IN_QUERY, description="Min price", type=openapi.TYPE_INTEGER)
max_price = openapi.Parameter('max_price', openapi.IN_QUERY, description="Max price", type=openapi.TYPE_INTEGER)
rooms_qty = openapi.Parameter('rooms_qty', openapi.IN_QUERY, description="Rooms total counts, limit 8+",
                              type=openapi.TYPE_INTEGER)
house_type = openapi.Parameter('house_type', openapi.IN_QUERY, description="House type", type=openapi.TYPE_STRING)
toilet_qty = openapi.Parameter('toilet_qty', openapi.IN_QUERY, description="Toilet total counts, limit 4+",
                               type=openapi.TYPE_INTEGER)
bath_qty = openapi.Parameter('bath_qty', openapi.IN_QUERY, description="Bath total counts, limit 4+",
                             type=openapi.TYPE_INTEGER)
bed_qty = openapi.Parameter('bed_qty', openapi.IN_QUERY, description="Bed total counts, limit 6+",
                            type=openapi.TYPE_INTEGER)
bedroom_qty = openapi.Parameter('bedroom_qty', openapi.IN_QUERY, description="Bedroom total counts, limit 6+",
                                type=openapi.TYPE_INTEGER)
limit = openapi.Parameter('limit', openapi.IN_QUERY, description="Limit", type=openapi.TYPE_INTEGER)
offset = openapi.Parameter('offset', openapi.IN_QUERY, description="Offset", type=openapi.TYPE_INTEGER)


class ProductViewSet(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProductListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductPermissions)
    queryset = Product.with_related.all()

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
                obj.like.create(user=user)

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
    ProductMixins,
    generics.GenericAPIView
):
    serializer_class = ProductRetrieveSerializer
    authentication_classes = []
    permission_classes = []
    queryset = Product.with_related.all()

    def get(self, request, pk):
        try:
            context = self.get_serializer_context()
            user_id = context.get('user_id') if context is not None else None
            product = Product.with_related
            if user_id:
                product = product.annotate(
                    is_favorite=Exists(
                        Favorites.objects.filter(user_id=user_id, product_id=pk)
                    )
                )
            serializer = ProductRetrieveSerializer(product.get(pk=pk), context={'user_id': user_id})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Product details {str(e)}')
            raise Http404


class ProductListByFilterViewSet(
    ProductMixins,
    generics.GenericAPIView
):
    authentication_classes = []
    permission_classes = []
    serializer_class = ProductListSerializer
    allowed_methods = ["GET"]
    queryset = Product.active_related.all()
    pagination_class = None
    ROOM_LIMIT = 8
    TOILET_LIMIT = 4
    BED_LIMIT = 6
    BATH_LIMIT = 4
    BEDROOM_LIMIT = 6

    @swagger_auto_schema(
        manual_parameters=[min_price, max_price, start_date, end_date, guests_count, rooms_qty, toilet_qty, bed_qty,
                           bath_qty, bedroom_qty, category, house_type, limit, offset])
    def get(self, request):
        offset = request.GET.get('offset', None)

        q = self.get_query_filter(request)
        queryset = Product.active_related.filter(q)

        context = self.get_serializer_context()
        user_id = context.get('user_id') if context is not None else None
        if user_id:
            queryset = queryset.annotate(
                is_favorite=Exists(
                    Favorites.objects.filter(user_id=user_id, product_id=OuterRef('id'))
                )
            )

        paginator = LimitOffsetPagination()
        paginator.page_size = offset if offset else 25
        result_page = paginator.paginate_queryset(queryset, request)

        try:
            serializer = ProductListSerializer(result_page, context={
                'user_id': user_id
            }, many=True)
        except Exception as e:
            log_exception(e, f'Product list error {str(e)}')
            serializer = ProductListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def get_query_filter(self, request):
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        guests_count = request.GET.get('guests_count', 1)
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        rooms_qty = request.GET.get('rooms_qty', None)
        bed_qty = request.GET.get('bed_qty', None)
        bath_qty = request.GET.get('bath_qty', None)
        bedroom_qty = request.GET.get('bedroom_qty', None)
        toilet_qty = request.GET.get('toilet_qty', None)
        category = request.GET.get('category', None)
        house_type = request.GET.get('house_type', None)

        q = Q()

        if min_price is not None:
            q &= Q(price_per_night__gte=min_price)

        if max_price is not None:
            q &= Q(price_per_night__lte=max_price)

        if start_date is not None:
            q &= ~Q(booking__start_date__range=(start_date, end_date))

        if end_date is not None:
            q &= ~Q(booking__end_date__range=(start_date, end_date))

        if guests_count is not None:
            q &= Q(guest_qty__gte=guests_count)

        if rooms_qty is not None and int(rooms_qty) < self.ROOM_LIMIT:
            q &= Q(rooms_qty=rooms_qty)
        elif rooms_qty is not None and int(rooms_qty) == self.ROOM_LIMIT:
            q &= Q(rooms_qty__gte=rooms_qty)

        if toilet_qty is not None and int(toilet_qty) < self.TOILET_LIMIT:
            q &= Q(toilet_qty=toilet_qty)
        elif toilet_qty is not None and int(toilet_qty) >= self.TOILET_LIMIT:
            q &= Q(toilet_qty__gte=toilet_qty)

        if bed_qty is not None and int(bed_qty) < self.BED_LIMIT:
            q &= Q(bed_qty=bed_qty)
        elif bed_qty is not None and int(bed_qty) >= self.BED_LIMIT:
            q &= Q(bed_qty__gte=bed_qty)

        if bath_qty is not None and int(bath_qty) < self.BATH_LIMIT:
            q &= Q(bath_qty=bath_qty)
        elif bath_qty is not None and int(bath_qty) >= self.BATH_LIMIT:
            q &= Q(bath_qty__gte=bath_qty)

        if bedroom_qty is not None and int(bedroom_qty) < self.BEDROOM_LIMIT:
            q &= Q(bedroom_qty=bedroom_qty)
        elif bedroom_qty is not None and int(bedroom_qty) >= self.BEDROOM_LIMIT:
            q &= Q(bedroom_qty__gte=bedroom_qty)

        if category is not None:
            q &= Q(category__pk=category)

        if house_type is not None:
            q &= Q(type__pk__in=house_type.split(","))

        return q


class ProductPreviewViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProductListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductPreviewPermissions)
    queryset = Product.with_related.all()


class FavoritesViewSet(
    generics.GenericAPIView
):
    serializer_class = FavoritesListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Favorites.objects.all()

    def get(self, request):
        try:
            user_id = None
            user = request.user
            if user:
                user_id = user.id
            favorites = user.favorites.all()
            serializer = FavoritesListSerializer(favorites, context={'user_id': user_id})
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
    permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticatedOrReadOnly)
    serializer_class = BookingSerializer
    filterset_class = BookingFilterSet
    queryset = Booking.objects.all()


class CategoryViewSet(
    generics.ListAPIView,
    viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)
    pagination_class = None


class TypeViewSet(
    generics.ListAPIView,
    viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    serializer_class = TypeSerializer
    queryset = Type.objects.all()
    pagination_class = None


class ConvenienceViewSet(
    generics.ListAPIView,
    viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    serializer_class = ConvenienceSerializer
    queryset = Convenience.objects.filter(is_active=True)
    pagination_class = None
