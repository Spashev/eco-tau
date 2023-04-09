import os
from rest_framework import serializers

from product.models import Product, Category, Convenience, Type, Image, Like
from product.serializers.booking import BookingSerializer
from utils.validator import MAX_FILE_SIZE


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


class ImageSerializer(serializers.ModelSerializer):
    original = serializers.ImageField(read_only=True)
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Image
        fields = (
            'original',
            'thumbnail',
        )

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
    images = ImageSerializer(many=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=MAX_FILE_SIZE, allow_empty_file=False, use_url=False),
        write_only=True
    )

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
            'uploaded_files',
        )

    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_files')
        category = validated_data.pop('category')
        convenience = validated_data.pop('convenience')
        product = Product.objects.create(**validated_data)
        product.category.set(category)
        product.convenience.set(convenience)
        for file in uploaded_files:
            if file.content_type != 'image/png' and file.content_type != 'image/jpeg' \
                    and file.content_type != 'image/gif' and file.content_type != 'application/pdf':
                raise serializers.ValidationError({'uploaded_files': ['Неверный формат файла']})
        i = 1
        for file in uploaded_files:
            extension = os.path.splitext(file.name)[1]
            file.name = str(i) + '_' + validated_data['name'] + extension
            Image.objects.create(product=product, original=file, thumbnail_path=file)
            i += 1

        return product


class ProductLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Like
        fields = (
            'user',
        )
