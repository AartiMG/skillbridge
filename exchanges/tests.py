from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from skills.models import Skill, UserSkill
from exchanges.models import SkillExchangeRequest, Feedback

class ExchangesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        
        self.python_skill = Skill.objects.create(name='Python', category='Programming')
        self.figma_skill = Skill.objects.create(name='Figma', category='Design')

        UserSkill.objects.create(profile=self.user1.profile, skill=self.python_skill, skill_type='TEACH')
        UserSkill.objects.create(profile=self.user2.profile, skill=self.figma_skill, skill_type='TEACH')

    def test_prevent_self_exchange_request(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('send_request', kwargs={'receiver_username': 'user1'}))
        self.assertEqual(response.status_code, 302) # Redirects to dashboard with error flash

    def test_exchange_request_lifecycle(self):
        # 1. User1 sends request to User2
        exchange_req = SkillExchangeRequest.objects.create(
            sender=self.user1,
            receiver=self.user2,
            skill_offered=self.python_skill,
            skill_requested=self.figma_skill,
            message='Let us exchange skills!'
        )
        self.assertEqual(exchange_req.status, 'Pending')

        # 2. User2 accepts request
        self.client.login(username='user2', password='password123')
        response = self.client.get(reverse('respond_request', kwargs={'request_id': exchange_req.id, 'action': 'accept'}))
        exchange_req.refresh_from_db()
        self.assertEqual(exchange_req.status, 'Accepted')

        # 3. Complete exchange
        response = self.client.get(reverse('respond_request', kwargs={'request_id': exchange_req.id, 'action': 'complete'}))
        exchange_req.refresh_from_db()
        self.assertEqual(exchange_req.status, 'Completed')

        # 4. User2 submits feedback
        feedback = Feedback.objects.create(
            exchange_request=exchange_req,
            reviewer=self.user2,
            rating=5,
            comment='Great experience!'
        )
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(self.user1.profile.average_rating(), 5.0)
