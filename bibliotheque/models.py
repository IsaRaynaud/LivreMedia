from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Media(models.Model):
    LIVRE = 'livre'
    DVD = 'dvd'
    CD = 'cd'
    JEU = 'jeu de plateau'

    MEDIA_CHOICES = [
        (LIVRE, 'Livre'),
        (DVD, 'DVD'),
        (CD, 'CD'),
        (JEU, 'Jeu de plateau'),
    ]

    titre = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=MEDIA_CHOICES, default=LIVRE)
    auteur = models.CharField(max_length=250, null=True, blank=True)
    disponible = models.BooleanField(default=True)

    def emprunte_par(self):
        emprunt_actif = self.emprunt_set.filter(date_retour__isnull=True).first()
        return emprunt_actif.membre if emprunt_actif else None

    def __str__(self):
        return f"{self.titre} ({self.type})"


# Classe Membre (anciennement Emprunteur)
class Membre(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True)
    bloque = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def emprunts_actifs(self):
        return Emprunt.objects.filter(membre=self, date_retour__isnull=True).count()

    def bloquer(self):
        self.bloque = True
        self.save()

    def debloquer(self):
        self.bloque = False
        self.save()

    def __str__(self):
        return self.user.username


# Classe Emprunt
class Emprunt(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name="emprunts")
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    date_emprunt = models.DateField(auto_now_add=True)
    date_retour = models.DateField(null=True, blank=True)
    date_retour_effectif = models.DateField(null=True, blank=True)

    def clean(self):
        # Vérification si le média est déjà emprunté
        if Emprunt.objects.filter(media=self.media, date_retour__isnull=True).exists():
            raise ValidationError(f" {self.media.titre} est déjà emprunté.")

        # Nombre d'emprunts du membre déjà en cours
        if Emprunt.objects.filter(membre=self.membre, date_retour_effectif__isnull=True).count() >= 3:
            raise ValidationError(f" {self.membre.nom} ne peut pas emprunter plus de 3 documents.")

        # Jeu de plateau ou pas
        if self.media.type == 'jeu de plateau':
            raise ValidationError("Les jeux de plateau ne peuvent pas être empruntés.")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()

        # Calcul de la date de retour
        if not self.date_retour:
            self.date_retour = timezone.now().date() + timedelta(days=7)

        # Mise à jour de la disponibilité du média
        self.media.disponible = False
        self.media.save()

        super().save(*args, **kwargs)

    # Rendre un emprunt
    def retour(self):
        if not self.date_retour_effectif:
            self.date_retour_effectif = timezone.now().date()
            self.save()
            self.media.disponible = True
            self.media.save()

    def __str__(self):
        return f"{self.membre.nom} -> {self.media.titre}"