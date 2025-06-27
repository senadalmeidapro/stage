"""
URL configuration for stage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# Import the core app's URLs
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/client/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/client/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/client/token/verify/', TokenVerifyView.as_view(), name='token_verify'), 
    # Include the core app URLs
    # path('api/client/core/', include('apps.core.urls')),
    # path('api/client/classrooms/', include('apps.classrooms.urls')),
    path('api/client/', include('apps.nurseries.urls')),
    path('api/client/', include('apps.children.urls')),
    # path('api/client/activities/', include('apps.activities.urls')),
     # path('api/client/subscriptions/', include('apps.subscriptions.urls')),
    path('api/client/', include('apps.users.urls')),
]
