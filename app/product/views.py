from rest_framework import viewsets, mixins, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination

from product.serializers import ProductListSerializer, ProductCreateSerializer, BookingSerializer, \
    ProductLikeSerializer, ProductRetrieveSerializer, UploadFilesSerializer, CategorySerializer, \
    CommentSerializer, FavoritesListSerializer
from product.models import Product, Booking, Image, Category, Comment, Favorites
from product.filters import BookingFilterSet
from product.permissions import ProductPermissions, CommentPermissions, ProductPreviewPermissions
from utils.logger import log_exception
from account.authentication import JWTAuthentication

category = openapi.Parameter('category', openapi.IN_QUERY, description="Category", type=openapi.TYPE_INTEGER)
start_date = openapi.Parameter('start_date', openapi.IN_QUERY, description="Date start", type=openapi.FORMAT_DATE)
end_date = openapi.Parameter('end_date', openapi.IN_QUERY, description="Date end", type=openapi.FORMAT_DATE)
guests_count = openapi.Parameter('guests_count', openapi.IN_QUERY, description="Guests total counts",
                                 type=openapi.TYPE_INTEGER)
min_price = openapi.Parameter('min_price', openapi.IN_QUERY, description="Min price", type=openapi.TYPE_INTEGER)
max_price = openapi.Parameter('max_price', openapi.IN_QUERY, description="Max price", type=openapi.TYPE_INTEGER)
rooms_qty = openapi.Parameter('rooms_qty', openapi.IN_QUERY, description="Rooms total counts",
                              type=openapi.TYPE_INTEGER)
type = openapi.Parameter('type', openapi.IN_QUERY, description="House type", type=openapi.TYPE_INTEGER)
toilet_qty = openapi.Parameter('toilet_qty', openapi.IN_QUERY, description="Toilet total counts",
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
    queryset = Product.with_related.all()

    def get(self, request, pk):
        try:
            product = Product.with_related.get(pk=pk)
            jwt = JWTAuthentication()
            user = jwt.authenticate(request)
            user_id = None
            if user is not None:
                user_id = user[0].id
            serializer = ProductRetrieveSerializer(product, context={'user_id': user_id})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Product details {str(e)}')
            raise Http404


class ProductListByFilterViewSet(
    generics.GenericAPIView
):
    authentication_classes = []
    permission_classes = []
    serializer_class = ProductListSerializer
    allowed_methods = ["GET"]
    queryset = Product.with_related.all()
    pagination_class = None

    @swagger_auto_schema(
        manual_parameters=[min_price, max_price, start_date, end_date, guests_count, rooms_qty, toilet_qty, category,
                           type, limit, offset])
    def get(self, request):
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        guests_count = request.GET.get('guests_count', 1)
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        rooms_qty = request.GET.get('rooms_qty', None)
        toilet_qty = request.GET.get('toilet_qty', None)
        category = request.GET.get('category', None)
        product_type = request.GET.get('type', None)
        offset = request.GET.get('offset', None)

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

        if rooms_qty is not None:
            q &= Q(rooms_qty__gte=rooms_qty)

        if toilet_qty is not None:
            q &= Q(toilet_qty__gte=toilet_qty)

        if category is not None:
            q &= Q(category__pk=category)

        if product_type is not None:
            q &= Q(type__pk=product_type)

        queryset = Product.with_related.filter(q)
        paginator = LimitOffsetPagination()
        paginator.page_size = offset if offset else 25
        result_page = paginator.paginate_queryset(queryset, request)
        try:
            jwt = JWTAuthentication()
            user = jwt.authenticate(request)
            user_id = None
            if user is not None:
                user_id = user[0].id
            serializer = ProductListSerializer(result_page, context={'user_id': user_id}, many=True)
        except Exception as e:
            log_exception(e, f'Product list error {str(e)}')
            raise Http404

        return paginator.get_paginated_response(serializer.data)


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
    queryset = Category.objects.all()
