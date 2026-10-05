from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/catatan_keuangan/api/', include('account.urls')),
    path('transaction/catatan_keuangan/api/', include('transaction.urls')),

    # open schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # swagger ui
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # redoc (opsional, lebih cantik)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]