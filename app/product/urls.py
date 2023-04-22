from django.urls import path, include
from product.views import ProductViewSet, BookingViewSet, CategoryViewSet

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter(trailing_slash=True)
router.register('products', ProductViewSet, basename='products')
router.register('booking', BookingViewSet, basename='booking')
router.register('categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('', include(router.urls))
]
