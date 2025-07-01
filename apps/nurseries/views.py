from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import Nursery, NurseryAssistant, OpeningHour
from .serializers import NurserySerializer, NurseryAssistantSerializer, OpeningHourSerializer
from apps.users.models import UserType
from .filters import NurseryFilter, NurseryPagination
from django_filters import rest_framework as filters


class NurseryGetViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.AllowAny]
    queryset = Nursery.objects.filter(manager__type='nursery_manager', verified=True)
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = NurseryFilter
    pagination_class = NurseryPagination

    class BasicNurserySerializer(NurserySerializer):
        class Meta(NurserySerializer.Meta):
            fields = ['id', 'name', 'address']

    class DetailedNurserySerializer(NurserySerializer):
        class Meta(NurserySerializer.Meta):
            fields = [
                'id', 'name', 'address', 'contact_number', 'legal_status',
                'max_age', 'max_children_per_class', 'photo_exterior',
                'photo_interior', 'opening_hours', 'information'
            ]

    def get_serializer_class(self):
        if self.action == 'list':
            return self.BasicNurserySerializer
        if self.action == 'retrieve':
            return self.DetailedNurserySerializer
        return super().get_serializer_class()


class NurseryViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NurserySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Nursery.objects.all()
        return Nursery.objects.filter(manager__user=self.request.user)

    def perform_create(self, serializer):
        manager = UserType.objects.get(user=self.request.user)
        serializer.save(manager=manager)

    def perform_update(self, serializer):
        nursery = self.get_object()
        if nursery.manager.user != self.request.user:
            raise PermissionDenied("Vous ne pouvez pas modifier cette crèche.")
        serializer.save()

    @action(
        detail=True,
        methods=['post', 'put', 'patch'],
        url_path='opening-hours',
        parser_classes=[JSONParser]
    )
    def opening_hours(self, request, pk=None):
        nursery = self.get_object()
        serializer = OpeningHourSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        nursery.opening_hours.all().delete()

        for hou in serializer.validated_data:
            OpeningHour.objects.create(nursery=nursery, **hou)

        return Response(status=status.HTTP_204_NO_CONTENT)


class NurseryAssistantViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NurseryAssistantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        nursery_pk = self.kwargs.get('nursery_pk')
        return NurseryAssistant.objects.filter(nursery_id=nursery_pk)

    def perform_create(self, serializer):
        nursery_id = self.kwargs.get("nursery_pk")
        serializer.save(nursery_id=nursery_id)

    def perform_update(self, serializer):
        assistant = self.get_object()
        serializer.save()
