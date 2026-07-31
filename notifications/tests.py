from django.test import TestCase, Client
from django.contrib.auth.models import User
from notifications.models import Notification, create_notification

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
        self.client = Client()

    def test_create_notification_helper(self):
        n = create_notification(
            recipient=self.user1,
            actor=self.user2,
            verb="sent you a request",
            target_url="/exchanges/requests/"
        )
        self.assertIsNotNone(n)
        self.assertEqual(self.user1.notifications.count(), 1)
        self.assertFalse(n.is_read)

    def test_notification_self_prevention(self):
        # Should return None if recipient == actor
        n = create_notification(recipient=self.user1, actor=self.user1, verb="self action")
        self.assertIsNone(n)
        self.assertEqual(self.user1.notifications.count(), 0)

    def test_notifications_list_and_read_views(self):
        create_notification(recipient=self.user1, actor=self.user2, verb="sent you a request")
        self.client.login(username='testuser1', password='password123')
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sent you a request")
