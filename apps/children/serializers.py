from rest_framework import serializers
from apps.users.serializers import UserTypeSerializer
from .models import Child


class ChildSerializer(serializers.ModelSerializer):
    parent = UserTypeSerializer(read_only=True)  # affichage uniquement, pas d’écriture

    class Meta:
        model = Child
        fields = [
            "parent",
            "id",
            "last_name",
            "first_name",
            "birthday",
            "detail",
            "joined_date",
            "existe",
        ]
        read_only_fields = ["id", "parent", "joined_date"]
        extra_kwargs = {
            "last_name": {"required": True},
            "first_name": {"required": True},
            "birthday": {"required": True},
            "detail": {"required": False},
            "existe": {"required": False},
        }

    def update(self, instance, validated_data):
        # Empêche modification du parent même si transmis par erreur
        validated_data.pop("parent", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
