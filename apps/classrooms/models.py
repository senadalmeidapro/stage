from django.db import models
from apps.nurseries.models import Nursery

# Create your models here.
class Classroom(models.Model):
    """
    Représente une salle ou une classe dans une crèche :
    - name : nom de la classe
    - nursery : FK vers Nursery
    - capacity : capacité d'accueil
    - age_range_start, age_range_end : tranche d'âge (en mois) gérée
    - max_children : nombre max d'enfants
    - description : texte libre
    - created_at : timestamp de création
    """
    name = models.CharField(max_length=100, help_text="Nom de la salle/Classe")
    nursery = models.ForeignKey(
        Nursery,
        on_delete=models.CASCADE,
        related_name='classrooms',
        help_text="Crèche propriétaire de cette salle"
    )
    capacity = models.PositiveIntegerField(help_text="Capacité totale")
    age_range_start = models.PositiveIntegerField(help_text="Âge minimum (en mois)")
    age_range_end = models.PositiveIntegerField(help_text="Âge maximum (en mois)")
    nbr_children = models.PositiveIntegerField(help_text="Nombre d'enfants dans la salle", default=0)
    existe = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date de création")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date de mise à jour")

    class Meta:
        verbose_name = "Salle / Classe"
        verbose_name_plural = "Salles / Classes"
        ordering = ['name']
        unique_together = ('name', 'nursery')

    def __str__(self):
        return f"{self.name} ({self.nursery.name})"


class Group(models.Model):
    """
    Représente un groupe d'enfants dans une classe :
    - name : nom du groupe
    - classroom : FK vers Classroom
    - description, created_at, updated_at
    """
    name = models.CharField(max_length=100, help_text="Nom du groupe")
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='groups',
        help_text="Classe à laquelle appartient ce groupe"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date de création")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date de mise à jour")

    class Meta:
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        ordering = ['name']
        unique_together = ('name', 'classroom')

    def __str__(self):
        return f"{self.name} ({self.classroom.name})"