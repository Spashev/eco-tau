from django.urls import path, include
from product.views import ProductViewSet, ProductListViewSet, ProductSearchViewSet, ProductRetrieveViewSet, \
    BookingViewSet, CategoryViewSet

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter(trailing_slash=True)
router.register('products', ProductViewSet, basename='products')
router.register('booking', BookingViewSet, basename='booking')
router.register('categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('', include(router.urls)),
    path('products', ProductListViewSet.as_view()),
    path('products/search', ProductSearchViewSet.as_view()),
    path('products/<int:pk>', ProductRetrieveViewSet.as_view()),
]
