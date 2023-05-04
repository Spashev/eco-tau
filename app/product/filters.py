from django_filters import rest_framework as rest_filters
from product.models import Product, Booking


class ProductFilterSet(rest_filters.FilterSet):
    price_per_night = rest_filters.CharFilter(field_name='price_per_night', lookup_expr='lte')
    price_per_week = rest_filters.CharFilter(field_name='price_per_week', lookup_expr='lte')
    price_per_month = rest_filters.CharFilter(field_name='price_per_month', lookup_expr='lte')
    name = rest_filters.CharFilter(field_name='name', lookup_expr='icontains')
    address = rest_filters.CharFilter(field_name='address', lookup_expr='icontains')
    category = rest_filters.NumberFilter(field_name='category__pk')

    class Meta:
        model = Product
        fields = ['price_per_night', 'price_per_week', 'price_per_month', 'name', 'address', 'category']


class BookingFilterSet(rest_filters.FilterSet):
    start_date = rest_filters.DateTimeFilter(field_name='start_date')
    end_date = rest_filters.DateTimeFilter(field_name='end_date')
    product = rest_filters.DateTimeFilter(field_name='product__name')

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'product']
