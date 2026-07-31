from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

class Profile(models.Model):
    LEARNING_MODE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
        ('Both', 'Both'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    college_or_organization = models.CharField(max_length=200, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    preferred_learning_mode = models.CharField(max_length=20, choices=LEARNING_MODE_CHOICES, default='Online')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_full_name_or_username(self):
        full = f"{self.user.first_name} {self.user.last_name}".strip()
        return full if full else self.user.username

    def average_rating(self):
        # Calculate average rating received from all completed exchanges where user was a participant
        from exchanges.models import Feedback
        feedbacks = Feedback.objects.filter(exchange_request__in=self.user.sent_exchange_requests.filter(status='Completed') | self.user.received_exchange_requests.filter(status='Completed')).exclude(reviewer=self.user)
        avg = feedbacks.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

    def rating_count(self):
        from exchanges.models import Feedback
        return Feedback.objects.filter(exchange_request__in=self.user.sent_exchange_requests.filter(status='Completed') | self.user.received_exchange_requests.filter(status='Completed')).exclude(reviewer=self.user).count()

    def get_skills_teach(self):
        return self.user_skills.filter(skill_type='TEACH')

    def get_skills_learn(self):
        return self.user_skills.filter(skill_type='LEARN')

    def total_skills_count(self):
        return self.user_skills.count()

    def completion_percentage(self):
        score = 20  # Base profile creation
        if self.bio and len(self.bio.strip()) > 5:
            score += 20
        if self.college_or_organization and self.college_or_organization.strip():
            score += 20
        if self.city and self.city.strip():
            score += 20
        if self.user_skills.exists():
            score += 20
        return min(score, 100)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
