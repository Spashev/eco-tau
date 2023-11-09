from django.urls import path, include
from product.views import (
    ProductViewSet,
    ProductRetrieveViewSet,
    BookingViewSet,
    CategoryViewSet,
    CommentViewSet,
    ProductPreviewViewSet,
    FavoritesViewSet,
    ProductListByFilterViewSet,
    TypeViewSet,
    ConvenienceViewSet
)

from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=True)
router.register('products', ProductViewSet, basename='products')
router.register('preview', ProductPreviewViewSet, basename='preview')
router.register('booking', BookingViewSet, basename='booking')
router.register('categories', CategoryViewSet, basename='categories')
router.register('comments', CommentViewSet, basename='comments')
router.register('conveniences', ConvenienceViewSet, basename='conveniences')
router.register('types', TypeViewSet, basename='types')

urlpatterns = [
    path('', include(router.urls)),
    path('products/get', ProductListByFilterViewSet.as_view()),
    path('products/<int:pk>', ProductRetrieveViewSet.as_view()),
    path('favorite/products', FavoritesViewSet.as_view()),
]
