from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile

class AccountsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teststudent',
            email='test@student.com',
            password='password123',
            first_name='Test',
            last_name='Student'
        )

    def test_profile_auto_creation_signal(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user, self.user)
        self.assertEqual(self.user.profile.preferred_learning_mode, 'Online')

    def test_user_registration_view(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'email': 'newuser@student.com',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard upon success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_and_dashboard_access(self):
        login_success = self.client.login(username='teststudent', password='password123')
        self.assertTrue(login_success)

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back, Test!')

    def test_protected_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_profile_completion_percentage(self):
        profile = self.user.profile
        self.assertEqual(profile.completion_percentage(), 20)  # Base registration
        profile.bio = "This is a detailed bio about my skills and passions."
        profile.college_or_organization = "Stanford"
        profile.city = "San Francisco"
        profile.save()
        self.assertEqual(profile.completion_percentage(), 80)

    def test_explore_sorting_and_pagination(self):
        response = self.client.get(reverse('explore') + '?sort=alphabetical')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'teststudent')

