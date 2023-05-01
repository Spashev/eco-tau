from rest_framework import serializers
from product.models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            'start_date',
            'end_date'
        )
