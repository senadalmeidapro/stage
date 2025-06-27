import os
import uuid
from django.db import models

def nursery_upload_path(instance, filename, subfolder):
    """
    Génère le chemin d'upload du fichier dans un dossier unique par crèche.
    Format : nurseries/{uuid}/{subfolder}/{filename}
    """
    # Sécurité : fallback si upload_folder n'est pas encore défini
    folder = getattr(instance, 'upload_folder', 'unknown')
    return os.path.join(f"nurseries/{folder}/{subfolder}", filename)

def doc_upload_path(instance, filename):
    return nursery_upload_path(instance, filename, 'doc')

def images_upload_path(instance, filename):
    return nursery_upload_path(instance, filename, 'images')


class Nursery(models.Model):
    LEGAL_STATUS_CHOICES = [
        ('agrée', 'Agrée par le ministère'),
        ('en_cours', 'En cours d’agrément'),
        ('communautaire', 'Structure communautaire'),
        ('autre', 'Autre'),
    ]

    # UUID unique et immuable, utilisé comme nom de dossier pour les fichiers médias
    upload_folder = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Dossier média unique attribué à chaque crèche"
    )

    manager = models.OneToOneField(
        "users.UserType",
        on_delete=models.CASCADE,
        help_text="Manager (UserType avec le rôle 'nursery_manager')",
    )
    name = models.CharField(max_length=255, help_text="Nom de la crèche")
    address = models.TextField(help_text="Adresse de la crèche")
    contact_number = models.CharField(max_length=15, help_text="Téléphone de la crèche")
    information = models.TextField(help_text="Informations complémentaires")
    max_age = models.PositiveIntegerField(help_text="Âge maximum des enfants acceptés (en mois)")
    max_children_per_class = models.PositiveIntegerField(help_text="Nombre maximum d'enfants par classe")

    legal_status = models.CharField(
        max_length=20,
        choices=LEGAL_STATUS_CHOICES,
        default='en_cours',
        help_text="Statut légal de la structure",
    )

    agreement_document = models.FileField(
        upload_to=doc_upload_path,
        help_text="Document d’agrément (PDF, image)",
        null=True,
        blank=True,
    )

    id_card_document = models.FileField(
        upload_to=doc_upload_path,
        help_text="Pièce d’identité du responsable",
        null=True,
        blank=True,
    )

    photo_exterior = models.ImageField(
        upload_to=images_upload_path,
        help_text="Photo extérieure de la crèche",
        null=True,
        blank=True,
    )
    photo_interior = models.ImageField(
        upload_to=images_upload_path,
        help_text="Photo intérieure de la crèche",
        null=True,
        blank=True,
    )

    verified = models.BooleanField(
        default=False,
        help_text="Indique si la crèche est certifiée par la plateforme",
    )

    online = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date de création")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date de dernière mise à jour")

    class Meta:
        verbose_name = "Crèche"
        verbose_name_plural = "Crèches"
        ordering = ["name"]

    def __str__(self):
        return self.name



class OpeningHour(models.Model):
    DAYS_OF_WEEK = [
        (0, "Lundi"),
        (1, "Mardi"),
        (2, "Mercredi"),
        (3, "Jeudi"),
        (4, "Vendredi"),
        (5, "Samedi"),
        (6, "Dimanche"),
    ]
    nursery = models.ForeignKey(
        "nurseries.Nursery",
        on_delete=models.CASCADE,
        related_name="opening_hours",
        help_text="Crèche liée à cet horaire",
    )
    day = models.IntegerField(choices=DAYS_OF_WEEK, help_text="Jour de la semaine (0=Lundi, …, 6=Dimanche)")
    open_time = models.TimeField(help_text="Heure d'ouverture (HH:MM)", null=True, blank=True)
    close_time = models.TimeField(help_text="Heure de fermeture (HH:MM)", null=True, blank=True)
    is_closed = models.BooleanField(default=False, help_text="Si vrai, la crèche est fermée ce jour")

    class Meta:
        unique_together = ("nursery", "day")
        ordering = ["day"]
        verbose_name = "Horaire d'ouverture"
        verbose_name_plural = "Horaires d'ouverture"

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_display()} : Fermé"
        return f"{self.get_day_display()} : {self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)



class NurseryAssistant(models.Model):
    """
    Spécialisation de UserType pour un assistant de crèche :
    - profil : FK vers UserType
    - nursery : FK vers Nursery
    - classroom, group : FKs optionnels vers Classroom et Group
    - hired_date : date d'embauche
    - is_manager : indique un manager temporaire
    """

    profil = models.ForeignKey(
        "users.UserType",
        on_delete=models.CASCADE,
        limit_choices_to={"type": "nursery_assistant"},
        help_text="Profil UserType de l'assistant",
    )
    nursery = models.ForeignKey(
        "nurseries.Nursery",
        on_delete=models.CASCADE,
        related_name="assistants",
        help_text="Crèche dans laquelle l'assistant travaille",
    )
    classroom = models.ForeignKey(
        "classrooms.Classroom",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assistants",
        help_text="Classe dans laquelle l'assistant est assigné",
    )
    group = models.ForeignKey(
        "classrooms.Group",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assistants",
        help_text="Groupe d'enfants pris en charge",
    )
    # hired_date = models.DateField(help_text="Date d'embauche")
    is_manager = models.BooleanField(
        default=False, help_text="Rôle de manager temporaire ?"
    )
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("profil", "nursery")
        verbose_name = "Assistant de crèche"
        verbose_name_plural = "Assistants de crèche"

    def __str__(self):
        # On suppose que UserType a un champ `user` lié à l’utilisateur authentifié
        return f"{self.profil.user.username} (Assistant – {self.nursery.name})"
