from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from .models import Membre, Media, Emprunt
from .forms import EmpruntForm


# Accueil
def accueil(request):
    medias = Media.objects.all()
    return render(request, 'liste_medias.html', {'medias': medias})


# Bibliothécaires
def is_bibliothecaire(user):
    return user.is_authenticated and user.groups.filter(name="Bibliothécaire").exists()


# Liste des membres
@user_passes_test(is_bibliothecaire)
def liste_membres(request):
    membres = Membre.objects.all()
    return render(request, 'liste_membres.html', {'membres': membres})


# Ajouter un membre
@user_passes_test(is_bibliothecaire)
def ajouter_membre(request):
    if request.method == "POST":
        nom = request.POST['nom']
        email = request.POST['email']
        username = nom
        user = User.objects.create(username=username, email=email)

        # Bibliothécaire ou pas
        if 'bibliothecaire' in request.POST:
            mot_de_passe = request.POST['mot_de_passe']
            user.set_password(mot_de_passe)
            bibliothecaire_group = Group.objects.get(name="Bibliothécaire")
            user.groups.add(bibliothecaire_group)

        Membre.objects.create(nom=nom, email=email, user=user)

        return redirect('liste_membres')
    return render(request, 'ajouter_membre.html')


# Mettre à jour un membre
@user_passes_test(is_bibliothecaire)
def maj_membre(request, id):
    membre = get_object_or_404(Membre, id=id)

    if request.method == "POST":
        membre.nom = request.POST['nom']
        membre.email = request.POST['email']
        membre.save()
        return redirect('liste_membres')

    return render(request, 'maj_membre.html', {'membre': membre})


# Supprimer membre
@user_passes_test(is_bibliothecaire)
def supprimer_membre(request, id):
    membre = get_object_or_404(Membre, id=id)

    if membre.user:
        membre.user.delete()
    membre.delete()

    return redirect('liste_membres')


# Liste des médias
def liste_medias(request):
    medias = Media.objects.all()
    emprunts_actifs = {emprunt.media.id: emprunt for emprunt in Emprunt.objects.filter(date_retour_effectif__isnull=True).select_related("media")}
    return render(request, 'liste_medias.html', {'medias': medias, 'emprunts_actifs': emprunts_actifs})


# Ajouter un média
@user_passes_test(is_bibliothecaire)
def ajouter_media(request):
    if request.method == 'POST':
        type_media = request.POST['type']
        titre = request.POST['titre']
        auteur = request.POST['auteur']
        Media.objects.create(type=type_media, titre=titre, auteur=auteur)
        return redirect('liste_medias')

    return render(request, 'ajouter_media.html')


# Emprunter un média
@user_passes_test(is_bibliothecaire)
def emprunter_media(request, media_id):
    media = get_object_or_404(Media, id=media_id)


    if request.method == 'POST':
        form = EmpruntForm(request.POST)

        if form.is_valid():
            membre_id = form.cleaned_data['membre_id']
            membre = get_object_or_404(Membre, id=membre_id)

            # Vérification de la possibilité d'emprunt
            if media.type == 'jeu':
                messages.error(request, "Les jeux de plateau ne peuvent pas être empruntés.")
                return redirect('liste_medias')
            if membre.bloque:
                messages.error(request, f"{membre.nom} ne peut pas emprunter plus de 3 médias.")
                return redirect('liste_medias')

            try:
                with transaction.atomic():
                    emprunt = Emprunt(membre=membre, media=media)
                    emprunt.save()

                    media.disponible = False
                    media.save()

                    messages.success(request, f"Le média '{media.titre}' a été emprunté par {membre.nom}.")
                    return redirect('liste_medias')

            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('liste_medias')

    else:
        form = EmpruntForm()

    return render(request, 'emprunter_media.html', {'media': media, 'form': form})


# Rendre un emprunt
@user_passes_test(is_bibliothecaire)
def rendre_media(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, id=emprunt_id)

    emprunt.retour()

    # Message de succès
    messages.success(request, f"Le média '{emprunt.media.titre}' a bien été retourné par {emprunt.membre.nom}.")
    return redirect('liste_medias')