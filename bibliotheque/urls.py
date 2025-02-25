from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('membres/', views.liste_membres, name='liste_membres'),
    path('membres/ajouter/', views.ajouter_membre, name='ajouter_membre'),
    path('membres/mettreajour/<int:id>/', views.maj_membre, name='maj_membre'),
    path('membres/supprimer/<int:id>/', views.supprimer_membre, name='supprimer_membre'),
    path('medias/', views.liste_medias, name='liste_medias'),
    path('medias/emprunter/<int:media_id>/', views.emprunter_media, name='emprunter_media'),
    path('medias/retourner/<int:emprunt_id>/', views.rendre_media, name='rendre_media'),
    path('medias/ajouter/', views.ajouter_media, name='ajouter_media'),
]