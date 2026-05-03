from django.contrib import admin
from django.urls import path,include
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import UserDeviceLinkViewSet,BiometricReadingViewSet

router = DefaultRouter()
router.register(r'user-devices', UserDeviceLinkViewSet, basename='user-device')
router.register(r"biometric",BiometricReadingViewSet,basename="biometric")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('api.urls')),
    path('api/', include(router.urls)),
]
