from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from entregas.auth_views import CustomAuthToken

from entregas.views import (
    EntregaViewSet, MotoristaViewSet, ClienteViewSet,
    RotaViewSet, VeiculoViewSet, rota_dashboard
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

# Router do DRF
router = DefaultRouter()
router.register(r'motorista', MotoristaViewSet)
router.register(r'entregas', EntregaViewSet, basename='entrega')
router.register(r'rotas', RotaViewSet)
router.register(r'veiculos', VeiculoViewSet)
router.register(r'cliente', ClienteViewSet)

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Endpoint de autenticação por token
    path('api/token/', CustomAuthToken.as_view(), name='api-token'),

    # Rotas da API
    path('', include(router.urls)),

    # Dashboard da rota
    path('rotas/<int:pk>/dashboard/', rota_dashboard, name='rota-dashboard'),

    # Documentação da API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
