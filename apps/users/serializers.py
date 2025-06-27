from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from .models import *
from apps.nurseries.models import NurseryAssistant

class UserPasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Mot de passe trop court.") 
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'username': {'help_text': "Nom d'utilisateur", 'required': True},
            'first_name': {'help_text': "Prénom", 'required': False},
            'last_name': {'help_text': "Nom de famille", 'required': False},
            'email': {'help_text': "Email", 'required': True},
            'password': {'write_only': True, 'required': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields.pop('password', None)
            self.fields['username'].read_only = True
        else:
            self.fields['password'].required = True

class UserTypeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserType
        fields = ['id', 'user', 'contact', 'address', 'birthday', 'type']
        read_only_fields = ['id', 'type']
        extra_kwargs = {
            'contact': {'help_text': "Contact téléphonique"},
            'address': {'help_text': "Adresse physique"},
            'birthday': {'help_text': "Date de naissance"},
            'type': {'help_text': "Rôle de l'utilisateur"},
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        # user_serializer = UserSerializer(data=user_data)
        # user_serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**user_data)
        return UserType.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        if user_data:
            for attr, value in user_data.items():
                if attr == 'password':
                    continue  # protection stricte : on ignore toute tentative de modification
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate(self, data):
        if data.get('type') == 'nursery_assistant' and not isinstance(self.instance, NurseryAssistant):
            raise serializers.ValidationError(
                "Les utilisateurs de type 'nursery_assistant' doivent être créés via le modèle NurseryAssistant."
            )
        return data
