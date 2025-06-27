from rest_framework import serializers
from .models import Group, Classroom
from apps.nurseries.models import Nursery, NurseryAssistant


class NestedNurseryAssistantSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = NurseryAssistant
        fields = ['id', 'full_name', 'is_manager']

    def get_full_name(self, obj):
        return f"{obj.profil.user.first_name} {obj.profil.user.last_name}"


class ClassroomSerializer(serializers.ModelSerializer):
    nursery = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="ID de la crèche propriétaire de cette salle",
    )
    assistants = NestedNurseryAssistantSerializer(
        source='nurseryassistant_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Classroom
        fields = [
            'id', 'name', 'nursery', 'capacity',
            'age_range_start', 'age_range_end',
            'nbr_children', 'existe', 'assistants'
        ]
        read_only_fields = ['id', 'assistants']
        extra_kwargs = {
            'name': {'required': True},
            'capacity': {'required': True},
            'age_range_start': {'required': True},
            'age_range_end': {'required': True},
            'nbr_children': {'required': False},
            'existe': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # En update : la crèche est figée
        if self.instance:
            self.fields['nbr_children'].required = True
        

    def validate(self, attrs):
        for attr, value in attrs.items():
            if self.instance and attr == 'nursery':
                continue
            if value in [None, '']:
                raise serializers.ValidationError({attr: f"Le champ '{attr}' est requis et ne peut pas être vide."})
        return attrs


class GroupSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="ID de la classe associée à ce groupe",
    )
    assistants = NestedNurseryAssistantSerializer(
        source='nurseryassistant_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'classroom', 'active', 'assistants']
        read_only_fields = ['id', 'assistants']
        extra_kwargs = {
            'name': {'required': True},
            'active': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['classroom'].read_only = True

    def validate(self, attrs):
        required_fields = ['name', 'classroom']
        for attr, value in attrs.items():
            if self.instance and attr == 'classroom':
                continue
            if value in [None, '']:
                raise serializers.ValidationError({attr: f"Le champ '{attr}' est requis."})
        return attrs
