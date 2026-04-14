from django.contrib import admin
from django.urls import path,include
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import UserDeviceLinkViewSet

router = DefaultRouter()
router.register(r'user-devices', UserDeviceLinkViewSet, basename='user-device')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('api.urls')),
    path('api/', include(router.urls)),
]
