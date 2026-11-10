"""
Tests for Authentication & Access Control (AUTH-01 to AUTH-05).
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile, UserRole


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="staff1",
            password="password123",
            email="staff1@example.com"
        )

    def test_auth01_login_required_for_protected_pages(self):
        """AUTH-01: Anonymous users cannot access dashboard or orders without login."""
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_auth02_user_profile_creation_on_user_created(self):
        """AUTH-02: Profile created with appropriate role."""
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertEqual(self.user.profile.role, UserRole.WAREHOUSE_STAFF)

    def test_auth03_authenticated_user_can_access_dashboard(self):
        """AUTH-03: Authenticated user can access protected dashboard."""
        self.client.login(username="staff1", password="password123")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)

    def test_auth04_user_can_logout(self):
        """AUTH-04: User can securely log out."""
        self.client.login(username="staff1", password="password123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        # Attempt to access dashboard again
        dash_res = self.client.get(reverse("dashboard:index"))
        self.assertEqual(dash_res.status_code, 302)

    def test_auth05_inactive_user_cannot_login(self):
        """AUTH-05: Inactive user cannot log in."""
        self.user.is_active = False
        self.user.save()
        logged_in = self.client.login(username="staff1", password="password123")
        self.assertFalse(logged_in)
