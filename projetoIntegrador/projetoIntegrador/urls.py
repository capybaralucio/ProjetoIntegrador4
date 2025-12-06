from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from entregas.views import (EntregaViewSet, MotoristaViewSet, ClienteViewSet, RotaViewSet, VeiculoViewSet)
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView)


router = DefaultRouter()
router.register(r'motorista', MotoristaViewSet)
router.register(r'entrega', EntregaViewSet)
router.register(r'rotas', RotaViewSet)
router.register(r'veiculos', VeiculoViewSet)
router.register(r'cliente', ClienteViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
