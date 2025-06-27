from django.db import models
from apps.nurseries.models import Nursery
from apps.classrooms.models import Classroom

# Create your models here.
class Activity(models.Model):
    """
    Représente une activité dans une crèche :
    - name, description
    - nursery : FK vers Nursery
    - type : educational, recreational, cultural, other
    - created_at : timestamp d'ajout
    """
    TYPE_CHOICES = [
        ('educational', 'Educationnele'),
        ('recreational', 'Récréationnele'),
        ('cultural', 'Culturel'),
        ('other', 'Autre'),
    ]
    name = models.CharField(max_length=100, help_text="Nom de l'activité")
    description = models.TextField(blank=True, null=True, help_text="Description détaillée")
    nursery = models.ForeignKey(
        Nursery,
        on_delete=models.CASCADE,
        related_name='activities',
        help_text="Crèche qui propose cette activité"
    )
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, help_text="Catégorie de l'activité")
    valide = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date de création")

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} @{self.nursery.name} le {self.created_at.date()}"

class ClassroomActivity(models.Model):
    """
    Association entre une classe (Classroom) et une activité (Activity) :
    - classroom : FK vers Classroom
    - activity : FK vers Activity
    - start_time, end_time : horaires respectifs pour cette classe
    """
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='classroom_activities',
        help_text="Classe réalisant cette activité"
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='classroom_links',
        help_text="Activité planifiée"
    )
    active = models.BooleanField(default=True)
    date = models.DateField(help_text="Date de l'activité pour cette classe")
    start_time = models.TimeField(help_text="Heure de début pour la classe")
    end_time = models.TimeField(help_text="Heure de fin pour la classe")

    class Meta:
        unique_together = ('classroom', 'activity')
        ordering = ['start_time']
        verbose_name = "Activité de classe"
        verbose_name_plural = "Activités de classe"

    def __str__(self):
        return (
            f"{self.classroom.name} → {self.activity.name} "
            f"({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
        )
