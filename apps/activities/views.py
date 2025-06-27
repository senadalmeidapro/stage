from django.shortcuts import render
from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from apps.nurseries.models import Nursery, NurseryAssistant
from apps.activities.models import Activity, ClassroomActivity
from apps.activities.serializers import ActivitySerializer, ClassroomActivitySerializer

# Create your views here.


class ActivityViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(nursery__manager__user=self.request.user)

    def perform_create(self, serializer):
        try:
            nursery = Nursery.objects.get(manager__user=self.request.user)
        except Nursery.DoesNotExist:
            raise PermissionDenied("Accès refusé.")
        serializer.save()

    def perform_update(self, serializer):
        activity = self.get_object()
        user = self.request.user
        if not user.is_staff and activity.nursery.manager.user != user:
            raise PermissionDenied("Accès refusé.")
        serializer.save()


class ClassroomActivityViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ClassroomActivity.objects.all()
    serializer_class = ClassroomActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ClassroomActivity.objects.all()
        return ClassroomActivity.objects.filter(classroom__nursery__manager__user=self.request.user)

    def perform_create(self, serializer):
        try:
            assistant = NurseryAssistant.objects.get(profil__user=self.request.user, type='nursery_assistant', nursery=self.kwargs['nursery_pk'], is_manager=True)
        except NurseryAssistant.DoesNotExist:
            raise PermissionDenied("Accès refusé.")
        serializer.save()

    def perform_update(self, serializer):
        classroom_activity = self.get_object()
        user = self.request.user
        if not user.is_staff and classroom_activity.classroom.nursery.manager.user != user:
            raise PermissionDenied("Accès refusé.")
        serializer.save()