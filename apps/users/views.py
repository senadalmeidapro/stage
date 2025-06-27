from rest_framework import generics, permissions, status, mixins, viewsets
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import (
    UserPasswordUpdateSerializer,
    UserTypeSerializer,
)
from .models import UserType
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "is_staff": self.user.is_staff,
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UpdatePasswordView(generics.UpdateAPIView):
    serializer_class = UserPasswordUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save()


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserTypeSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()


class UserDetailView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserType.objects.all()

    def get_queryset(self):
        user = self.request.user
        return UserType.objects.filter(user=user).order_by('id')

    def get_object(self):
        user = self.request.user
        try:
            return UserType.objects.get(user=user)
        except UserType.DoesNotExist:
            raise NotFound(detail="Profil utilisateur introuvable.")

    def perform_update(self, serializer):
        serializer.save()
