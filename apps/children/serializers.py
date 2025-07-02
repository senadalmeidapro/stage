from rest_framework import serializers
from apps.users.serializers import UserTypeSerializer
from apps.users.models import UserType
from .models import *

class ChildSerializer(serializers.ModelSerializer):
    parent = UserTypeSerializer(read_only=True)
    read_only_fields = ['id']

    class Meta:
        model = Child
        fields = ['parent', 'id', 'last_name', 'first_name', 'birthday', 'detail', 'joined_date', 'existe']
        read_only_fields = ['id', 'parent', 'joined_date']
        extra_kwargs = {
            'last_name': {'required': True},
            'first_name': {'required': True},
            'birthday': {'required': True},
            'detail': {'required': False},
            'existe': {'required': False},
        }



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('parent', None)
        self.fields['joined_date'].read_only = True
        if self.instance is not None:
            self.fields['parent_id'].read_only = True
            # self.fields['parent'].read_only = True
    

    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('parent', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


