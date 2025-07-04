from rest_framework import viewsets, mixins, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.exceptions import PermissionDenied
from django_filters import rest_framework as filters
from django.core.files.storage import default_storage
from rest_framework.pagination import PageNumberPagination

from .models import Nursery, OpeningHour, NurseryAssistant
from .serializers import NurserySerializer, OpeningHourSerializer, NurseryAssistantSerializer


class NurseryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', help_text="Recherche par nom (insensible à la casse)", field_name='name')
    address = filters.CharFilter(lookup_expr='startswith', help_text="Filtre par ville exacte", field_name='address')
    max_age = filters.NumberFilter(field_name='max_age', lookup_expr='gte', help_text="Âge maximum")

    class Meta:
        model = Nursery
        fields = ['name', 'address', 'max_age']


class NurseryPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size' 
    max_page_size = 100 


class NurseryGetViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
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


class NurseryViewSet(viewsets.ModelViewSet):
    serializer_class = NurserySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser, FormParser]
    queryset = Nursery.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(manager__user=self.request.user)

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'usertype'):
            nursery = serializer.save(manager=self.request.user.usertype)
            
            # Création des horaires par défaut si fournis dans le payload initial
            if 'opening_hours' in self.request.data:
                hours_serializer = OpeningHourSerializer(
                    data=self.request.data['opening_hours'],
                    many=True,
                    context={'nursery': nursery}
                )
                hours_serializer.is_valid(raise_exception=True)
                hours_serializer.save(nursery=nursery)

    @action(
        detail=True,
        methods=['GET', 'POST', 'PUT', 'PATCH'],
        url_path='opening-hours',
        parser_classes=[JSONParser]
    )
    def opening_hours(self, request, pk=None):
        nursery = self.get_object()
        
        # Vérification des permissions
        if nursery.manager.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Permission refusée."},
                status=status.HTTP_403_FORBIDDEN
            )

        # GET - Lister les horaires existants
        if request.method == 'GET':
            hours = nursery.opening_hours.all()
            serializer = OpeningHourSerializer(hours, many=True)
            return Response(serializer.data)

        # POST/PUT/PATCH - Créer ou mettre à jour les horaires
        serializer = OpeningHourSerializer(
            data=request.data,
            many=True,
            context={'nursery': nursery}
        )
        serializer.is_valid(raise_exception=True)

        # Suppression des anciens horaires (pour PUT/PATCH)
        if request.method in ['PUT', 'PATCH']:
            nursery.opening_hours.all().delete()

        # Création des nouveaux horaires
        serializer.save(nursery=nursery)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Suppression des fichiers associés
        for field in ['agreement_document', 'id_card_document', 
                     'photo_exterior', 'photo_interior']:
            file = getattr(instance, field)
            if file and default_storage.exists(file.name):
                default_storage.delete(file.path)
        
        return super().destroy(request, *args, **kwargs)


class NurseryAssistantViewSet(viewsets.ModelViewSet):
    serializer_class = NurseryAssistantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        nursery_pk = self.kwargs.get('nursery_pk')
        return NurseryAssistant.objects.filter(nursery_id=nursery_pk)

    def perform_create(self, serializer):
        nursery_id = self.kwargs.get("nursery_pk")
        serializer.save(nursery_id=nursery_id)

    def perform_update(self, serializer):
        assistant = self.get_object()
        if assistant.nursery.manager.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied(
                "Permission refusée."
            )
        serializer.save()
