from rest_framework import serializers
from product.models import Product, Category, Convenience, Type, Like, Favorites
from product.serializers import booking, comment
from django.db.models import Sum
import math

from utils.serializers import ImageSerializer, UserSerializer
from utils.logger import log_exception


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'icon'
        )


class ConvenienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convenience
        fields = (
            'id',
            'name',
            'icon',
            'parent'
        )


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class ProductRetrieveSerializer(serializers.ModelSerializer):
    convenience = ConvenienceSerializer(many=True, read_only=True)
    type = TypeSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    booking = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    owner = UserSerializer()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price_per_night',
            'price_per_week',
            'price_per_month',
            'owner',
            'rooms_qty',
            'guest_qty',
            'bed_qty',
            'bedroom_qty',
            'toilet_qty',
            'bath_qty',
            'description',
            'city',
            'address',
            'convenience',
            'type',
            'images',
            'lat',
            'lng',
            'booking',
            'comments',
            'like_count',
        )

    def get_booking(self, obj):
        bookings = obj.booking_set.all()
        serializer = booking.BookingSerializer(bookings, many=True)

        return serializer.data

    def get_comments(self, obj):
        comments = obj.product_comments.all()
        serializer = comment.CommentListSerializer(comments, many=True)
        return serializer.data


class ProductListSerializer(serializers.ModelSerializer):
    type = TypeSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    owner = UserSerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price_per_night',
            'price_per_week',
            'price_per_month',
            'owner',
            'rooms_qty',
            'guest_qty',
            'bed_qty',
            'bedroom_qty',
            'toilet_qty',
            'bath_qty',
            'description',
            'city',
            'address',
            'type',
            'images',
            'is_active',
            'rating',
            'lat',
            'lng'
        )

    def get_rating(self, obj):
        total_likes = Product.objects.aggregate(Sum('like_count'))
        return math.ceil((int(obj.like_count) / int(total_likes.get('like_count__sum'))) * 100)


class ProductCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price_per_night',
            'price_per_week',
            'price_per_month',
            'owner',
            'rooms_qty',
            'guest_qty',
            'bed_qty',
            'bedroom_qty',
            'toilet_qty',
            'bath_qty',
            'description',
            'category',
            'city',
            'address',
            'convenience',
            'type',
            'lat',
            'lng'
        )

        read_only_fields = (
            'id',
        )

    def create(self, validated_data):
        try:
            category = validated_data.pop('category')
            convenience = validated_data.pop('convenience')
            product = Product.objects.create(**validated_data)
            product.category.set(category)
            product.convenience.set(convenience)

            return product
        except Exception as e:
            log_exception(e, f'Create product error {str(e)}')


class ProductLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Like
        fields = (
            'user',
        )


class FavoritesListSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Favorites
        fields = (
            'products',
        )

    def get_products(self, obj):
        products = []
        for favorites in obj:
            product = favorites.product
            products.append(product)
        return ProductListSerializer(products, many=True).data
