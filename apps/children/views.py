from rest_framework import viewsets, mixins, permissions
from rest_framework.exceptions import PermissionDenied
from apps.users.models import UserType
from .serializers import ChildSerializer, Child



class ChildViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Child.objects.select_related('parent__user')
        return Child.objects.filter(parent__user=user, existe=True).select_related('parent__user')
    
    def perform_create(self, serializer):
        profil = UserType.objects.get(user=self.request.user)
        if profil.type !='parent':
            return PermissionDenied("Seul un parent peut inscrire un enfant")
        serializer.save()

    def perform_update(self, serializer):
        child = self.get_object()
        user = self.request.user
        if child.parent.user != user:
            raise PermissionDenied("Vous ne pouvez pas modifier les donnée de cet enfant.")
        serializer.save()