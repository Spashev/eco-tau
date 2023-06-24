from django_filters import rest_framework as rest_filters
import django_filters
from product.models import Product, Booking


class ProductFilterSet(rest_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    rooms_qty = rest_filters.CharFilter(field_name='rooms_qty', lookup_expr='lte')
    toilet_qty = rest_filters.CharFilter(field_name='toilet_qty', lookup_expr='lte')
    type = rest_filters.CharFilter(field_name='type__pk')
    category = rest_filters.NumberFilter(field_name='category__pk')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'rooms_qty', 'type', 'toilet_qty',  'category']


class BookingFilterSet(rest_filters.FilterSet):
    start_date = rest_filters.DateTimeFilter(field_name='start_date')
    end_date = rest_filters.DateTimeFilter(field_name='end_date')
    product = rest_filters.DateTimeFilter(field_name='product__name')

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'product']
