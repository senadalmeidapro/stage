# serializers.py

from rest_framework import serializers
from .models import Nursery, OpeningHour, NurseryAssistant
from apps.users.models import UserType
from apps.classrooms.models import Classroom, Group
from apps.users.serializers import UserTypeSerializer
from django.contrib.auth.models import User
from django.db import transaction


class OpeningHourSerializer(serializers.ModelSerializer):
    nursery = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OpeningHour
        fields = ['day', 'open_time', 'close_time', 'is_closed', 'nursery']

    def validate(self, attrs):
        # Si la crèche n'est pas fermée, open_time et close_time sont obligatoires
        if not attrs.get('is_closed'):
            if attrs.get('open_time') is None or attrs.get('close_time') is None:
                raise serializers.ValidationError(
                    "Horaires et fermeture obligatoires si le jour n'est pas fermé."
                )
            if attrs['open_time'] >= attrs['close_time']:
                raise serializers.ValidationError(
                    "L'heure d'ouverture doit être antérieure à l'heure de fermeture."
                )
        # jour entre 0 et 6
        day = attrs.get('day')
        if day is None or not (0 <= day <= 6):
            raise serializers.ValidationError(
                "Le jour doit être un entier entre 0 (Lundi) et 6 (Dimanche)."
            )
        return attrs


class NurserySerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(read_only=True, source='manager')
    manager = UserTypeSerializer(read_only=True)

    agreement_document = serializers.FileField(required=False)
    id_card_document = serializers.FileField(required=False)
    photo_exterior    = serializers.ImageField(required=False)
    photo_interior    = serializers.ImageField(required=False)

    # on expose en GET, mais la création initiale ne l'utilise pas
    opening_hours = OpeningHourSerializer(many=True, read_only=True)

    class Meta:
        model = Nursery
        fields = [
            'id', 'name', 'address', 'contact_number', 'information',
            'max_age', 'max_children_per_class', 'legal_status',
            'agreement_document', 'id_card_document',
            'photo_exterior', 'photo_interior',
            'verified', 'manager_id', 'manager',
            'opening_hours'
        ]
        read_only_fields = ['id', 'verified', 'manager_id', 'manager']


class NurseryAssistantSerializer(serializers.ModelSerializer):
    profil_id = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.filter(type='nursery_assistant'),
        source='profil', read_only=False, write_only=True
    )
    profil = UserTypeSerializer(read_only=True)
    nursery = serializers.PrimaryKeyRelatedField(read_only=True)
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(), required=False, allow_null=True
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = NurseryAssistant
        fields = [
            'id', 'profil', 'profil_id', 'nursery',
            'classroom', 'group', 'is_manager'
        ]
        read_only_fields = ['id', 'profil', 'nursery']


    def create(self, validated_data):
        # la logique existante pour créer user + UserType + assistant
        profil_data = self.initial_data.get('profil')
        user_data = profil_data.pop('user', None)
        user = User.objects.create_user(**user_data)
        profil = UserType(user=user, **profil_data)
        profil._bypass_check = True
        profil.save()
        assistant = NurseryAssistant.objects.create(
            profil=profil,
            **{k: v for k, v in validated_data.items() if k != 'profil'}
        )
        return assistant


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
