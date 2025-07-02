from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from apps.users.models import UserType
from .models import Child
from .serializers import ChildSerializer

class ChildViewSet(viewsets.ModelViewSet):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Accès total pour le staff
            return Child.objects.select_related('parent__user')
        # Pour les parents, seulement leurs enfants actifs
        return Child.objects.filter(parent__user=user, existe=True).select_related('parent__user')

    def perform_create(self, serializer):
        profil = UserType.objects.get(user=self.request.user)
        if profil.type != 'parent':
            raise PermissionDenied("Seul un parent peut inscrire un enfant")
        # Injection automatique du parent lié à l'utilisateur connecté
        serializer.save(parent=profil)

    def perform_update(self, serializer):
        child = self.get_object()
        user = self.request.user
        if child.parent.user != user:
            raise PermissionDenied("Vous ne pouvez pas modifier les données de cet enfant.")
        serializer.save()
