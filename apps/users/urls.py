from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserDetailView, UpdatePasswordView, UserCreateView, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'profil', UserDetailView, basename='user-profil')

urlpatterns = [
    path('mot-de-passe/', UpdatePasswordView.as_view(), name='update-password'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
]

# On concatène proprement les URLs du router DRF
urlpatterns += router.urls
