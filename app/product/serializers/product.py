from rest_framework import serializers

from product.models import Product, Category, Convenience, Type, Image, Like
from product.serializers.booking import BookingSerializer

from utils.serializers import ImageSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ConvenienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convenience
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class ProductRetrieveSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    convenience = ConvenienceSerializer(many=True, read_only=True)
    type = TypeSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    bookings = BookingSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
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
            'images',
            'latitude',
            'longitude',
            'bookings',
        )


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    convenience = ConvenienceSerializer(many=True, read_only=True)
    type = TypeSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
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
            'images',
            'latitude',
            'longitude'
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
            'type'
        )

        read_only_fields = (
            'id',
        )

    def create(self, validated_data):
        category = validated_data.pop('category')
        convenience = validated_data.pop('convenience')
        product = Product.objects.create(**validated_data)
        product.category.set(category)
        product.convenience.set(convenience)

        return product


class ProductLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Like
        fields = (
            'user',
        )
