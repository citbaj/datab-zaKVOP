from django.contrib.auth.models import User
from django.test import TestCase


class AuthTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_login_page_accessible(self):
        """Prihlasovacia stránka je prístupná bez autentifikácie."""
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "username")

    def test_wizard_redirects_anonymous(self):
        """/wizard/ presmeruje neprihlásených na login."""
        response = self.client.get("/wizard/")
        self.assertRedirects(response, "/login/?next=/wizard/", fetch_redirect_response=False)

    def test_search_redirects_anonymous(self):
        """/search/ presmeruje neprihlásených na login."""
        response = self.client.get("/search/")
        self.assertRedirects(response, "/login/?next=/search/", fetch_redirect_response=False)

    def test_login_correct_credentials(self):
        """Správne prihlásenie presmeruje na wizard."""
        response = self.client.post("/login/", {"username": "testuser", "password": "testpass123"})
        self.assertRedirects(response, "/wizard/", fetch_redirect_response=False)

    def test_login_wrong_credentials(self):
        """Nesprávne heslo zobrazí chybu na login stránke."""
        response = self.client.post("/login/", {"username": "testuser", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nesprávne meno alebo heslo")

    def test_wizard_accessible_after_login(self):
        """Prihlásený užívateľ má prístup na /wizard/."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/wizard/")
        self.assertEqual(response.status_code, 200)

    def test_search_accessible_after_login(self):
        """Prihlásený užívateľ má prístup na /search/."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """Odhlásenie presmeruje na login stránku."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post("/logout/")
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)

    def test_wizard_inaccessible_after_logout(self):
        """Po odhlásení je /wizard/ opäť chránený."""
        self.client.login(username="testuser", password="testpass123")
        self.client.post("/logout/")
        response = self.client.get("/wizard/")
        self.assertRedirects(response, "/login/?next=/wizard/", fetch_redirect_response=False)
