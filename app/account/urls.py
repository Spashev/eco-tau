from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from account.views import UserViewSet, CreateManagerViewSet


router = DefaultRouter(trailing_slash=True)
router.register('users', UserViewSet, basename='users')
router.register('manager', CreateManagerViewSet, basename='manager')

urlpatterns = [
    path('users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls))
]
