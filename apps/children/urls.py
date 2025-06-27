from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChildViewSet

router = DefaultRouter()
# from .views import ExampleModelViewSet
router.register(r'child', ChildViewSet, basename='child')
urlpatterns = router.urls