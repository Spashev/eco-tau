from django_filters import rest_framework as rest_filters
from product.models import Booking


class BookingFilterSet(rest_filters.FilterSet):
    start_date = rest_filters.DateTimeFilter(field_name='start_date')
    end_date = rest_filters.DateTimeFilter(field_name='end_date')
    product = rest_filters.DateTimeFilter(field_name='product__name')

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'product']
