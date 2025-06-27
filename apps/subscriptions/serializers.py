from rest_framework import serializers
from .models import Plan, Subscription, SubscriptionDetail
from apps.nurseries.models import Nursery
from apps.children.models import Child
from apps.users.models import UserType
from apps.classrooms.models import Classroom, Group

# -----------------------
# Serializers de base (lecture simple)
# -----------------------

class PlanSerializer(serializers.ModelSerializer):
    nursery = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'name', 'nursery', 'description', 'price', 'duration', 'created_at']
        read_only_fields = ['id', 'created_at']

class MyNurserySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nursery
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']

class MyPlanSerializer(serializers.ModelSerializer):
    nursery = MyNurserySerializer()

    class Meta:
        model = Plan
        fields = ['id', 'name', 'nursery', 'duration',]
        read_only_fields = ['id']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'first_name', 'last_name', 'birthday',]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name']


# -----------------------
# SubscriptionDetailSerializer — pour le write (POST/PUT)
# -----------------------

class SubscriptionDetailSerializer(serializers.ModelSerializer):
    child = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all())
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all(), required=False, allow_null=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False, allow_null=True)

    class Meta:
        model = SubscriptionDetail
        fields = ['id', 'child', 'classroom', 'group']
        read_only_fields = ['id']

    def validate_child(self, value):
        request = self.context.get('request')
        if request:
            try:
                parent_usertype = UserType.objects.get(user=request.user, type='parent')
            except UserType.DoesNotExist:
                raise serializers.ValidationError("Vous n’êtes pas autorisé à enregistrer un enfant.")
            if value.parent != parent_usertype:
                raise serializers.ValidationError("Cet enfant ne vous appartient pas.")
        return value


# -----------------------
# Full SubscriptionDetail (lecture complète récursive)
# -----------------------

class FullSubscriptionDetailSerializer(serializers.ModelSerializer):
    child = ChildSerializer()
    classroom = ClassroomSerializer()
    group = GroupSerializer()

    class Meta:
        model = SubscriptionDetail
        fields = ['id', 'child', 'classroom', 'group']


# -----------------------
# SubscriptionSerializer — pour création & mise à jour
# -----------------------

class SubscriptionSerializer(serializers.ModelSerializer):
    parent = serializers.HiddenField(default=serializers.CurrentUserDefault())
    plan = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(),  # nécessaire pour qu’il soit modifiable
        write_only=False,
        required=False,
        help_text="ID du plan (modifiable uniquement après création)"
    )


    # Pour le POST/PUT
    details = SubscriptionDetailSerializer(many=True, write_only=True)

    # Pour le GET
    detail_objects = FullSubscriptionDetailSerializer(many=True, read_only=True, source='details')

    class Meta:
        model = Subscription
        fields = [
            'id', 'parent', 'plan', 'start_date', 'end_date',
            'price', 'is_active', 'created_at',
            'details', 'detail_objects'
        ]
        read_only_fields = ['id', 'created_at', 'detail_objects','price']
        extra_kwargs = {
            'start_date': {'required': False, 'help_text': "Date de début de la souscription (obligatoire)"},
            'end_date': {'required': False, 'help_text': "Date de fin de la souscription (optionnelle, pour les plans à durée limitée)"},
            'is_active': {'required': False, 'default': True, 'help_text': "Indique si la souscription est active"}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['plan'].read_only = False

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        subscription = Subscription.objects.create(**validated_data)
        SubscriptionDetail.objects.bulk_create([
            SubscriptionDetail(subscription=subscription, **detail) for detail in details_data
        ])
        return subscription

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            instance.details.all().delete()
            SubscriptionDetail.objects.bulk_create([
                SubscriptionDetail(subscription=instance, **detail) for detail in details_data
            ])
        return instance


# -----------------------
# MySubscriptionSerializer — Vue complète récursive personnalisée
# -----------------------

class MySubscriptionSerializer(serializers.ModelSerializer):
    parent = serializers.HiddenField(default=serializers.CurrentUserDefault())
    plan = MyPlanSerializer(read_only=True)
    detail_objects = FullSubscriptionDetailSerializer(many=True, read_only=True, source='details')

    class Meta:
        model = Subscription
        fields = [
            'id', 'parent', 'plan', 'start_date', 'end_date',
            'price', 'is_active', 'created_at',
            'detail_objects'
        ]
        read_only_fields = ['id', 'created_at', 'detail_objects', 'plan', 'end_date', 'price']
