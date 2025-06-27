from django.db import models
from apps.users.models import UserType
from django.utils import timezone

# Create your models here.
class Child(models.Model):
    """
    Représente un enfant :
    - parent : FK vers UserType (reste le parent)
    - last_name, first_name, birthday : identité de l'enfant
    - subscription : FK vers Subscription (0 ou 1 abonnement actif)
    - register_date : date d'enregistrement
    """
    parent = models.ForeignKey(
        UserType,
        on_delete=models.CASCADE,
        related_name='children',
        limit_choices_to={'type': 'parent'},
        help_text="Utilisateur (type parent) responsable de cet enfant"
    )
    last_name = models.CharField(max_length=100, help_text="Nom de famille")
    first_name = models.CharField(max_length=100, help_text="Prénom")
    birthday = models.DateField(blank=True, null=True, help_text="Date de naissance")
    joined_date = models.DateTimeField(auto_now_add=True, help_text="Date d'enregistrement")
    detail = models.TextField(max_length=500, blank=True,
        null=True,)
    existe = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Enfant"
        verbose_name_plural = "Enfants"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        parent_username = self.parent.user.username if self.parent else "inconnu"
        return f"{self.first_name} {self.last_name} (parent : {parent_username})"
