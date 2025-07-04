import os
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Nursery, OpeningHour, NurseryAssistant
from apps.users.models import UserType
from apps.classrooms.models import Classroom, Group
from apps.users.serializers import UserTypeSerializer
from django.contrib.auth.models import User

class FileValidator:
    def __init__(self, allowed_extensions, max_size_mb):
        self.allowed_extensions = allowed_extensions
        self.max_size = max_size_mb * 1024 * 1024
    
    def __call__(self, value):
        if not value:
            return value
            
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                _(f"Format invalide. Extensions autorisées: {', '.join(self.allowed_extensions)}")
            )
        
        if value.size > self.max_size:
            raise ValidationError(
                _(f"Fichier trop volumineux. Maximum: {self.max_size/1024/1024}MB")
            )
        return value

class OpeningHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHour
        fields = ['day', 'open_time', 'close_time', 'is_closed', 'nursery']
        extra_kwargs = {
            'nursery': {'read_only': True},
            'open_time': {'required': False},
            'close_time': {'required': False}
        }

    def validate(self, attrs):
        if not attrs.get('is_closed'):
            if not attrs.get('open_time') or not attrs.get('close_time'):
                raise serializers.ValidationError(
                    "Les horaires sont obligatoires lorsque la crèche est ouverte"
                )
            if attrs['open_time'] >= attrs['close_time']:
                raise serializers.ValidationError(
                    "L'heure d'ouverture doit être avant l'heure de fermeture"
                )
        
        if attrs.get('day') is None or not 0 <= attrs['day'] <= 6:
            raise serializers.ValidationError(
                "Le jour doit être compris entre 0 (Lundi) et 6 (Dimanche)"
            )
            
        return attrs

class NurserySerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(
        source='manager',
        read_only=True
    )
    manager = UserTypeSerializer(read_only=True)
    
    agreement_document = serializers.FileField(
        required=False,
        validators=[FileValidator(['.pdf'], 10)]
    )
    id_card_document = serializers.FileField(
        required=False,
        validators=[FileValidator(['.pdf', '.jpg', '.jpeg', '.png'], 5)]
    )
    photo_exterior = serializers.ImageField(
        required=False,
        validators=[FileValidator(['.jpg', '.jpeg', '.png'], 5)]
    )
    photo_interior = serializers.ImageField(
        required=False,
        validators=[FileValidator(['.jpg', '.jpeg', '.png'], 5)]
    )
    
    opening_hours = OpeningHourSerializer(
        many=True,
        read_only=True
    )

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

    def validate_contact_number(self, value):
        if not value or len(value) < 8:
            raise serializers.ValidationError(
                "Numéro de téléphone invalide"
            )
        return value

class NurseryAssistantSerializer(serializers.ModelSerializer):
    profil_id = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.filter(type='nursery_assistant'),
        source='profil',
        write_only=True
    )
    profil = UserTypeSerializer(read_only=True)
    nursery = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = NurseryAssistant
        fields = [
            'id', 'profil', 'profil_id', 'nursery',
            'classroom', 'group', 'is_manager'
        ]
        read_only_fields = ['id', 'profil', 'nursery']

    def create(self, validated_data):
        with transaction.atomic():
            profil_data = validated_data.pop('profil', {})
            user_data = profil_data.pop('user', {})
            
            user = User.objects.create_user(**user_data)
            profil = UserType.objects.create(
                user=user,
                type='nursery_assistant',
                **profil_data
            )
            
            return NurseryAssistant.objects.create(
                profil=profil,
                **validated_data
            )

    def update(self, instance, validated_data):
        with transaction.atomic():
            profil_data = validated_data.pop('profil', {})
            user_data = profil_data.pop('user', {})
            
            if user_data:
                user = instance.profil.user
                for attr, value in user_data.items():
                    setattr(user, attr, value)
                user.save()
            
            if profil_data:
                for attr, value in profil_data.items():
                    setattr(instance.profil, attr, value)
                instance.profil.save()
            
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()
            return instance
