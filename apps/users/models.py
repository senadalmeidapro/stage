from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from apps.nurseries.models import NurseryAssistant

# Create your models here.
class UserType(models.Model):
    """
    Extension du modèle User : 
    - contact : numéro de téléphone
    - address : adresse complète
    - birthday : date de naissance
    - type : rôle (parent, assistant, manager, admin)
    - is_active : activation/désactivation métier
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    TYPE_CHOICES = [
        ('parent', 'Parent'),
        ('nursery_assistant', 'Nursery Assistant'),
        ('nursery_manager', 'Nursery Manager'),
        ('admin', 'Admin'),
    ]
    contact = models.CharField(max_length=15, blank=True, null=True, help_text="Numéro de téléphone")
    address = models.TextField(blank=True, null=True, help_text="Adresse postale")
    birthday = models.DateField(blank=True, null=True, help_text="Date de naissance")
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='parent',
        help_text="Rôle de l'utilisateur (parent, assistant, manager, admin)"
    )

    class Meta:
        verbose_name = "Utilisateur étendu"
        verbose_name_plural = "Utilisateurs étendus"

    def __str__(self):
        return f"{self.user.username} ({self.get_type_display()})"
    

    _bypass_check = False  # Champ non enregistré pour contourner temporairement la règle
    def save(self, *args, **kwargs):
        if self.type == 'nursery_assistant' and not hasattr(self, 'nurseryassistant'):
            if not getattr(self, '_bypass_check', False):
                raise ValueError("Les utilisateurs de type 'nursery_assistant' doivent être créés via le modèle NurseryAssistant.")
        super().save(*args, **kwargs)

