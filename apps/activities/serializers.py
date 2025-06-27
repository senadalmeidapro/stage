from rest_framework import serializers
from .models import ClassroomActivity, Activity
from apps.classrooms.serializers import Classroom
from apps.nurseries.serializers import NurserySerializer , Nursery
from rest_framework import serializers

class ActivitySerializer(serializers.ModelSerializer):
    nursery = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="ID de la crèche propriétaire de cette activité",
    )

    class Meta:
        model = Activity
        fields = ['id', 'name', 'description', 'nursery', 'type']
        extra_kwargs = {
            'name': {'required': True},
            'description': {'required': True},
            'type': {'required': True},
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Empêcher toute modification après création
        if self.instance:
            for field in self.fields:
                self.fields[field].read_only = True

    def validate(self, attrs):
        # Validation stricte : rien ne doit être vide
        for field in ['name', 'nursery', 'type', 'description']:
            if attrs.get(field) in [None, '']:
                raise serializers.ValidationError({field: "Ce champ est obligatoire et ne peut pas être vide."})
        return attrs


class ClassroomActivitySerializer(serializers.ModelSerializer):

    activity = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="ID de l'activité"
    )

    classroom = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="ID de la salle de classe"
    )



    class Meta:
        model = ClassroomActivity
        fields = ['id', 'classroom', 'activity', 'date','start_time', 'end_time']
        extra_kwargs = {
            'classroom': {'required': True},
            'activity': {'required': True},
            'date': {'required': True},
            'start_time': {'required': True},
            'end_time': {'required': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # En update, rendre classroom et activity non modifiables
        if self.instance:
            self.fields['classroom'].read_only = True
            self.fields['activity'].read_only = True

    def validate(self, attrs):
        # Validation stricte : rien ne doit être vide
        for field in ['classroom', 'activity', 'date', 'start_time', 'end_time']:
            if self.instance and field in ['classroom', 'activity']:
                continue  # déjà en read_only
            if attrs.get(field) in [None, '']:
                raise serializers.ValidationError({field: "Ce champ est requis et ne peut pas être vide."})
        return attrs
