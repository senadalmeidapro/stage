from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserType, NurseryAssistant
from django.contrib.auth.models import User


# @receiver(post_save, sender=UserCommandHistory)
# def handle_command_post_save(sender, instance, created, **kwargs):
 
@receiver(post_save, sender=User)
def create_user_type(sender, instance, created, **kwargs):
    if created:
        UserType.objects.create(user=instance)