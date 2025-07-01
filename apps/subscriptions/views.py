from rest_framework import viewsets, status
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from apps.users.models import UserType
from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer, MySubscriptionSerializer

class PlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des plans d’abonnement.
    Accessible uniquement aux utilisateurs authentifiés.
    Filtre les plans actifs liés à une crèche donnée (nursery_pk dans l’URL).
    """
    serializer_class = PlanSerializer
    
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            # Pour GET, HEAD, OPTIONS → autorise tout le monde
            permission_classes = [AllowAny]
        else:
            # Pour POST, PUT, PATCH, DELETE → seulement les authentifiés
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        nursery_id = self.kwargs.get("nursery_pk")
        return Plan.objects.filter(is_active=True, nursery_id=nursery_id)

    def perform_create(self, serializer):
        nursery_id = self.kwargs.get("nursery_pk")
        serializer.save(nursery_id=nursery_id)

    def perform_update(self, serializer):
        serializer.save()


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les abonnements parentaux à un plan.
    Chaque abonnement est lié à un parent (UserType)
    et peut inclure plusieurs enfants via des SubscriptionDetail.
    """
    queryset = Subscription.objects.select_related('plan', 'parent').prefetch_related('details')
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            parent = UserType.objects.get(user=self.request.user, type='parent')
            return self.queryset.filter(parent=parent)
        except UserType.DoesNotExist:
            return Subscription.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        plan_id = self.kwargs.get('plans_pk')
        plan = get_object_or_404(Plan, id=plan_id)

        try:
            parent = UserType.objects.get(user=self.request.user, type='parent')
        except UserType.DoesNotExist:
            raise ValidationError("Vous n’avez pas de compte parent associé.")

        serializer.save(parent=parent, plan=plan)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class MySubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vue pour récupérer les abonnements du parent connecté,
    avec tous les détails associés récursivement.
    """
    serializer_class = MySubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            parent = UserType.objects.get(user=user, type='parent')
        except UserType.DoesNotExist:
            return Subscription.objects.none()
        return Subscription.objects.filter(parent=parent, details__child__existe=True, plan__is_active=True).prefetch_related(
            'details__child', 'details__classroom', 'details__group', 'plan'
        )
