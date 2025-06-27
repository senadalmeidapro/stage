from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from apps.nurseries.serializers import Nursery

# ===== FILTRES =====
class NurseryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', help_text="Recherche par nom (insensible à la casse)", field_name='name')
    address = filters.CharFilter(lookup_expr='startswith', help_text="Filtre par ville exacte", field_name='address')
    max_age = filters.NumberFilter(field_name='max_age', lookup_expr='gte', help_text="Âge maximum")

    class Meta:
        model = Nursery
        fields = ['name', 'address', 'max_age']

# ===== PAGINATION CUSTOM (optionnel) =====
class NurseryPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size' 
    max_page_size = 100 
