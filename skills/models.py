from django.db import models
from accounts.models import Profile

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Programming', 'Programming'),
        ('Web Development', 'Web Development'),
        ('Mobile Development', 'Mobile Development'),
        ('Data Science', 'Data Science'),
        ('Artificial Intelligence', 'Artificial Intelligence'),
        ('Design', 'Design'),
        ('Communication', 'Communication'),
        ('Languages', 'Languages'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class UserSkill(models.Model):
    SKILL_TYPE_CHOICES = [
        ('TEACH', 'Can Teach'),
        ('LEARN', 'Wants to Learn'),
    ]

    PROFICIENCY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_skills')
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPE_CHOICES)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='Intermediate')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'skill', 'skill_type')
        ordering = ['skill_type', 'skill__name']

    def __str__(self):
        return f"{self.profile.user.username} - {self.get_skill_type_display()}: {self.skill.name} ({self.proficiency_level})"
