from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from bibliotheque.models import Membre, Media, Emprunt
from django.urls import reverse


# Test de création d'un membre
class MembreTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.bibliothecaire = User.objects.create_user(username="biblio", password="biblio123")
        self.biblio_group = Group.objects.create(name="Bibliothécaire")
        self.bibliothecaire.groups.add(self.biblio_group)

        self.membre = Membre.objects.create(nom="Jean Dupont", email="jean@example.com", user=self.user)

    def test_membre_creation(self):
        membre = Membre.objects.get(nom="Jean Dupont")
        self.assertEqual(membre.email, "jean@example.com")


# Test d'accès à la liste des membres
class ListeMembresTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(username="biblio", password="biblio123")
        self.biblio_group = Group.objects.create(name="Bibliothécaire")
        self.bibliothecaire.groups.add(self.biblio_group)

    def test_acces_liste_membres_non_authentifie(self):
        response = self.client.get(reverse('liste_membres'))
        self.assertEqual(response.status_code, 302)  # 302 = Redirection vers la page de connexion

    def test_acces_liste_membres_bibliothecaire(self):
        self.client.login(username="biblio", password="biblio123")
        response = self.client.get(reverse('liste_membres'))
        self.assertEqual(response.status_code, 200)


# Test de mise à jour d'un membre
class MajMembreTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(username="biblio", password="biblio123")
        self.biblio_group = Group.objects.create(name="Bibliothécaire")
        self.bibliothecaire.groups.add(self.biblio_group)
        self.client.login(username="biblio", password="biblio123")

        self.user = User.objects.create_user(username="membretest", password="test123")
        self.membre = Membre.objects.create(nom="Membre Test", email="test@membre.com", user=self.user)

    def test_mise_a_jour_membre(self):
        response = self.client.post(reverse('maj_membre', args=[self.membre.id]), {
            'nom': 'Membre Test Mis à Jour',
            'email': 'test_update@membre.com',
        })

        self.assertEqual(response.status_code, 302)

        self.membre.refresh_from_db()
        self.assertEqual(self.membre.nom, 'Membre Test Mis à Jour')
        self.assertEqual(self.membre.email, 'test_update@membre.com')

    def test_mise_a_jour_membre_non_authentifie(self):
        self.client.logout()

        response = self.client.post(reverse('maj_membre', args=[self.membre.id]), {
            'nom': 'Membre Non Authentifié',
            'email': 'non_auth@membre.com',
        })

        self.assertEqual(response.status_code, 302)
        self.membre.refresh_from_db()
        self.assertEqual(self.membre.nom, 'Membre Test')


# Test suppression d'un membre
class SuppressionMembreTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(username="biblio", password="biblio123")
        self.biblio_group = Group.objects.create(name="Bibliothécaire")
        self.bibliothecaire.groups.add(self.biblio_group)
        self.client.login(username="biblio", password="biblio123")

        self.user = User.objects.create_user(username="membretest", password="test123")
        self.membre = Membre.objects.create(nom="Membre Test", email="test@membre.com", user=self.user)

    def test_suppression_membre(self):
        response = self.client.post(reverse('supprimer_membre', args=[self.membre.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Membre.objects.filter(id=self.membre.id).exists())


# Test ajouter un média
class AjouterMediaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(username="biblio", password="biblio123")
        self.biblio_group = Group.objects.create(name="Bibliothécaire")
        self.bibliothecaire.groups.add(self.biblio_group)
        self.client.login(username="biblio", password="biblio123")

    def test_ajouter_media(self):
        response = self.client.post(reverse('ajouter_media'), {
            'titre': 'Test Média',
            'auteur': 'Auteur Test',
            'type': 'livre',
            'disponible': True,
        })

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Media.objects.filter(titre='Test Média').exists())
        media = Media.objects.get(titre='Test Média')
        self.assertEqual(media.auteur, 'Auteur Test')
        self.assertTrue(media.disponible)

    def test_ajouter_media_non_authentifie(self):
        self.client.logout()  # Déconnexion de l'utilisateur

        response = self.client.post(reverse('ajouter_media'), {
            'titre': 'Média Non Authentifié',
            'auteur': 'Auteur Test',
            'type': 'livre',
            'disponible': True,
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Media.objects.filter(titre='Média Non Authentifié').exists())


# Test emprunt d'un média
class EmpruntTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(username="biblio", password="biblio123")
        self.biblio_group = Group.objects.create(name="Bibliothécaire")
        self.bibliothecaire.groups.add(self.biblio_group)
        self.client.login(username="biblio", password="biblio123")

        self.membre = Membre.objects.create(nom="Membre Test", email="membre@test.com", user=self.bibliothecaire)
        self.media = Media.objects.create(titre="Livre Test", type="Livre", auteur="Auteur Test", disponible=True)

    def test_emprunt_media(self):
        self.client.login(username="user1", password="password")

        response = self.client.post(reverse('emprunter_media', args=[self.media.id]), {'membre_id': self.membre.id})

        self.assertEqual(response.status_code, 302)
        self.media.refresh_from_db()
        self.assertFalse(self.media.disponible)

    def test_emprunt_media_non_authentifie(self):
        self.client.logout()

        response = self.client.post(reverse('emprunter_media', args=[self.media.id]), {'membre_id': self.membre.id})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.media.disponible)


# Test retour d'un média
class RendreMediaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(username="biblio", password="biblio123")
        self.biblio_group = Group.objects.create(name="Bibliothécaire")
        self.bibliothecaire.groups.add(self.biblio_group)
        self.client.login(username="biblio", password="biblio123")

        self.membre = Membre.objects.create(nom="Membre Test", email="membre@test.com", user=self.bibliothecaire)
        self.media = Media.objects.create(titre="Test Média", auteur="Auteur Test", type="livre", disponible=False)

        self.emprunt = Emprunt.objects.create(membre=self.membre, media=self.media)

    def test_rendre_media(self):
        response = self.client.post(reverse('rendre_media', args=[self.emprunt.id]))

        self.assertEqual(response.status_code, 302)

        self.media.refresh_from_db()
        self.assertTrue(self.media.disponible)

        self.emprunt.refresh_from_db()
        self.assertIsNotNone(self.emprunt.date_retour_effectif)

    def test_rendre_media_non_authentifie(self):
        self.client.logout()

        response = self.client.post(reverse('rendre_media', args=[self.emprunt.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.media.disponible)
