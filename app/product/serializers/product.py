from datetime import datetime, timedelta

from rest_framework import serializers

from product.models import Product, Category, Convenience, Type, Like, Favorites
from product.serializers import booking, comment
from django.db.models import Q

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
    bookings = booking.BookingSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    owner = UserSerializer()
    is_favorite = serializers.SerializerMethodField()

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
            'bookings',
            'comments',
            'like_count',
            'rating',
            'is_favorite',
        )

    def get_comments(self, obj):
        comments = obj.product_comments.all()
        serializer = comment.CommentListSerializer(comments, many=True)
        return serializer.data

    def to_representation(self, instance):
        current_date = datetime.now().date()
        start_date = current_date.replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        filtered_bookings = instance.booking_set.filter(
            Q(start_date__range=(start_date, end_date)) |
            Q(end_date__range=(start_date, end_date))
        )
        serialized_bookings = booking.BookingSerializer(filtered_bookings, many=True).data

        representation = super().to_representation(instance)
        representation['bookings'] = serialized_bookings
        return representation

    def get_is_favorite(self, obj):
        user_id = self.context.get('user_id')
        if user_id:
            if obj.likes.filter(user_id=user_id).first():
                return True
        return False


class ProductListSerializer(serializers.ModelSerializer):
    type = TypeSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    owner = UserSerializer()
    is_favorite = serializers.SerializerMethodField()

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
            'is_favorite',
            'rating',
            'lat',
            'lng'
        )

    def get_is_favorite(self, obj):
        user_id = self.context.get('user_id')
        if user_id:
            if obj.likes.filter(user_id=user_id).first():
                return True
        return False


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
        user_id = self.context.get('user_id')
        for favorites in obj:
            product = favorites.product
            products.append(product)
        return ProductListSerializer(products, many=True, context={'user_id': user_id}).data


class ProductByDateSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    min_price = serializers.IntegerField(required=False)
    max_price = serializers.IntegerField(required=False)
    rooms_qty = serializers.IntegerField(required=False)
    type = serializers.IntegerField(required=False)
    toilet_qty = serializers.IntegerField(required=False)
    category = serializers.IntegerField(required=False)