from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from skills.models import Skill

class SkillExchangeRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_exchange_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_exchange_requests')
    skill_offered = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='offered_in_exchanges')
    skill_requested = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='requested_in_exchanges')
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Exchange Request #{self.id}: {self.sender.username} -> {self.receiver.username} ({self.status})"

    def get_partner(self, user):
        return self.receiver if self.sender == user else self.sender

    def can_leave_feedback(self, user):
        """Check if user can leave feedback for this completed exchange."""
        if self.status != 'Completed':
            return False
        if user not in [self.sender, self.receiver]:
            return False
        # Check if already left feedback
        return not self.feedbacks.filter(reviewer=user).exists()


class Feedback(models.Model):
    exchange_request = models.ForeignKey(SkillExchangeRequest, on_delete=models.CASCADE, related_name='feedbacks')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks_given')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (poor) to 5 (excellent)"
    )
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exchange_request', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback by {self.reviewer.username} for Request #{self.exchange_request.id} - {self.rating}/5"
