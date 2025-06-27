from django.db import models
from apps.nurseries.models import Nursery

class Plan(models.Model):
    DURATION_CHOICES = [
        ('none', ''),
        ('day', 'Journalier'),
        ('week', 'Hebdomadaire'),
        ('month', 'Mensuel'),
        ('quarter', 'Trimestriel'),
        ('semester', 'Semestriel'),
        ('year', 'Annuel'),
    ]

    name = models.CharField(max_length=100)
    nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE, related_name='plans')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='none')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan d'abonnement"
        verbose_name_plural = "Plans d'abonnement"
        ordering = ['nursery', 'duration']

    def __str__(self):
        return f"{self.name} ({self.get_duration_display()})"


class Subscription(models.Model):
    parent = models.ForeignKey(
        'users.UserType',
        limit_choices_to={'type': 'parent'},
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField(
        help_text="Date de début de la souscription (obligatoire pour tous les plans)",
    )
    end_date = models.DateField(
        null=True, blank=True, help_text="Date de fin de la souscription (optionnelle, pour les plans à durée limitée)"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                help_text="Prix de la souscription (sera calculé automatiquement en fonction du plan)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Souscription"
        verbose_name_plural = "Souscriptions"
        ordering = ['-start_date']

    def __str__(self):
        return f"Souscription #{self.id} - {self.plan.name} ({self.parent})"


class SubscriptionDetail(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='details'
    )
    child = models.ForeignKey(
        'children.Child',
        on_delete=models.CASCADE,
        related_name='subscription_details_for_child'
    )
    classroom = models.ForeignKey(
        'classrooms.Classroom',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscription_details_for_classroom'
    )
    group = models.ForeignKey(
        'classrooms.Group',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscription_details_for_group'
    )
    is_valide = models.BooleanField(default=True, help_text="Indique si le détail de souscription est valide")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Détail de souscription"
        verbose_name_plural = "Détails de souscription"
        unique_together = ('subscription', 'child')
        ordering = ['child__last_name']

    def __str__(self):
        return f"{self.child} dans {self.classroom} ({self.group})"
