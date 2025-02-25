from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Membre

@receiver(post_save, sender=User)
def creer_membre(sender, instance, created, **kwargs):
    """Créer un Membre automatiquement quand un User est créé."""
    if created:
        Membre.objects.create(user=instance)

@receiver(post_save, sender=User)
def sauvegarder_membre(sender, instance, **kwargs):
    """Sauvegarder Membre quand User est modifié."""
    instance.membre.save()