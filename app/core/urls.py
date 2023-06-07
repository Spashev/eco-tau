from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import admin_view

from core.swagger import swagger_patterns

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('swagger/', include(swagger_patterns)),

    path('', include('admin_volt.urls')),
    path('admin/', admin_view.index, name="index"),
    path('admin/', admin.site.urls),

    path('api/v1/', include('account.urls')),
    path('api/v1/', include('product.urls')),
]
if settings.LOCAL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
