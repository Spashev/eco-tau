from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.swagger import swagger_patterns

API_PREFIX = 'api/v1/'

urlpatterns = [
    path('swagger/', include(swagger_patterns)),

    path('admin/', admin.site.urls),

    path(API_PREFIX, include('account.urls')),
    path(API_PREFIX, include('product.urls')),
]

if settings.LOCAL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
if settings.SILK:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]
