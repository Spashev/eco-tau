from rest_framework import serializers
import logging
from product.models import Product, Category, Convenience, Type, Image, Like
from product.serializers import booking, comment

from utils.serializers import ImageSerializer

logger = logging.getLogger(__name__)


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
        )

    def get_booking(self, obj):
        bookings = obj.booking_set.filter(is_active=True)
        serializer = booking.BookingSerializer(bookings, many=True)

        return serializer.data

    def get_comments(self, obj):
        comments = obj.product_comments.all()
        serializer = comment.CommentListSerializer(comments, many=True)
        return serializer.data


class ProductListSerializer(serializers.ModelSerializer):
    type = TypeSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)

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
            'lat',
            'lng'
        )


class ProductSearchSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    owner = serializers.CharField(required=False)
    rooms_qty = serializers.IntegerField(required=False)
    guest_qty = serializers.IntegerField(required=False)
    date_start = serializers.DateField(required=False)
    date_end = serializers.DateField(required=False)

    class Meta:
        model = Product
        fields = (
            'name',
            'owner',
            'rooms_qty',
            'guest_qty',
            'date_start',
            'date_end'
        )


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
            logger.error(f'Create product error {str(e)}')


class ProductLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Like
        fields = (
            'user',
        )
