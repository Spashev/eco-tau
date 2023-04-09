from rest_framework import permissions, filters
from orders.models import Order
from utils.permissions import AuthorOrReadOnly

from django_filters import rest_framework


class OrderQuerySetMixin:
    model = Order
    queryset = Order.objects.all()
    filter_backends = (rest_framework.DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['project_code', 'user__username', 'user__email', 'status']

    def get_queryset_filter(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserQuerySetMixin:
    user_filed = 'user'
    allow_staff_view = False

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        lookup_data = {self.user_filed: user}
        qs = super().get_queryset(*args, **kwargs)
        if not self.allow_staff_view and not user.is_staff:
            return qs
        return qs.filter(**lookup_data)
