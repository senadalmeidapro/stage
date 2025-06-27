from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .models import Classroom, Group
from apps.nurseries.models import Nursery
from .serializers import ClassroomSerializer, GroupSerializer


class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        nursery_id = self.kwargs.get('nursery_pk')
        if not nursery_id:
            raise ValidationError("L'ID de la crèche est requis.")
        return Classroom.objects.filter(nursery_id=nursery_id)

    def perform_create(self, serializer):
        nursery_id = self.kwargs.get('nursery_pk')
        try:
            nursery = Nursery.objects.get(pk=nursery_id)
        except Nursery.DoesNotExist:
            raise NotFound("Crèche non trouvée.")
        serializer.save(nursery_id=nursery_id)


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer

    def get_queryset(self):
        classroom_id = self.kwargs.get('classroom_pk')
        if not classroom_id:
            raise ValidationError("L'ID de la classe est requis.")
        return Group.objects.filter(classroom_id=classroom_id)

    def perform_create(self, serializer):
        classroom_id = self.kwargs.get('classroom_pk')
        try:
            classroom = Classroom.objects.get(pk=classroom_id)
        except Classroom.DoesNotExist:
            raise NotFound("Classe non trouvée.")
        serializer.save(classroom_id=classroom_id)
