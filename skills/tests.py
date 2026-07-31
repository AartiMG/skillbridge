from django.test import TestCase
from django.contrib.auth.models import User
from skills.models import Skill, UserSkill

class SkillsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='skilluser', password='password123')
        self.skill = Skill.objects.create(
            name='Python Basics',
            category='Programming',
            description='Fundamentals of Python syntax'
        )

    def test_skill_creation(self):
        self.assertEqual(self.skill.name, 'Python Basics')
        self.assertEqual(self.skill.category, 'Programming')

    def test_user_skill_assignment(self):
        user_skill = UserSkill.objects.create(
            profile=self.user.profile,
            skill=self.skill,
            skill_type='TEACH',
            proficiency_level='Advanced'
        )
        self.assertEqual(user_skill.profile.user.username, 'skilluser')
        self.assertEqual(user_skill.skill_type, 'TEACH')
        self.assertIn(user_skill, self.user.profile.get_skills_teach())
